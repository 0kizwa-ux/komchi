from pathlib import Path
import unittest


class ButtonHtmlTest(unittest.TestCase):
    def setUp(self):
        self.html = Path("room_draft_button.html").read_text(encoding="utf-8")

    def test_html_is_api_key_free_button_ui(self):
        self.assertIn("APIキー不要", self.html)
        self.assertIn("投稿候補を作成", self.html)
        self.assertIn("楽天ROOMへの投稿は、内容を確認してから手動", self.html)

    def test_html_can_generate_csv_and_copy_comments(self):
        self.assertIn("CSVをダウンロード", self.html)
        self.assertIn("コメント案をコピー", self.html)
        self.assertIn("makeCsv", self.html)

    def test_html_links_to_rakuten_search_for_manual_check(self):
        self.assertIn("search.rakuten.co.jp/search/mall", self.html)
        self.assertIn("楽天市場で確認", self.html)


if __name__ == "__main__":
    unittest.main()
