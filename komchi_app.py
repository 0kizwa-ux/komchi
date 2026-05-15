#!/usr/bin/env python3
"""Local dashboard for the Komchi creator tools.

The app runs only on localhost. It provides simple browser forms for creating
short-video stock packages and links to the existing ROOM draft assistant.
"""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs
import html
import socket
import subprocess
import sys
import webbrowser

HOST = "127.0.0.1"
DEFAULT_PORT = 8787


DASHBOARD_HTML = r"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Komchi Creator App</title>
  <style>
    :root { --accent:#bf0000; --bg:#fff7f4; --card:#fff; --line:#ead8d4; --text:#222; --muted:#666; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:linear-gradient(135deg,#fff7f4,#fff); color:var(--text); }
    main { width:min(1040px, calc(100% - 32px)); margin:0 auto; padding:32px 0 56px; }
    .hero, .card { background:var(--card); border:1px solid var(--line); border-radius:24px; box-shadow:0 18px 48px rgba(191,0,0,.09); padding:28px; }
    .hero { text-align:center; margin-bottom:18px; }
    h1 { margin:0 0 8px; font-size:clamp(28px,5vw,44px); }
    h2 { margin:0 0 12px; }
    p { color:var(--muted); line-height:1.8; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; }
    label { display:block; margin:12px 0 6px; font-weight:700; }
    input, select { width:100%; border:2px solid var(--line); border-radius:14px; padding:13px 14px; font-size:16px; }
    button, .button { display:inline-block; border:0; border-radius:14px; background:var(--accent); color:#fff; cursor:pointer; font-weight:800; padding:13px 18px; margin-top:14px; text-decoration:none; }
    .button.secondary, button.secondary { background:#333; }
    .result { background:#f7fff9; border-color:#b7e4c7; }
    code { background:#fff0eb; padding:2px 6px; border-radius:8px; }
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>Komchi Creator App</h1>
    <p>楽天ROOM下書き、ショート動画ストック、写真1枚ダンス風ショートをブラウザから起動できます。</p>
    <a class="button" href="/room_draft_button.html" target="_blank" rel="noopener">ROOM下書きUIを開く</a>
  </section>
  {message}
  <section class="grid">
    <form class="card" method="post" action="/create-short">
      <h2>ショート動画ストック作成</h2>
      <p>台本・タイトル・説明文・メタデータをストックします。ffmpegがあればMP4も作成します。</p>
      <label>テーマ</label>
      <input name="theme" value="ベイビーダンス" required>
      <label>テンプレート</label>
      <select name="template">
        <option value="baby_dance">ベイビーダンス</option>
        <option value="simple">通常ショート</option>
      </select>
      <label>保存先</label>
      <input name="output_dir" value="C:\Users\osk_k\Desktop\ユーチューブショート動画ストック">
      <button type="submit">ストック作成</button>
    </form>
    <form class="card" method="post" action="/create-reference-project">
      <h2>参考動画テンプレート作成</h2>
      <p>参考動画URLを貼り付け、人物・BGM・背景などを差し替える編集プロジェクトを作ります。</p>
      <label>参考動画URL</label>
      <input name="reference_url" placeholder="https://www.tiktok.com/@.../video/..." required>
      <label>テーマ</label>
      <input name="theme" value="参考動画テンプレート" required>
      <label>特徴メモ</label>
      <input name="notes" placeholder="例: ベイビーダンス、白字幕、明るいBGM">
      <label>入れ替え指定</label>
      <input name="replace" placeholder="例: 人物A=C:\Users\osk_k\Desktop\portrait.jpg">
      <label>保存先</label>
      <input name="output_dir" value="C:\Users\osk_k\Desktop\ユーチューブショート動画ストック">
      <button type="submit">編集プロジェクト作成</button>
    </form>
    <form class="card" method="post" action="/create-photo-dance">
      <h2>写真1枚ダンス風ショート</h2>
      <p>肖像画像1枚に上下バウンス・ズーム・左右スウェイを付けた動画ストックを作ります。</p>
      <label>画像パス</label>
      <input name="image" placeholder="C:\Users\osk_k\Desktop\portrait.jpg" required>
      <label>テーマ</label>
      <input name="theme" value="写真ダンス" required>
      <label>BGMファイルパス（任意）</label>
      <input name="bgm" placeholder="C:\Users\osk_k\Desktop\music.mp3">
      <label>BGM音量</label>
      <input name="bgm_volume" value="0.8">
      <label>保存先</label>
      <input name="output_dir" value="C:\Users\osk_k\Desktop\ユーチューブショート動画ストック">
      <button type="submit">写真ダンス作成</button>
    </form>
  </section>
</main>
</body>
</html>
"""


class KomchiHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        self.root = Path(directory or Path.cwd())
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:  # noqa: N802 - inherited API name.
        if self.path in ("/", "/index.html"):
            self.render_dashboard()
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 - inherited API name.
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        values = {key: vals[0] for key, vals in parse_qs(body).items()}
        if self.path == "/create-short":
            message = self.create_short(values)
        elif self.path == "/create-photo-dance":
            message = self.create_photo_dance(values)
        elif self.path == "/create-reference-project":
            message = self.create_reference_project(values)
        else:
            self.send_error(404)
            return
        self.render_dashboard(message)

    def render_dashboard(self, message: str = "") -> None:
        html_body = DASHBOARD_HTML.replace("{message}", message)
        payload = html_body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def create_short(self, values: dict[str, str]) -> str:
        theme = values.get("theme", "ショート動画")
        template = values.get("template", "simple")
        output_dir = values.get("output_dir") or str(self.root / "youtube_shorts_stock")
        bgm = values.get("bgm", "").strip()
        bgm_volume = values.get("bgm_volume", "0.8").strip() or "0.8"
        cmd = [
            sys.executable,
            str(self.root / "shorts" / "create_stock_short.py"),
            "--theme",
            theme,
            "--template",
            template,
            "--output-dir",
            output_dir,
        ]
        return self.run_command(cmd, "ショート動画ストックを作成しました")

    def create_photo_dance(self, values: dict[str, str]) -> str:
        image = values.get("image", "")
        if not image:
            return result_box("画像パスを入力してください。", error=True)
        theme = values.get("theme", "写真ダンス")
        output_dir = values.get("output_dir") or str(self.root / "youtube_shorts_stock")
        bgm = values.get("bgm", "").strip()
        bgm_volume = values.get("bgm_volume", "0.8").strip() or "0.8"
        cmd = [
            sys.executable,
            str(self.root / "shorts" / "create_photo_dance.py"),
            "--image",
            image,
            "--theme",
            theme,
            "--output-dir",
            output_dir,
            "--bgm-volume",
            bgm_volume,
        ]
        if bgm:
            cmd.extend(["--bgm", bgm])
        return self.run_command(cmd, "写真ダンス風ショートを作成しました")

    def create_reference_project(self, values: dict[str, str]) -> str:
        reference_url = values.get("reference_url", "").strip()
        if not reference_url:
            return result_box("参考動画URLを入力してください。", error=True)
        theme = values.get("theme", "参考動画テンプレート")
        notes = values.get("notes", "")
        replacement = values.get("replace", "").strip()
        output_dir = values.get("output_dir") or str(self.root / "youtube_shorts_stock")
        cmd = [
            sys.executable,
            str(self.root / "shorts" / "create_reference_project.py"),
            "--reference-url",
            reference_url,
            "--theme",
            theme,
            "--notes",
            notes,
            "--output-dir",
            output_dir,
        ]
        if replacement:
            cmd.extend(["--replace", replacement])
        return self.run_command(cmd, "参考動画編集プロジェクトを作成しました")

    def run_command(self, cmd: list[str], success_title: str) -> str:
        completed = subprocess.run(cmd, cwd=self.root, text=True, capture_output=True, check=False)
        output = completed.stdout + completed.stderr
        if completed.returncode != 0:
            return result_box(f"作成に失敗しました。<pre>{html.escape(output)}</pre>", error=True)
        return result_box(f"{html.escape(success_title)}<pre>{html.escape(output)}</pre>")

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002 - inherited API name.
        return


def result_box(content: str, error: bool = False) -> str:
    klass = "card" if error else "card result"
    title = "エラー" if error else "完了"
    return f'<section class="{klass}"><h2>{title}</h2>{content}</section>'


def find_port(start: int = DEFAULT_PORT) -> int:
    for port in range(start, start + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            try:
                probe.bind((HOST, port))
            except OSError:
                continue
            return port
    raise RuntimeError("利用可能なローカルポートが見つかりませんでした。")


def main() -> int:
    root = Path(__file__).resolve().parent
    port = find_port()
    handler = partial(KomchiHandler, directory=str(root))
    server = ThreadingHTTPServer((HOST, port), handler)
    url = f"http://{HOST}:{port}/"
    print("Komchi Creator App を起動しました。")
    print(f"ブラウザが開かない場合は、このURLを開いてください: {url}")
    print("終了するには、この画面で Ctrl+C を押してください。")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n終了しました。")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
