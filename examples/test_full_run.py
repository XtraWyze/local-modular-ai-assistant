import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from module_manager import ModuleRegistry

MODULE_CONFIGS = {
    "hello_module": {"greeting": "Hi!"}
}

TESTS = [
    ("modules.hello_module", "say_hello", {"name": "Levi"}),
    ("modules.llm_module", "chat", {"prompt": "Say hello!"}),
    ("modules.pyautogui_tools", "get_mouse_position", {}),
    ("modules.desktop_shortcuts", "get_desktop_path", {}),
    ("modules.tts_integration", "speak", {"text": "This is a test of Coqui TTS.", "async_play": False}),
    ("modules.vosk_integration", "get_info", {}),
    ("modules.vision_tools", "get_info", {}),
    ("modules.voice_input", "get_info", {}),
    ("modules.window_tools", "get_info", {}),
    ("modules.actions", "get_info", {}),
    ("modules.tools", "get_info", {}),
    ("modules.utils", "get_info", {}),
]

class FullRunTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = ModuleRegistry()
        cls.registry.auto_discover("modules", config_map=MODULE_CONFIGS)
        import llm_interface
        llm_interface.config["llm_backend"] = "mock"

    def assert_non_empty(self, result):
        self.assertIsNotNone(result, "Result is None")
        if isinstance(result, str):
            self.assertTrue(result.strip(), "Result string is empty")
        elif isinstance(result, (list, tuple, dict, set)):
            self.assertTrue(len(result) > 0, "Result collection is empty")
        # Other result types are considered valid as long as not None

    def test_module_calls(self):
        for mod_name, func_name, kwargs in TESTS:
            with self.subTest(module=mod_name, function=func_name):
                if mod_name not in self.registry.modules:
                    self.skipTest(f"Module {mod_name} not loaded")
                result = self.registry.call(mod_name, func_name, **kwargs)
                self.assert_non_empty(result)

if __name__ == "__main__":
    unittest.main()
