import importlib.util
import sys
from pathlib import Path
import unittest


class KomchiAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("komchi_app", "komchi_app.py")
        cls.app = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.app
        spec.loader.exec_module(cls.app)

    def test_dashboard_has_main_tools(self):
        html = self.app.DASHBOARD_HTML
        self.assertIn("Komchi Creator App", html)
        self.assertIn("ROOM下書きUI", html)
        self.assertIn("写真1枚ダンス風ショート", html)
        self.assertIn("ショート動画ストック作成", html)
        self.assertIn("参考動画テンプレート作成", html)

    def test_find_port_returns_available_port(self):
        port = self.app.find_port(9900)
        self.assertIsInstance(port, int)
        self.assertGreaterEqual(port, 9900)

    def test_desktop_shortcut_installers_exist(self):
        self.assertTrue(Path("install_desktop_shortcuts.ps1").exists())
        self.assertTrue(Path("install_desktop_shortcuts.bat").exists())
        self.assertIn("Komchi Creator App", Path("install_desktop_shortcuts.ps1").read_text(encoding="utf-8"))

    def test_beginner_friendly_click_targets_exist(self):
        self.assertTrue(Path("ここをダブルクリック_最初に起動.bat").exists())
        self.assertTrue(Path("デスクトップにアイコンを作成.bat").exists())
        self.assertIn("komchi_app.py", Path("ここをダブルクリック_最初に起動.bat").read_text(encoding="utf-8"))
        self.assertIn("install_desktop_shortcuts.ps1", Path("デスクトップにアイコンを作成.bat").read_text(encoding="utf-8"))

    def test_ascii_numbered_launch_targets_exist(self):
        self.assertTrue(Path("00_START_HERE.bat").exists())
        self.assertTrue(Path("00_CREATE_DESKTOP_ICONS.bat").exists())
        self.assertTrue(Path("START_HERE_最初に読んでください.txt").exists())
        self.assertIn("komchi_app.py", Path("00_START_HERE.bat").read_text(encoding="utf-8"))
        self.assertIn("install_desktop_shortcuts.ps1", Path("00_CREATE_DESKTOP_ICONS.bat").read_text(encoding="utf-8"))

    def test_simplest_launch_targets_exist(self):
        self.assertTrue(Path("START.bat").exists())
        self.assertTrue(Path("ICONS.bat").exists())
        self.assertIn("komchi_app.py", Path("START.bat").read_text(encoding="utf-8"))
        self.assertIn("install_desktop_shortcuts.ps1", Path("ICONS.bat").read_text(encoding="utf-8"))
        self.assertIn("Python が見つかりません", Path("START.bat").read_text(encoding="utf-8"))

    def test_debug_launcher_exists(self):
        self.assertTrue(Path("START_DEBUG.bat").exists())
        debug_text = Path("START_DEBUG.bat").read_text(encoding="utf-8")
        self.assertIn("Checking Python", debug_text)
        self.assertIn("komchi_app.py", debug_text)

    def test_no_black_screen_launcher_exists(self):
        self.assertTrue(Path("START_NO_BLACK_SCREEN.vbs").exists())
        self.assertTrue(Path("START_LOG_ONLY.bat").exists())
        self.assertIn("START_LOG.txt", Path("START_NO_BLACK_SCREEN.vbs").read_text(encoding="utf-8"))
        self.assertIn("START_LOG.txt", Path("START_LOG_ONLY.bat").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
