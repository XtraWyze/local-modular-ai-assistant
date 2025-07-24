"""Attempt to save then close a window using multiple strategies."""

from __future__ import annotations

import subprocess
import platform
import time

try:
    import pygetwindow as gw
    import pyautogui
except Exception as e:  # pragma: no cover - optional dependency
    gw = None
    pyautogui = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

__all__ = ["save_and_exit", "get_description"]


def _find_window(title: str):
    """Return the first window matching ``title`` or ``None``."""
    if gw is None or _IMPORT_ERROR:
        return None
    matches = gw.getWindowsWithTitle(title)
    return matches[0] if matches else None


def _send_hotkey(*keys):
    """Send a hotkey if pyautogui is available."""
    if pyautogui:
        try:
            pyautogui.hotkey(*keys)
            time.sleep(0.3)
        except Exception:
            pass


def _kill_process_for_window(win) -> bool:
    """Kill the process owning ``win``."""
    try:
        title = win.title
        if platform.system() == "Windows":
            subprocess.run([
                "taskkill",
                "/FI",
                f"WINDOWTITLE eq {title}",
                "/T",
                "/F",
            ], check=True)
        else:
            subprocess.run(["pkill", "-f", title], check=True)
        return True
    except Exception:
        return False


def save_and_exit(title: str) -> str:
    """Attempt to save and then close the window ``title``.

    Five saving strategies are attempted before giving up. After the save
    attempts, three close strategies try to close the same window.

    Parameters
    ----------
    title:
        Partial title of the target window.

    Returns
    -------
    str
        Message describing the outcome.
    """

    if _IMPORT_ERROR:
        return f"Missing dependency: {_IMPORT_ERROR}"

    win = _find_window(title)
    if win is None:
        return f"Window '{title}' not found"

    win.activate()
    save_attempts = [
        lambda: _send_hotkey("ctrl", "s"),
        lambda: _send_hotkey("ctrl", "shift", "s"),
        lambda: (_send_hotkey("alt", "f"), _send_hotkey("s")),
        lambda: (_send_hotkey("alt", "f"), _send_hotkey("a"), _send_hotkey("enter")),
        lambda: _send_hotkey("ctrl", "s"),
    ]
    for attempt in save_attempts:
        attempt()
        time.sleep(0.2)
    close_attempts = [
        lambda: getattr(win, "close", lambda: None)(),
        lambda: _send_hotkey("alt", "f4"),
        lambda: _kill_process_for_window(win),
    ]
    for attempt in close_attempts:
        attempt()
        time.sleep(0.3)
        if win not in gw.getAllWindows():
            return f"Saved and closed '{win.title}'"
    return f"Save attempts done; window may still be open"


def get_description() -> str:
    """Return a short summary of this module."""
    return "Save a window using common shortcuts then close it robustly."
