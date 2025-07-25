# utils.py

import os
import sys
import re
from pathlib import Path

__all__ = [
    "resource_path",
    "project_path",
    "clean_for_tts",
    "hide_cmd_window",
    "show_cmd_window",
]

def resource_path(relative_path: str) -> str:
    """Return absolute path for ``relative_path`` inside packaged app."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def project_path(*parts: str) -> str:
    """Return an absolute path within the project directory.

    This resolves paths relative to the repository root so modules can
    reliably access bundled data regardless of the current working
    directory.
    """
    root = Path(__file__).resolve().parents[1]
    return str(root.joinpath(*parts))


def clean_for_tts(text: str) -> str:
    """Remove unsupported characters for TTS output."""
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r'[®+/=]', '', text)
    text = re.sub(r'[^a-zA-Z0-9.,?!:"\'\- \n]', '', text)
    return text
def get_info():
    """Return metadata about this module for discovery."""
    return {
        "name": "utils",
        "description": "General utility functions used across the assistant.",
        # List the functions actually provided by this module
        "functions": [
            "resource_path",
            "project_path",
            "clean_for_tts",
            "hide_cmd_window",
            "show_cmd_window",
        ]
    }


def get_description() -> str:
    """Return a short summary of this module."""
    return "General helper utilities for file paths and text cleaning."


def hide_cmd_window() -> None:
    """Hide the console window on Windows, if present."""
    if sys.platform != "win32":
        return
    try:  # pragma: no cover - Windows only
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception as exc:  # pragma: no cover - optional failure
        print(f"[utils] Could not hide console: {exc}")


def show_cmd_window() -> None:
    """Show the console window on Windows, if present."""
    if sys.platform != "win32":
        return
    try:  # pragma: no cover - Windows only
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 1)
    except Exception as exc:  # pragma: no cover - optional failure
        print(f"[utils] Could not show console: {exc}")
