import unittest

from scripts.room_draft_assistant import (
    Item,
    filter_items,
    format_price,
    make_room_comment,
    render_markdown,
    risk_hits,
)


class RoomDraftAssistantTest(unittest.TestCase):
    def test_make_room_comment_adds_manual_check_hint(self):
        item = Item(
            name="コーヒー ギフト",
            price=2500,
            url="https://example.test/item",
            shop_name="テスト店",
            review_average=4.6,
            review_count=20,
            caption="香りを楽しめるギフト向けの商品です。",
        )

        comment = make_room_comment(item)

        self.assertIn("コーヒー ギフト", comment)
        self.assertIn("レビュー平均4.6・20件", comment)
        self.assertIn("商品ページでサイズ・内容量・配送条件を確認", comment)

    def test_risk_hits_finds_unsafe_claims(self):
        self.assertEqual(risk_hits("絶対に痩せるアイテム"), ["絶対", "痩せる"])

    def test_filter_items_uses_review_thresholds(self):
        items = [
            Item("A", 1000, "https://a.example", "店A", 4.8, 10),
            Item("B", 1000, "https://b.example", "店B", 3.8, 100),
        ]

        filtered = filter_items(items, min_review_count=10, min_review_average=4.0)

        self.assertEqual([item.name for item in filtered], ["A"])

    def test_render_markdown_declares_no_auto_posting(self):
        item = Item("A", 1000, "https://a.example", "店A", None, None)

        markdown = render_markdown("テスト", [item])

        self.assertIn("楽天ROOMへの自動投稿は行っていません", markdown)
        self.assertIn("手動確認チェックリスト", markdown)

    def test_format_price(self):
        self.assertEqual(format_price(12345), "12,345円")
        self.assertEqual(format_price(None), "未取得")


if __name__ == "__main__":
    unittest.main()
