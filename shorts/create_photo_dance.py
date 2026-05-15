#!/usr/bin/env python3
"""Create a simple dance-like short video from one portrait image.

This is not a pose-generation model. It makes a still portrait feel like a short
"dance" by applying beat-synced bounce, zoom, and title-card motion with ffmpeg.
If ffmpeg is unavailable, it still creates a storyboard package so the idea can
be produced later.
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
DEFAULT_SECONDS = 12
DEFAULT_FPS = 30


@dataclass(frozen=True)
class PhotoDancePackage:
    slug: str
    package_dir: Path
    video_path: Path
    title_path: Path
    description_path: Path
    storyboard_path: Path
    metadata_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="写真1枚から簡単なダンス風ショート動画を作成します。")
    parser.add_argument("--image", required=True, help="元にする肖像画像のパス")
    parser.add_argument("--theme", default="写真ダンス", help="動画テーマ・タイトル用テキスト")
    parser.add_argument("--output-dir", default=default_stock_dir(), help="ストック先フォルダ")
    parser.add_argument("--seconds", type=int, default=DEFAULT_SECONDS, help="動画秒数。既定は12秒")
    parser.add_argument("--title", help="YouTube用タイトル。省略時は自動生成")
    parser.add_argument("--bgm", help="追加するBGMファイルのパス。省略時は簡易ビート音を使います")
    parser.add_argument("--bgm-volume", type=float, default=0.8, help="BGM音量。既定は0.8")
    parser.add_argument("--hashtags", default="#shorts #写真ダンス #AI動画", help="説明文末尾に入れるハッシュタグ")
    parser.add_argument("--no-video", action="store_true", help="MP4を作らず、絵コンテ・メタデータだけ作成")
    return parser.parse_args()


def default_stock_dir() -> str:
    if os.name == "nt":
        return DEFAULT_WINDOWS_STOCK_DIR
    return str(Path.cwd() / DEFAULT_POSIX_STOCK_DIR)


def safe_slug(text: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-zぁ-んァ-ン一-龥ー]+", "_", text).strip("_")
    normalized = normalized[:36] or "photo_dance"
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{normalized}"


def build_package(output_dir: Path, theme: str) -> PhotoDancePackage:
    slug = safe_slug(theme)
    package_dir = output_dir / slug
    return PhotoDancePackage(
        slug=slug,
        package_dir=package_dir,
        video_path=package_dir / "photo_dance.mp4",
        title_path=package_dir / "title.txt",
        description_path=package_dir / "description.txt",
        storyboard_path=package_dir / "storyboard.txt",
        metadata_path=package_dir / "metadata.json",
    )


def make_title(theme: str, custom_title: str | None) -> str:
    if custom_title:
        return custom_title.strip()
    return f"{theme}｜写真1枚でダンス風ショート"


def make_description(theme: str, hashtags: str) -> str:
    return textwrap.dedent(
        f"""
        {theme}を写真1枚からダンス風ショートにしたストック動画です。
        跳ねる動き・ズーム・リズム感のある編集で、短く見やすくまとめます。

        {hashtags}
        """
    ).strip()


def make_storyboard(theme: str, seconds: int) -> str:
    midpoint = max(seconds // 2, 1)
    return textwrap.dedent(
        f"""
        0-2秒: 肖像画像を中央に配置。タイトル「{theme}」。
        2-{midpoint}秒: ビートに合わせて上下バウンス、軽いズーム、左右スウェイ。
        {midpoint}-{max(seconds - 2, midpoint + 1)}秒: 少し大きめに寄って、表情を見せる。
        {max(seconds - 2, midpoint + 1)}-{seconds}秒: 最後に軽く跳ねて停止。保存・フォロー用の余白を残す。
        """
    ).strip()


def write_assets(
    package: PhotoDancePackage,
    image: Path,
    title: str,
    description: str,
    storyboard: str,
    seconds: int,
    bgm: Path | None = None,
    bgm_volume: float = 0.8,
) -> None:
    package.package_dir.mkdir(parents=True, exist_ok=True)
    package.title_path.write_text(title + "\n", encoding="utf-8")
    package.description_path.write_text(description + "\n", encoding="utf-8")
    package.storyboard_path.write_text(storyboard + "\n", encoding="utf-8")
    metadata = {
        "source_image": str(image),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "video": str(package.video_path),
        "seconds": seconds,
        "bgm": str(bgm) if bgm else None,
        "bgm_volume": bgm_volume,
        "template": "photo_dance",
        "motion": ["bounce", "zoom", "sway"],
        "posting": "manual_or_official_api_only",
    }
    package.metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def create_video(package: PhotoDancePackage, image: Path, title: str, seconds: int, bgm: Path | None, bgm_volume: float) -> bool:
    if shutil.which("ffmpeg") is None:
        return False

    safe_title = escape_drawtext(title)
    video_filter = (
        "scale=900:1500:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x111827,"
        "zoompan=z='1+0.045*sin(on/5)':"
        "x='iw/2-(iw/zoom/2)+18*sin(on/7)':"
        "y='ih/2-(ih/zoom/2)+34*sin(on/4)':"
        f"d=1:s={VIDEO_SIZE}:fps={DEFAULT_FPS},"
        "drawtext=fontcolor=white:fontsize=58:line_spacing=12:box=1:boxcolor=black@0.48:boxborderw=24:"
        f"text='{safe_title}':x=(w-text_w)/2:y=h*0.08,"
        "format=yuv420p"
    )
    cmd = ["ffmpeg", "-y", "-loop", "1", "-t", str(seconds), "-i", str(image)]
    if bgm:
        cmd.extend(["-stream_loop", "-1", "-i", str(bgm)])
    else:
        cmd.extend(["-f", "lavfi", "-i", "sine=frequency=128:sample_rate=44100"])
    cmd.extend(
        [
            "-vf",
            video_filter,
            "-af",
            f"volume={max(bgm_volume, 0.0)}",
            "-shortest",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(package.video_path),
        ]
    )
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True


def escape_drawtext(text: str) -> str:
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")


def main() -> int:
    args = parse_args()
    image = Path(args.image).expanduser()
    if not image.exists():
        print(f"画像が見つかりません: {image}", file=sys.stderr)
        return 1

    bgm = Path(args.bgm).expanduser() if args.bgm else None
    if bgm and not bgm.exists():
        print(f"BGMファイルが見つかりません: {bgm}", file=sys.stderr)
        return 1

    seconds = max(args.seconds, 3)
    package = build_package(Path(args.output_dir).expanduser(), args.theme)
    title = make_title(args.theme, args.title)
    description = make_description(args.theme, args.hashtags)
    storyboard = make_storyboard(args.theme, seconds)
    write_assets(package, image, title, description, storyboard, seconds, bgm, args.bgm_volume)

    created_video = False
    if not args.no_video:
        created_video = create_video(package, image, title, seconds, bgm, args.bgm_volume)

    print(f"写真ダンス用ストックを作成しました: {package.package_dir}")
    if created_video:
        print(f"MP4を作成しました: {package.video_path}")
    else:
        print("MP4は未作成です。ffmpegがない場合は絵コンテ・タイトル・説明文のみ保存されます。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
