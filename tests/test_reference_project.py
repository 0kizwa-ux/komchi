import importlib.util
import sys
import tempfile
from pathlib import Path
import unittest


class ReferenceProjectTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("reference_project", "shorts/create_reference_project.py")
        cls.creator = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.creator
        spec.loader.exec_module(cls.creator)

    def test_parse_replacements_supports_asset_swaps(self):
        replacements = self.creator.parse_replacements(["人物A=portrait.jpg", "BGM=music.mp3"])
        self.assertEqual(replacements, [("人物A", "portrait.jpg"), ("BGM", "music.mp3")])

    def test_validate_reference_url_rejects_invalid_value(self):
        with self.assertRaises(ValueError):
            self.creator.validate_reference_url("not-a-url")

    def test_write_project_creates_editable_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.creator.build_project(Path(tmp), "ベイビーダンス参考")
            self.creator.write_project(
                project,
                "https://www.tiktok.com/@bkkth/video/7622581244072561936",
                "ベイビーダンス参考",
                "明るいBGM",
                [("人物A", "portrait.jpg")],
            )
            self.assertTrue(project.reference_path.exists())
            self.assertTrue(project.storyboard_path.exists())
            self.assertTrue(project.replacements_path.exists())
            self.assertTrue(project.checklist_path.exists())
            self.assertIn("portrait.jpg", project.replacements_path.read_text(encoding="utf-8-sig"))
            self.assertIn("inspired_original_not_exact_clone", project.metadata_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
