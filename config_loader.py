# config_loader.py

import json
import os
import sys
import types


def apply_emulation(config: dict) -> None:
    """Monkey patch automation libraries when ``emulate_actions`` is true."""
    if not config.get("emulate_actions"):
        return

    class DummyModule(types.ModuleType):
        def __getattr__(self, name):
            def _dummy(*args, **kwargs):
                print(
                    f"[EMULATION] {self.__name__}.{name} called with {args} {kwargs}"
                )
                if name == "position":
                    return (0, 0)
                return None

            return _dummy

    sys.modules["pyautogui"] = DummyModule("pyautogui")
    sys.modules["pygetwindow"] = DummyModule("pygetwindow")
    sys.modules["pyperclip"] = DummyModule("pyperclip")

class ConfigLoader:
    def __init__(self, path="config.json"):
        """Load and watch a JSON configuration file."""
        self.path = path
        self.last_modified = None
        self.config = {}
        self.load_config()

    def load_config(self):
        """Read ``self.path`` and return the parsed dictionary."""
        with open(self.path, "r") as f:
            self.config = json.load(f)
        self.last_modified = os.path.getmtime(self.path)
        # apply_emulation(self.config)
        return self.config

    def reload_if_changed(self):
        mod_time = os.path.getmtime(self.path)
        if mod_time != self.last_modified:
            print("[ConfigLoader] Detected config change, reloading...")
            return self.load_config()
        return self.config

    def reload(self):
        """Force reload, even if not changed."""
        return self.load_config()
