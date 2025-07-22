import sys
import types


def apply_simulation(config: dict) -> None:
    """Monkey patch automation libraries when ``simulate_actions`` is true."""
    if not config.get("simulate_actions"):
        return

    class DummyModule(types.ModuleType):
        def __getattr__(self, name):
            def _dummy(*args, **kwargs):
                print(f"[SIMULATION] {self.__name__}.{name} called with {args} {kwargs}")
                if name == "position":
                    return (0, 0)
                return None
            return _dummy

    sys.modules["pyautogui"] = DummyModule("pyautogui")
    sys.modules["pygetwindow"] = DummyModule("pygetwindow")
    sys.modules["pyperclip"] = DummyModule("pyperclip")
