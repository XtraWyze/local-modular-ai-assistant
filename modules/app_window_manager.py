"""app_window_manager.py

Unified window management utilities for controlling open application windows.

This module centralizes window interaction logic using ``pygetwindow`` and
optionally ``pywinauto``. It exposes helper functions to list, focus, resize and
close windows and keeps a JSON file mapping applications to custom workflows.

These utilities are designed for the assistant to trigger window operations or
learn new app-specific actions. On Windows, process names are returned for open
windows when ``pywin32`` and ``psutil`` are available.
"""
from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import time
import platform

# Optional dependencies ------------------------------------------------------
try:
    import pygetwindow as gw
except Exception as e:  # pragma: no cover - optional dependency
    gw = None
    _GW_ERROR = e
else:  # pragma: no cover - optional dependency
    _GW_ERROR = None

try:
    import pyautogui
except Exception as e:  # pragma: no cover - optional dependency
    pyautogui = None
    _PYAUTOGUI_ERROR = e
else:  # pragma: no cover - optional dependency
    _PYAUTOGUI_ERROR = None

try:  # for retrieving process names on Windows
    import psutil
    import win32process
except Exception as e:  # pragma: no cover - optional dependency
    psutil = None
    win32process = None
    _WIN32_ERROR = e
else:
    _WIN32_ERROR = None

try:  # optional for UI element access
    from pywinauto import Application
except Exception as e:  # pragma: no cover - optional dependency
    Application = None
    _PYWINAUTO_ERROR = e
else:
    _PYWINAUTO_ERROR = None

# Key combinations for common window actions
if platform.system() == "Darwin":
    _ALT_TAB_KEYS = ("command", "tab")
    _MAXIMIZE_HOTKEY = ("command", "ctrl", "f")
else:
    _ALT_TAB_KEYS = ("alt", "tab")
    _MAXIMIZE_HOTKEY = ("alt", "space", "x")


# ---------------------------------------------------------------------------
# Previous implementations lived across ``window_tools`` and
# ``automation_actions``. The logic has been consolidated here so the
# assistant can rely on a single window management API. These modules still
# expose thin wrappers for backwards compatibility, but the real logic now
# resides in this file.

MODULE_NAME = "app_window_manager"

__all__ = [
    "get_open_windows",
    "open_application",
    "close_window",
    "minimize_window",
    "maximize_window",
    "resize_window",
    "focus_window",
    "register_workflow",
    "handle_app_logic",
]

# Path where workflows are stored
_WORKFLOWS_FILE = Path(__file__).resolve().with_name("app_workflows.json")


# Workflow storage ----------------------------------------------------------

def _load_workflows() -> dict[str, list[dict]]:
    if _WORKFLOWS_FILE.exists():
        try:
            with _WORKFLOWS_FILE.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}
    return {}


def _save_workflows(data: dict[str, list[dict]]) -> None:
    try:
        with _WORKFLOWS_FILE.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
    except Exception:
        pass


APP_WORKFLOWS: dict[str, list[dict]] = _load_workflows()


# Helper functions ----------------------------------------------------------

def get_open_windows() -> list[dict[str, str | None]]:
    """Return a list of dictionaries with ``title`` and optional ``process``."""
    if gw is None or _GW_ERROR:
        return []

    windows: list[dict[str, str | None]] = []
    for win in gw.getAllWindows():
        title = getattr(win, "title", "").strip()
        if not title:
            continue
        proc = None
        if os.name == "nt" and win32process is not None and hasattr(win, "_hWnd"):
            try:
                _, pid = win32process.GetWindowThreadProcessId(int(win._hWnd))
                proc = psutil.Process(pid).name() if psutil else None
            except Exception:  # pragma: no cover - OS specific
                proc = None
        windows.append({"title": title, "process": proc})
    return windows


def open_application(command: str) -> tuple[bool, str]:
    """Launch an application or open a file."""
    try:
        if os.name == "nt":
            if os.path.exists(command):
                os.startfile(command)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(command)
        else:
            subprocess.Popen(command.split())
        return True, f"Opened {command}"
    except Exception as e:  # pragma: no cover - platform specific
        return False, f"Failed to open {command}: {e}"


def close_window(partial_title: str) -> tuple[bool, str]:
    """Close the first window containing ``partial_title``."""
    if gw is None or _GW_ERROR:
        return False, f"pygetwindow not available: {_GW_ERROR}" if _GW_ERROR else "pygetwindow not available"

    matches = [w for w in gw.getAllTitles() if partial_title.lower() in w.lower()]
    if not matches:
        return False, f"No window found containing '{partial_title}'"
    win = gw.getWindowsWithTitle(matches[0])[0]

    try:
        win.activate()
        win.close()
        time.sleep(0.5)
        if win not in gw.getAllWindows():
            return True, f"Closed window: {matches[0]}"
    except Exception:
        pass

    if pyautogui is not None:
        try:
            win.activate()
            pyautogui.hotkey("alt", "f4")
            return True, f"Closed window via Alt+F4: {matches[0]}"
        except Exception:
            pass

    return False, f"Failed to close '{matches[0]}'"


# Window manipulation implementations ---------------------------------------

