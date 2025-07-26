"""Automation learning module.

This module provides utilities to record and play back desktop automation
macros. Recording uses ``pyautogui`` if available. If the installed
``pyautogui`` library does not provide ``record``/``play`` helpers, it falls
back to a lightweight implementation powered by ``pynput``.
"""

import os
import json
import time

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
    "record_events",
    "play_events",
    "record_macro",
    "play_macro",
    "list_macros",
    "record_macro_script",
]


def record_events() -> list:
    """Capture keyboard and mouse input until ESC is pressed."""
    if pyautogui and hasattr(pyautogui, "record"):
        return pyautogui.record()
    try:
        from pynput import mouse, keyboard
    except Exception as e:  # pragma: no cover - optional dependency
        raise RuntimeError(f"pynput not available: {e}") from e

    events: list[dict] = []
    stop = keyboard.Events()

    def on_move(x, y):
        events.append({"type": "move", "x": x, "y": y, "t": time.time()})

    def on_click(x, y, button, pressed):
        events.append({
            "type": "click",
            "x": x,
            "y": y,
            "button": str(button),
            "pressed": pressed,
            "t": time.time(),
        })

    def on_scroll(x, y, dx, dy):
        events.append({
            "type": "scroll",
            "x": x,
            "y": y,
            "dx": dx,
            "dy": dy,
            "t": time.time(),
        })

    def on_press(key):
        if key == keyboard.Key.esc:
            return False
        events.append({"type": "key", "key": str(key), "down": True, "t": time.time()})

    def on_release(key):
        events.append({"type": "key", "key": str(key), "down": False, "t": time.time()})

    with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as ml, \
            keyboard.Listener(on_press=on_press, on_release=on_release) as kl:
        kl.join()
        ml.stop()
    return events


def play_events(events: list) -> None:
    """Replay recorded events using pyautogui."""
    if pyautogui is None:
        raise RuntimeError(f"pyautogui not available: {_IMPORT_ERROR}")
    if hasattr(pyautogui, "play"):
        pyautogui.play(events)
        return
    for ev in events:
        et = ev.get("type")
        if et == "move":
            pyautogui.moveTo(ev["x"], ev["y"])
        elif et == "click":
            button = ev.get("button", "left").replace("Button.", "")
            if ev.get("pressed", ev.get("down", True)):
                pyautogui.mouseDown(x=ev["x"], y=ev["y"], button=button)
            else:
                pyautogui.mouseUp(x=ev["x"], y=ev["y"], button=button)
        elif et == "scroll":
            pyautogui.scroll(ev.get("dy", 0), x=ev.get("x"), y=ev.get("y"))
        elif et == "write":
            pyautogui.write(ev.get("text", ""))
        elif et == "press" or et == "key":
            key = ev.get("key")
            if ev.get("pressed", ev.get("down", True)):
                pyautogui.keyDown(key)
            else:
                pyautogui.keyUp(key)



def record_macro(name: str) -> str:
    """Record keyboard and mouse events until ESC is pressed."""
    if _IMPORT_ERROR:
        return f"pyautogui not available: {_IMPORT_ERROR}"
    os.makedirs(MACRO_DIR, exist_ok=True)
    try:
        events = record_events()
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
        events = record_events()
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
        play_events(events)
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
            "record_events",
            "play_events",
            "record_macro",
            "play_macro",
            "list_macros",
            "record_macro_script",
        ],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Allows recording and playback of desktop macros taught by the user."


def register(registry=None):  # pragma: no cover - simple registration
    from module_manager import ModuleRegistry

    registry = registry or ModuleRegistry()
    registry.register(
        MODULE_NAME,
        {
            "record_events": record_events,
            "play_events": play_events,
            "record_macro": record_macro,
            "play_macro": play_macro,
            "list_macros": list_macros,
            "record_macro_script": record_macro_script,
            "get_info": get_info,
        },
    )

# register()
