#!/usr/bin/env python3
"""Create a simple vertical short-video stock package.

The script generates a 1080x1920 MP4 when ffmpeg is available. If ffmpeg is not
installed, it still creates the script, title, description, and metadata files so
that the short can be produced later without losing the idea.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

DEFAULT_WINDOWS_STOCK_DIR = r"C:\Users\osk_k\Desktop\ユーチューブショート動画ストック"
DEFAULT_POSIX_STOCK_DIR = "youtube_shorts_stock"
VIDEO_SIZE = "1080x1920"
VIDEO_SECONDS = 20
TEMPLATES = {"simple", "baby_dance"}


@dataclass(frozen=True)
class ShortPackage:
    slug: str
    package_dir: Path
    video_path: Path
    title_path: Path
    description_path: Path
    script_path: Path
    metadata_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ショート動画を作成し、指定フォルダへストックします。")
    parser.add_argument("--theme", required=True, help="動画テーマ。例: 朝の時短テク3選")
    parser.add_argument("--output-dir", default=default_stock_dir(), help="ストック先フォルダ")
    parser.add_argument("--title", help="YouTube用タイトル。省略時は自動生成")
    parser.add_argument(
        "--template",
        default="simple",
        choices=sorted(TEMPLATES),
        help="動画テンプレート。baby_dance はベイビーダンス風の構成を作ります。",
    )
    parser.add_argument("--hashtags", help="説明文末尾に入れるハッシュタグ。省略時はテンプレート別に自動設定")
    parser.add_argument("--no-video", action="store_true", help="MP4を作らず、台本・メタデータだけ作成")
    return parser.parse_args()


def default_stock_dir() -> str:
    if os.name == "nt":
        return DEFAULT_WINDOWS_STOCK_DIR
    return str(Path.cwd() / DEFAULT_POSIX_STOCK_DIR)


def safe_slug(text: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-zぁ-んァ-ン一-龥ー]+", "_", text).strip("_")
    normalized = normalized[:36] or "short"
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{normalized}"


def build_package(output_dir: Path, theme: str) -> ShortPackage:
    slug = safe_slug(theme)
    package_dir = output_dir / slug
    return ShortPackage(
        slug=slug,
        package_dir=package_dir,
        video_path=package_dir / "short_video.mp4",
        title_path=package_dir / "title.txt",
        description_path=package_dir / "description.txt",
        script_path=package_dir / "script.txt",
        metadata_path=package_dir / "metadata.json",
    )


def make_title(theme: str, custom_title: str | None, template: str = "simple") -> str:
    if custom_title:
        return custom_title.strip()
    if template == "baby_dance":
        return f"{theme}｜ベイビーダンス風ショート"
    return f"{theme}｜今日から使えるショート"


def make_script(theme: str, template: str = "simple") -> str:
    if template == "baby_dance":
        return make_baby_dance_script(theme)
    return textwrap.dedent(
        f"""
        0-3秒: 知っておくと便利な「{theme}」を紹介します。
        3-8秒: まずは、今すぐ試しやすいポイントを1つに絞ります。
        8-14秒: コツは、無理なく続けられる形にすることです。
        14-18秒: 気になったら保存して、あとで見返してください。
        18-20秒: 次回も役立つ短い情報を紹介します。
        """
    ).strip()


def make_baby_dance_script(theme: str) -> str:
    return textwrap.dedent(
        f"""
        0-2秒: 赤ちゃんのかわいい表情から開始。大きめテロップ「{theme}」。
        2-5秒: 手をふりふり、体をゆらゆら。動きに合わせて短い効果音を入れる。
        5-9秒: 近めのカットで笑顔や足踏みを見せる。テロップ「この動き、かわいすぎ」。
        9-14秒: いちばんかわいい瞬間をスロー気味にリピート。明るい色のハートや星を重ねる。
        14-18秒: 家族が見守る引きのカット。テロップ「癒やされたら保存」。
        18-20秒: 最後に一番いい表情で締める。テロップ「また見たい人はフォロー」。
        """
    ).strip()


def default_hashtags(template: str) -> str:
    if template == "baby_dance":
        return "#shorts #赤ちゃん #ベイビーダンス #癒し動画 #かわいい"
    return "#shorts #ショート動画"


def make_description(theme: str, hashtags: str | None, template: str = "simple") -> str:
    tags = hashtags or default_hashtags(template)
    if template == "baby_dance":
        return textwrap.dedent(
            f"""
            {theme}のベイビーダンス風ショートです。
            かわいい動きと表情を見やすくまとめるためのストック案です。
            癒やされたら保存して、あとで見返してください。

            {tags}
            """
        ).strip()
    return textwrap.dedent(
        f"""
        {theme}について、短く見やすくまとめました。
        気になったら保存して、あとで見返してください。

        {tags}
        """
    ).strip()


def write_text_assets(package: ShortPackage, title: str, description: str, script: str, template: str = "simple") -> None:
    package.package_dir.mkdir(parents=True, exist_ok=True)
    package.title_path.write_text(title + "\n", encoding="utf-8")
    package.description_path.write_text(description + "\n", encoding="utf-8")
    package.script_path.write_text(script + "\n", encoding="utf-8")
    metadata = {
        "theme": title,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "video": str(package.video_path),
        "title_file": str(package.title_path),
        "description_file": str(package.description_path),
        "script_file": str(package.script_path),
        "status": "draft",
        "template": template,
        "posting": "manual_or_official_api_only",
    }
    package.metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_video(package: ShortPackage, title: str, script: str) -> bool:
    if shutil.which("ffmpeg") is None:
        return False

    subtitle_text = "\\n".join(wrap_for_drawtext(line) for line in script.splitlines()[:4])
    drawtext = (
        "drawtext="
        "fontcolor=white:fontsize=54:line_spacing=18:box=1:boxcolor=black@0.52:boxborderw=28:"
        f"text='{escape_drawtext(title)}\\n\\n{escape_drawtext(subtitle_text)}':"
        "x=(w-text_w)/2:y=(h-text_h)/2"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=0x111827:s={VIDEO_SIZE}:d={VIDEO_SECONDS}",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-vf",
        drawtext,
        "-shortest",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        str(package.video_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True


def wrap_for_drawtext(text: str) -> str:
    return "\\n".join(textwrap.wrap(text, width=22))


def escape_drawtext(text: str) -> str:
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")


def main() -> int:
    args = parse_args()
    package = build_package(Path(args.output_dir).expanduser(), args.theme)
    title = make_title(args.theme, args.title, args.template)
    script = make_script(args.theme, args.template)
    description = make_description(args.theme, args.hashtags, args.template)
    write_text_assets(package, title, description, script, args.template)

    created_video = False
    if not args.no_video:
        created_video = make_video(package, title, script)

    print(f"ストック先を作成しました: {package.package_dir}")
    if created_video:
        print(f"MP4を作成しました: {package.video_path}")
    else:
        print("MP4は未作成です。ffmpegがない場合は台本・タイトル・説明文のみ保存されます。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