def focus_window(partial_title: str) -> tuple[bool, str]:
    """Bring the first window matching ``partial_title`` to the foreground."""
    if gw is None or _GW_ERROR:
        return False, f"pygetwindow not available: {_GW_ERROR}"
    try:
        matches = [w for w in gw.getAllTitles() if partial_title.lower() in w.lower()]
    except Exception:
        matches = []
    if matches:
        win = gw.getWindowsWithTitle(matches[0])[0]
        try:
            win.activate()
            time.sleep(0.5)
            return True, f"Activated window: {matches[0]}"
        except Exception:
            pass

    if _PYAUTOGUI_ERROR:
        return False, f"No window found containing '{partial_title}'"

    for _ in range(10):
        try:
            pyautogui.hotkey(*_ALT_TAB_KEYS)
            time.sleep(0.2)
            active = None
            try:
                active = gw.getActiveWindow()
            except Exception:
                pass
            if active and partial_title.lower() in active.title.lower():
                return True, f"Activated window via Alt+Tab: {active.title}"
        except Exception:
            break

    return False, f"No window found containing '{partial_title}'"


def minimize_window(partial_title: str) -> tuple[bool, str]:
    """Minimize the first window containing ``partial_title``."""
    if gw is None or _GW_ERROR:
        return False, f"pygetwindow not available: {_GW_ERROR}"
    matches = [w for w in gw.getAllTitles() if partial_title.lower() in w.lower()]
    if not matches:
        return False, f"No window found containing '{partial_title}'"
    win = gw.getWindowsWithTitle(matches[0])[0]
    try:
        win.minimize()
        return True, f"Minimized window: {matches[0]}"
    except Exception as e:
        return False, f"Failed to minimize '{matches[0]}': {e}"


def maximize_window(partial_title: str) -> tuple[bool, str]:
    """Maximize the first window containing ``partial_title``."""
    if gw is None or _GW_ERROR:
        return False, f"pygetwindow not available: {_GW_ERROR}"
    ok, msg = focus_window(partial_title)
    if not ok:
        return False, msg
    win = gw.getActiveWindow()
    if not win:
        return False, f"Could not activate '{partial_title}'"
    try:
        if hasattr(win, "maximize"):
            win.maximize()
            return True, f"Maximized window: {win.title}"
    except Exception:
        pass
    if _PYAUTOGUI_ERROR:
        return False, f"Failed to maximize '{win.title}'"
    try:
        if _MAXIMIZE_HOTKEY == ("alt", "space", "x"):
            pyautogui.hotkey("alt", "space")
            time.sleep(0.1)
            pyautogui.press("x")
        elif _MAXIMIZE_HOTKEY == ("command", "ctrl", "f"):
            pyautogui.hotkey("command", "ctrl", "f")
        else:
            pyautogui.press("f11")
        return True, f"Maximized window via hotkey: {win.title}"
    except Exception as e:
        return False, f"Failed to maximize '{win.title}': {e}"


def resize_window(title: str, width: int, height: int) -> str:
    """Resize the first window matching ``title``."""
    if gw is None or _GW_ERROR:
        return f"pygetwindow not available: {_GW_ERROR}"
    try:
        matches = gw.getWindowsWithTitle(title)
        if not matches:
            return f"Window '{title}' not found"
        win = matches[0]
        win.resizeTo(width, height)
        return f"Resized '{title}' to {width}x{height}"
    except Exception as e:
        return f"Error resizing window: {e}"


# Workflow helpers ---------------------------------------------------------

def register_workflow(app_name: str, actions: list[dict]) -> None:
    """Register and persist a workflow for ``app_name``."""
    APP_WORKFLOWS[app_name.lower()] = actions
    _save_workflows(APP_WORKFLOWS)


_FUNCTION_MAP = {
    "focus_window": focus_window,
    "minimize_window": minimize_window,
    "maximize_window": maximize_window,
    "close_window": close_window,
    "resize_window": resize_window,
    "open_application": open_application,
}


def handle_app_logic(app_name: str) -> str:
    """Execute stored workflow actions for ``app_name`` if present."""
    workflow = APP_WORKFLOWS.get(app_name.lower())
    if not workflow:
        return f"No workflow for {app_name}"

    messages = []
    for step in workflow:
        action = step.get("action")
        args = step.get("args", [])
        func = _FUNCTION_MAP.get(action)
        if func:
            result = func(*args)
            if isinstance(result, tuple):
                ok, msg = result
                messages.append(msg if ok else msg)
            else:
                messages.append(str(result))
    return "; ".join(messages)


# Metadata -----------------------------------------------------------------

def get_info():
    return {
        "name": MODULE_NAME,
        "description": "Unified window management and app-specific workflows.",
        "functions": list(__all__),
    }


def get_description() -> str:
    """Return a short summary of this module."""
    return (
        "Manage application windows (list, focus, resize, open, close) and"
        " execute stored workflows for known apps."
    )


def register(registry=None):
    """Register this module with ``ModuleRegistry``."""
    from module_manager import ModuleRegistry

    registry = registry or ModuleRegistry()
    registry.register(
        MODULE_NAME,
        {
            "get_open_windows": get_open_windows,
            "open_application": open_application,
            "close_window": close_window,
            "minimize_window": minimize_window,
            "maximize_window": maximize_window,
            "resize_window": resize_window,
            "focus_window": focus_window,
            "register_workflow": register_workflow,
            "handle_app_logic": handle_app_logic,
            "get_info": get_info,
        },
    )

# register()
