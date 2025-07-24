"""Automated save and exit functionality for application windows."""

from __future__ import annotations

import platform
import subprocess
import time

try:
    import pygetwindow as gw
    _GW_ERROR = None
except Exception as e:  # pragma: no cover - optional dependency
    gw = None
    _GW_ERROR = e

try:
    import pyautogui
    _PYAUTOGUI_ERROR = None
except Exception as e:  # pragma: no cover - optional dependency
    pyautogui = None
    _PYAUTOGUI_ERROR = e

from error_logger import log_error

__all__ = ["save_and_exit", "get_info", "get_description"]

MODULE_NAME = "save_exit"


def _find_window(title: str):
    """Return the first window containing ``title`` or ``None``."""
    if gw is None or _GW_ERROR:
        return None
    matches = [w for w in gw.getAllWindows() if title.lower() in w.title.lower()]
    return matches[0] if matches else None


def _close_window(win) -> tuple[bool, str]:
    """Attempt to close ``win`` using three strategies."""
    try:
        win.activate()
        time.sleep(0.2)
    except Exception:
        pass

    # 1) Native close()
    try:
        win.close()
        time.sleep(0.5)
        if win not in gw.getAllWindows():
            return True, f"Closed window '{win.title}'"
    except Exception:
        pass

    # 2) Alt+F4 fallback
    try:
        win.activate()
        if pyautogui:
            pyautogui.hotkey("alt", "f4")
            time.sleep(0.5)
            if win not in gw.getAllWindows():
                return True, f"Closed window '{win.title}' via Alt+F4"
    except Exception:
        pass

    # 3) OS kill as last resort
    try:
        title = win.title
        if platform.system() == "Windows":
            subprocess.run(
                ["taskkill", "/FI", f"WINDOWTITLE eq {title}", "/T", "/F"],
                check=True,
            )
        else:
            subprocess.run(["pkill", "-f", title], check=True)
        return True, f"Killed process for '{title}'"
    except Exception as e:
        return False, f"All close attempts failed for '{win.title}': {e}"


def save_and_exit(window_title: str) -> str:
    """Save and close the window matching ``window_title``."""
    if _GW_ERROR:
        return f"pygetwindow not available: {_GW_ERROR}"
    if _PYAUTOGUI_ERROR:
        return f"pyautogui not available: {_PYAUTOGUI_ERROR}"

    win = _find_window(window_title)
    if not win:
        return f"Window '{window_title}' not found"

    try:
        win.activate()
    except Exception:
        pass
    time.sleep(0.3)

    save_steps = [
        lambda: pyautogui.hotkey("ctrl", "s"),
        lambda: (pyautogui.hotkey("alt", "f"), pyautogui.press("s")),
        lambda: (pyautogui.hotkey("ctrl", "shift", "s"), pyautogui.press("enter")),
        lambda: (pyautogui.press("f10"), pyautogui.press("s")),
        lambda: (pyautogui.press("f10"), pyautogui.press("a"), pyautogui.press("enter")),
    ]

    saved = False
    for step in save_steps:
        try:
            step()
            time.sleep(0.4)
            saved = True
            break
        except Exception as e:  # pragma: no cover - log errors
            log_error(f"[{MODULE_NAME}] save attempt failed: {e}")

    close_success, close_msg = _close_window(win)
    status = "Saved" if saved else "Attempted to save"
    return f"{status}; {close_msg}"


def get_info() -> dict:
    return {
        "name": MODULE_NAME,
        "description": "Try multiple strategies to save a window then close it.",
        "functions": ["save_and_exit"],
    }


def get_description() -> str:
    """Return a short summary of this module."""
    return "Save the given window using several hotkeys and then close it."
