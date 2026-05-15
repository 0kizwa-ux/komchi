import importlib.util
import sys
import tempfile
from pathlib import Path
import unittest


class ShortStockCreatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("creator", "shorts/create_stock_short.py")
        cls.creator = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.creator
        spec.loader.exec_module(cls.creator)

    def test_default_windows_stock_path_is_configured(self):
        self.assertEqual(
            self.creator.DEFAULT_WINDOWS_STOCK_DIR,
            r"C:\Users\osk_k\Desktop\ユーチューブショート動画ストック",
        )

    def test_build_package_uses_theme_slug(self):
        package = self.creator.build_package(Path("stock"), "朝の時短テク3選")
        self.assertIn("朝の時短テク3選", package.slug)
        self.assertEqual(package.video_path.name, "short_video.mp4")
        self.assertEqual(package.title_path.name, "title.txt")

    def test_write_text_assets_creates_stock_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.creator.build_package(Path(tmp), "便利ワザ")
            self.creator.write_text_assets(package, "タイトル", "説明", "台本")
            self.assertTrue(package.title_path.exists())
            self.assertTrue(package.description_path.exists())
            self.assertTrue(package.script_path.exists())
            self.assertTrue(package.metadata_path.exists())

    def test_baby_dance_template_creates_dance_script_and_tags(self):
        script = self.creator.make_script("ベイビーダンス", "baby_dance")
        description = self.creator.make_description("ベイビーダンス", None, "baby_dance")
        title = self.creator.make_title("ベイビーダンス", None, "baby_dance")

        self.assertIn("手をふりふり", script)
        self.assertIn("癒やされたら保存", script)
        self.assertIn("#ベイビーダンス", description)
        self.assertIn("ベイビーダンス風ショート", title)

    def test_metadata_records_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.creator.build_package(Path(tmp), "ベイビーダンス")
            self.creator.write_text_assets(package, "タイトル", "説明", "台本", "baby_dance")
            self.assertIn('"template": "baby_dance"', package.metadata_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
