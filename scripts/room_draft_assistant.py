#!/usr/bin/env python3
"""Create human-reviewed Rakuten ROOM draft posts from Rakuten Ichiba items.

This script intentionally does not automate Rakuten ROOM posting. It only creates
reviewable Markdown/CSV drafts so a person can verify and post manually.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode
from urllib.request import urlopen

API_ENDPOINT = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401"
DEFAULT_ELEMENTS = ",".join(
    [
        "itemName",
        "itemPrice",
        "itemUrl",
        "affiliateUrl",
        "shopName",
        "reviewAverage",
        "reviewCount",
        "itemCaption",
    ]
)
RISK_TERMS = [
    "治る",
    "完治",
    "絶対",
    "必ず",
    "100%",
    "痩せる",
    "若返る",
    "シミが消える",
    "副作用なし",
    "最安値",
    "No.1",
]


@dataclass(frozen=True)
class Item:
    name: str
    price: int | None
    url: str
    shop_name: str
    review_average: float | None
    review_count: int | None
    caption: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="楽天ROOMへ手動投稿するための商品候補と紹介文下書きを作成します。"
    )
    parser.add_argument("--keyword", required=True, help="楽天市場の商品検索キーワード")
    parser.add_argument("--limit", type=int, default=10, help="出力する候補数。1〜30")
    parser.add_argument("--output", default="room_drafts.md", help="Markdown出力先")
    parser.add_argument("--csv", dest="csv_path", help="CSV出力先。省略時はCSVを作成しません")
    parser.add_argument("--min-review-count", type=int, default=0, help="最低レビュー件数")
    parser.add_argument("--min-review-average", type=float, default=0.0, help="最低レビュー平均")
    parser.add_argument("--sort", default="standard", help="楽天商品検索APIのsort値")
    parser.add_argument("--mock", action="store_true", help="APIを呼ばずモックデータで出力します")
    return parser.parse_args()


def fetch_items(keyword: str, limit: int, sort: str) -> list[Item]:
    app_id = os.environ.get("RAKUTEN_APP_ID")
    if not app_id:
        raise SystemExit("RAKUTEN_APP_ID が未設定です。--mock で動作確認するか、環境変数を設定してください。")

    params = {
        "applicationId": app_id,
        "affiliateId": os.environ.get("RAKUTEN_AFFILIATE_ID", ""),
        "format": "json",
        "formatVersion": 2,
        "keyword": keyword,
        "hits": min(max(limit, 1), 30),
        "sort": sort,
        "elements": DEFAULT_ELEMENTS,
    }
    params = {key: value for key, value in params.items() if value != ""}
    url = f"{API_ENDPOINT}?{urlencode(params)}"

    with urlopen(url, timeout=20) as response:  # noqa: S310 - user-provided official API endpoint only.
        payload = json.loads(response.read().decode("utf-8"))

    return [item_from_api(raw) for raw in payload.get("items", [])]


def item_from_api(raw: dict) -> Item:
    url = raw.get("affiliateUrl") or raw.get("itemUrl") or ""
    return Item(
        name=str(raw.get("itemName", "")).strip(),
        price=to_int(raw.get("itemPrice")),
        url=str(url).strip(),
        shop_name=str(raw.get("shopName", "")).strip(),
        review_average=to_float(raw.get("reviewAverage")),
        review_count=to_int(raw.get("reviewCount")),
        caption=str(raw.get("itemCaption", "")).strip(),
    )


def to_int(value: object) -> int | None:
    try:
        return int(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def to_float(value: object) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def mock_items(keyword: str, limit: int) -> list[Item]:
    base_items = [
        Item(
            name=f"{keyword} お試しセット",
            price=1980,
            url="https://item.rakuten.co.jp/example/sample-1/",
            shop_name="サンプルショップ",
            review_average=4.5,
            review_count=128,
            caption="毎日の暮らしで使いやすいセット商品です。",
        ),
        Item(
            name=f"{keyword} ギフトボックス",
            price=3480,
            url="https://item.rakuten.co.jp/example/sample-2/",
            shop_name="ギフト専門店",
            review_average=4.7,
            review_count=64,
            caption="贈り物向けのパッケージで、季節のギフトにも選ばれています。",
        ),
        Item(
            name=f"{keyword} 大容量タイプ",
            price=4980,
            url="https://item.rakuten.co.jp/example/sample-3/",
            shop_name="まとめ買いストア",
            review_average=4.2,
            review_count=210,
            caption="ストックしやすい大容量タイプです。",
        ),
    ]
    return base_items[:limit]


def filter_items(items: Iterable[Item], min_review_count: int, min_review_average: float) -> list[Item]:
    filtered = []
    for item in items:
        review_count = item.review_count or 0
        review_average = item.review_average or 0.0
        if review_count >= min_review_count and review_average >= min_review_average:
            filtered.append(item)
    return filtered


def make_room_comment(item: Item) -> str:
    review = ""
    if item.review_average is not None and item.review_count is not None:
        review = f"レビュー平均{item.review_average:.1f}・{item.review_count}件の実績も参考になります。"
    elif item.review_count:
        review = f"レビュー{item.review_count}件も参考になります。"

    caption_hint = summarize_caption(item.caption)
    parts = [
        f"気になったのは「{item.name}」。",
        caption_hint,
        review,
        "商品ページでサイズ・内容量・配送条件を確認してから選ぶのがおすすめです。",
    ]
    return " ".join(part for part in parts if part).strip()


def summarize_caption(caption: str) -> str:
    normalized = " ".join(caption.split())
    if not normalized:
        return "暮らしに取り入れやすそうなアイテムです。"
    return textwrap.shorten(normalized, width=80, placeholder="…")


def risk_hits(text: str) -> list[str]:
    return [term for term in RISK_TERMS if term.lower() in text.lower()]


def render_markdown(keyword: str, items: list[Item]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# 楽天ROOM 投稿候補: {keyword}",
        "",
        f"生成日時: {generated_at}",
        "",
        "> このファイルは投稿下書きです。楽天ROOMへの自動投稿は行っていません。投稿前に必ず人間が確認してください。",
        "",
        "## 手動確認チェックリスト",
        "",
        "- [ ] 商品ページで価格・在庫・配送条件を確認した",
        "- [ ] 紹介文が商品実態と一致している",
        "- [ ] 効果効能・No.1・最安値などの断定表現がない",
        "- [ ] 外部リンクや無許可画像を追加していない",
        "- [ ] 同一文面の連投になっていない",
        "",
    ]
    for index, item in enumerate(items, start=1):
        comment = make_room_comment(item)
        hits = risk_hits(comment)
        risk_label = "要確認: " + ", ".join(hits) if hits else "簡易チェックOK"
        lines.extend(
            [
                f"## {index}. {item.name}",
                "",
                f"- ショップ: {item.shop_name or '未取得'}",
                f"- 価格: {format_price(item.price)}",
                f"- レビュー: {format_review(item)}",
                f"- URL: {item.url}",
                f"- リスク表現: {risk_label}",
                "",
                "ROOMコメント案:",
                "",
                f"> {comment}",
                "",
            ]
        )
    return "\n".join(lines)


def write_csv(path: Path, items: list[Item]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "item_name",
                "shop_name",
                "price",
                "review_average",
                "review_count",
                "url",
                "room_comment",
                "risk_terms",
                "manual_review_done",
            ],
        )
        writer.writeheader()
        for item in items:
            comment = make_room_comment(item)
            writer.writerow(
                {
                    "item_name": item.name,
                    "shop_name": item.shop_name,
                    "price": item.price or "",
                    "review_average": item.review_average or "",
                    "review_count": item.review_count or "",
                    "url": item.url,
                    "room_comment": comment,
                    "risk_terms": ",".join(risk_hits(comment)),
                    "manual_review_done": "FALSE",
                }
            )


def format_price(price: int | None) -> str:
    return f"{price:,}円" if price is not None else "未取得"


def format_review(item: Item) -> str:
    if item.review_average is None and item.review_count is None:
        return "未取得"
    if item.review_average is None:
        return f"{item.review_count}件"
    if item.review_count is None:
        return f"平均{item.review_average:.1f}"
    return f"平均{item.review_average:.1f} / {item.review_count}件"


def main() -> int:
    args = parse_args()
    limit = min(max(args.limit, 1), 30)
    items = mock_items(args.keyword, limit) if args.mock else fetch_items(args.keyword, limit, args.sort)
    items = filter_items(items, args.min_review_count, args.min_review_average)[:limit]

    output_path = Path(args.output)
    output_path.write_text(render_markdown(args.keyword, items), encoding="utf-8")
    if args.csv_path:
        write_csv(Path(args.csv_path), items)

    print(f"{len(items)}件の投稿候補を作成しました: {output_path}")
    if args.csv_path:
        print(f"CSVも作成しました: {args.csv_path}")
    print("楽天ROOMには自動投稿していません。内容確認後、手動で投稿してください。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
