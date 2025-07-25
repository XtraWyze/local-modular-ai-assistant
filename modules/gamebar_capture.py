"""Control Xbox Game Bar capture widget via hotkeys."""

import sys
from error_logger import log_error

try:  # optional runtime dependency
    import keyboard
except Exception as e:  # pragma: no cover - optional dep
    keyboard = None
    _IMPORT_ERROR = e
else:  # pragma: no cover - optional dep
    _IMPORT_ERROR = None

try:  # optional fallback
    import pyautogui
except Exception:  # pragma: no cover - optional dep
    pyautogui = None

MODULE_NAME = "gamebar_capture"

__all__ = [
    "open_capture",
    "toggle_recording",
    "capture_screenshot",
    "capture_last_30s",
]


def _send_combo(keys: list[str]) -> str:
    """Send a key combination using available backends."""
    if not sys.platform.startswith("win"):
        return "Xbox Game Bar is only supported on Windows"

    combo = "+".join(keys)
    try:
        if keyboard is not None:
            keyboard.send(combo)
            return "ok"
        if pyautogui is not None:
            pyautogui.hotkey(*keys)
            return "ok"
        return f"keyboard module missing: {_IMPORT_ERROR}"
    except Exception as e:  # pragma: no cover - OS specific
        log_error(f"[{MODULE_NAME}] send combo error: {e}")
        return f"Error sending keys: {e}"


def open_capture() -> str:
    """Open the Xbox Game Bar overlay."""
    result = _send_combo(["win", "g"])
    return "Game Bar opened" if result == "ok" else result


def toggle_recording() -> str:
    """Start or stop screen recording."""
    result = _send_combo(["win", "alt", "r"])
    return "Recording toggled" if result == "ok" else result


def capture_screenshot() -> str:
    """Take a Game Bar screenshot."""
    result = _send_combo(["win", "alt", "printscreen"])
    return "Screenshot captured" if result == "ok" else result


def capture_last_30s() -> str:
    """Record the last 30 seconds of gameplay."""
    result = _send_combo(["win", "alt", "g"])
    return "Last 30 seconds captured" if result == "ok" else result


def get_info():
    return {
        "name": MODULE_NAME,
        "description": "Control Xbox Game Bar capture: open overlay, recording, screenshot.",
        "functions": [
            "open_capture",
            "toggle_recording",
            "capture_screenshot",
            "capture_last_30s",
        ],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Operate the Xbox Game Bar capture widget via hotkeys."


def register():
    from module_manager import ModuleRegistry

    ModuleRegistry.register(
        MODULE_NAME,
        {
            "open_capture": open_capture,
            "toggle_recording": toggle_recording,
            "capture_screenshot": capture_screenshot,
            "capture_last_30s": capture_last_30s,
            "get_info": get_info,
        },
    )

# register()

