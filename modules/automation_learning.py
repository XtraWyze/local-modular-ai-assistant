"""automation_learning.py
Module for recording and playing back desktop automation macros.
"""

import os
import json

try:
    import pyautogui
except Exception as e:  # pragma: no cover - optional dependency
    pyautogui = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None
from state_manager import register_action

from error_logger import log_error

MACRO_DIR = "macros"
MODULE_NAME = "automation_learning"

__all__ = [
    "record_macro",
    "play_macro",
    "list_macros",
    "record_macro_script",
]


def record_macro(name: str) -> str:
    """Record keyboard and mouse events until ESC is pressed."""
    if _IMPORT_ERROR:
        return f"pyautogui not available: {_IMPORT_ERROR}"
    os.makedirs(MACRO_DIR, exist_ok=True)
    try:
        events = pyautogui.record()
        path = os.path.join(MACRO_DIR, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(events, f)
        register_action(name, path)
        return path
    except Exception as e:
        log_error(f"[{MODULE_NAME}] record_macro error: {e}")
        return f"Error recording macro: {e}"


def record_macro_script(name: str) -> str:
    """Record events and create a Python script that replays them."""
    if _IMPORT_ERROR:
        return f"pyautogui not available: {_IMPORT_ERROR}"
    os.makedirs(MACRO_DIR, exist_ok=True)
    try:
        events = pyautogui.record()
        json_path = os.path.join(MACRO_DIR, f"{name}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(events, f)
        script_path = os.path.join(MACRO_DIR, f"{name}.py")
        with open(script_path, "w", encoding="utf-8") as s:
            s.write(
                "import json\nimport pyautogui\n\n\n"
                "def run():\n"
                f"    events = json.load(open({json_path!r}))\n"
                "    pyautogui.play(events)\n"
            )
        register_action(name, script_path)
        return script_path
    except Exception as e:  # pragma: no cover - conversion errors
        log_error(f"[{MODULE_NAME}] record_macro_script error: {e}")
        return f"Error recording macro script: {e}"


def play_macro(name: str) -> str:
    """Play back a previously recorded macro."""
    if _IMPORT_ERROR:
        return f"pyautogui not available: {_IMPORT_ERROR}"
    path = os.path.join(MACRO_DIR, f"{name}.json")
    if not os.path.exists(path):
        return f"Macro '{name}' not found"
    try:
        with open(path, "r", encoding="utf-8") as f:
            events = json.load(f)
        pyautogui.play(events)
        return f"Played macro {name}"
    except Exception as e:
        log_error(f"[{MODULE_NAME}] play_macro error: {e}")
        return f"Error playing macro: {e}"


def list_macros() -> list[str]:
    """Return the names of saved macros."""
    if not os.path.isdir(MACRO_DIR):
        return []
    return [f[:-5] for f in os.listdir(MACRO_DIR) if f.endswith(".json")]


def get_info():
    return {
        "name": MODULE_NAME,
        "description": "Record and play back user-taught automation macros.",
        "functions": [
            "record_macro",
            "play_macro",
            "list_macros",
            "record_macro_script",
        ],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Allows recording and playback of desktop macros taught by the user."


def register():  # pragma: no cover - simple registration
    from module_manager import ModuleRegistry

    ModuleRegistry.register(
        MODULE_NAME,
        {
            "record_macro": record_macro,
            "play_macro": play_macro,
            "list_macros": list_macros,
            "record_macro_script": record_macro_script,
            "get_info": get_info,
        },
    )

# register()
