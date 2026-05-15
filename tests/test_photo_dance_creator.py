import importlib.util
import sys
import tempfile
from pathlib import Path
import unittest


class PhotoDanceCreatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("photo_dance", "shorts/create_photo_dance.py")
        cls.creator = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.creator
        spec.loader.exec_module(cls.creator)

    def test_package_names_photo_dance_outputs(self):
        package = self.creator.build_package(Path("stock"), "ベイビーダンス")
        self.assertEqual(package.video_path.name, "photo_dance.mp4")
        self.assertEqual(package.storyboard_path.name, "storyboard.txt")

    def test_storyboard_mentions_motion(self):
        storyboard = self.creator.make_storyboard("ベイビーダンス", 12)
        self.assertIn("上下バウンス", storyboard)
        self.assertIn("左右スウェイ", storyboard)

    def test_write_assets_records_photo_dance_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.creator.build_package(Path(tmp), "写真ダンス")
            image = Path(tmp) / "portrait.jpg"
            image.write_bytes(b"fake")
            self.creator.write_assets(package, image, "タイトル", "説明", "絵コンテ", 12)
            self.assertTrue(package.title_path.exists())
            self.assertTrue(package.storyboard_path.exists())
            self.assertIn('"template": "photo_dance"', package.metadata_path.read_text(encoding="utf-8"))

    def test_write_assets_records_bgm_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.creator.build_package(Path(tmp), "写真ダンス")
            image = Path(tmp) / "portrait.jpg"
            bgm = Path(tmp) / "music.mp3"
            image.write_bytes(b"fake")
            bgm.write_bytes(b"fake-bgm")
            self.creator.write_assets(package, image, "タイトル", "説明", "絵コンテ", 12, bgm, 0.7)
            metadata = package.metadata_path.read_text(encoding="utf-8")
            self.assertIn('"bgm":', metadata)
            self.assertIn('"bgm_volume": 0.7', metadata)

    def test_create_video_signature_accepts_bgm_arguments(self):
        self.assertIn("bgm", self.creator.create_video.__annotations__)
        self.assertIn("bgm_volume", self.creator.create_video.__annotations__)


if __name__ == "__main__":
    unittest.main()
