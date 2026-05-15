#!/usr/bin/env python3
"""Open the no-API Rakuten ROOM draft assistant in a local browser.

The launcher serves the static HTML from this repository on localhost so browser
features such as copy-to-clipboard and CSV download work more reliably than when
opening the HTML file directly from disk.
"""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import sys
import webbrowser

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
ENTRYPOINT = "room_draft_button.html"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002 - inherited API name.
        return


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
    entrypoint = root / ENTRYPOINT
    if not entrypoint.exists():
        print(f"{ENTRYPOINT} が見つかりません。ファイル一式を同じフォルダに置いてください。", file=sys.stderr)
        return 1

    port = find_port()
    handler = partial(QuietHandler, directory=str(root))
    server = ThreadingHTTPServer((HOST, port), handler)
    url = f"http://{HOST}:{port}/{ENTRYPOINT}"

    print("楽天ROOM 投稿候補ツールを起動しました。")
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
