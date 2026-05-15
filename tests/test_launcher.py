import importlib.util
from pathlib import Path
import unittest


class LauncherTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("launcher", "start_room_draft_assistant.py")
        cls.launcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.launcher)

    def test_entrypoint_exists(self):
        self.assertTrue(Path(self.launcher.ENTRYPOINT).exists())

    def test_find_port_returns_int(self):
        port = self.launcher.find_port(9876)
        self.assertIsInstance(port, int)
        self.assertGreaterEqual(port, 9876)

    def test_platform_launchers_reference_python_launcher(self):
        self.assertIn("start_room_draft_assistant.py", Path("start_room_draft_assistant.command").read_text())
        self.assertIn("start_room_draft_assistant.py", Path("start_room_draft_assistant.bat").read_text())


if __name__ == "__main__":
    unittest.main()
