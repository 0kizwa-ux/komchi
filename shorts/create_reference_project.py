#!/usr/bin/env python3
"""Create an editable short-video project from a reference video URL.

The tool does not download or clone the referenced video. It creates a structured
project folder for making an original video with a similar format, including
reference notes, replacement slots, a storyboard, and a rights checklist.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_WINDOWS_STOCK_DIR = r"C:\Users\osk_k\Desktop\ユーチューブショート動画ストック"
DEFAULT_POSIX_STOCK_DIR = "youtube_shorts_stock"


@dataclass(frozen=True)
class ReferenceProject:
    slug: str
    project_dir: Path
    reference_path: Path
    storyboard_path: Path
    replacements_path: Path
    checklist_path: Path
    metadata_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="参考動画URLから編集可能なショート動画プロジェクトを作成します。")
    parser.add_argument("--reference-url", required=True, help="参考動画のURL")
    parser.add_argument("--theme", default="参考動画テンプレート", help="作成する動画のテーマ")
    parser.add_argument("--output-dir", default=default_stock_dir(), help="保存先フォルダ")
    parser.add_argument("--notes", default="", help="参考動画の特徴メモ。例: ベイビーダンス、白字幕、明るいBGM")
    parser.add_argument(
        "--replace",
        action="append",
        default=[],
        help="入れ替え指定。例: '人物A=自分の写真.jpg'。複数回指定できます。",
    )
    return parser.parse_args()


def default_stock_dir() -> str:
    if os.name == "nt":
        return DEFAULT_WINDOWS_STOCK_DIR
    return str(Path.cwd() / DEFAULT_POSIX_STOCK_DIR)


def safe_slug(text: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-zぁ-んァ-ン一-龥ー]+", "_", text).strip("_")
    normalized = normalized[:36] or "reference_project"
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{normalized}"


def validate_reference_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("reference-url は http または https のURLを指定してください。")


def build_project(output_dir: Path, theme: str) -> ReferenceProject:
    slug = safe_slug(theme)
    project_dir = output_dir / slug
    return ReferenceProject(
        slug=slug,
        project_dir=project_dir,
        reference_path=project_dir / "reference_url.txt",
        storyboard_path=project_dir / "storyboard_template.txt",
        replacements_path=project_dir / "asset_replacements.csv",
        checklist_path=project_dir / "rights_checklist.txt",
        metadata_path=project_dir / "metadata.json",
    )


def parse_replacements(values: list[str]) -> list[tuple[str, str]]:
    replacements = []
    for value in values:
        if "=" not in value:
            replacements.append((value.strip(), ""))
            continue
        source, replacement = value.split("=", 1)
        replacements.append((source.strip(), replacement.strip()))
    return replacements


def make_storyboard(theme: str, notes: str) -> str:
    notes_text = notes or "参考動画を見ながら、構図・字幕・テンポを自分の素材で再現する。"
    return textwrap.dedent(
        f"""
        # {theme} 編集テンプレート

        ## 参考メモ
        {notes_text}

        ## 量産用構成
        0-2秒: 冒頭フック。参考動画の雰囲気に寄せつつ、文言はオリジナルにする。
        2-5秒: 主役の人物・商品・動きを見せる。不要な背景やロゴは入れない。
        5-10秒: 一番見せたい動き・表情・変化を入れる。テロップは短く大きく。
        10-15秒: もう一度見たくなる瞬間をリピート、または別角度で見せる。
        15-20秒: 保存・フォロー・次回予告などのCTAで締める。

        ## 編集ルール
        - 参考動画を丸コピーしない。
        - 自分で用意した写真・動画・BGM・効果音を使う。
        - 人物、背景、文字、BGM、ロゴ、商品名は必要に応じて入れ替える。
        - 実在人物や子どもの素材は許可を得て使う。
        """
    ).strip()


def write_project(project: ReferenceProject, reference_url: str, theme: str, notes: str, replacements: list[tuple[str, str]]) -> None:
    project.project_dir.mkdir(parents=True, exist_ok=True)
    project.reference_path.write_text(reference_url + "\n", encoding="utf-8")
    project.storyboard_path.write_text(make_storyboard(theme, notes) + "\n", encoding="utf-8")
    with project.replacements_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_slot", "replacement_asset", "status", "memo"])
        writer.writeheader()
        if replacements:
            for source, replacement in replacements:
                writer.writerow({"source_slot": source, "replacement_asset": replacement, "status": "pending", "memo": ""})
        else:
            writer.writerows(
                [
                    {"source_slot": "人物A", "replacement_asset": "", "status": "pending", "memo": "差し替える人物写真・動画"},
                    {"source_slot": "BGM", "replacement_asset": "", "status": "pending", "memo": "権利上使える音源"},
                    {"source_slot": "背景", "replacement_asset": "", "status": "pending", "memo": "自分で撮影した背景や素材"},
                    {"source_slot": "テロップ", "replacement_asset": "", "status": "pending", "memo": "オリジナル文言"},
                ]
            )
    project.checklist_path.write_text(make_checklist() + "\n", encoding="utf-8")
    metadata = {
        "reference_url": reference_url,
        "theme": theme,
        "notes": notes,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "template": "reference_edit_project",
        "policy": "inspired_original_not_exact_clone",
        "files": {
            "storyboard": str(project.storyboard_path),
            "replacements": str(project.replacements_path),
            "checklist": str(project.checklist_path),
        },
    }
    project.metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_checklist() -> str:
    return textwrap.dedent(
        """
        # 投稿前・権利チェック

        - [ ] 参考動画をそのまま転載していない
        - [ ] BGM・効果音は自分で利用権を確認したものを使っている
        - [ ] 人物写真・子どもの肖像は本人または保護者の許可を得ている
        - [ ] ロゴ・透かし・他人のIDを映していない
        - [ ] テロップ文言は自分の言葉に変えている
        - [ ] 投稿先の規約に反していない
        """
    ).strip()


def main() -> int:
    args = parse_args()
    try:
        validate_reference_url(args.reference_url)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    project = build_project(Path(args.output_dir).expanduser(), args.theme)
    write_project(project, args.reference_url, args.theme, args.notes, parse_replacements(args.replace))
    print(f"参考動画編集プロジェクトを作成しました: {project.project_dir}")
    print("参考動画の丸コピーではなく、素材を差し替えてオリジナル動画として作成してください。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
