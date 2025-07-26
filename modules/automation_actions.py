# automation_actions.py
"""GUI automation helpers for dragging, window resizing and clipboard management."""

try:
    import pyautogui
except Exception as e:  # pragma: no cover - optional dependency
    pyautogui = None
    _PYAUTOGUI_ERROR = e
else:
    _PYAUTOGUI_ERROR = None
try:
    import pyperclip
except Exception as e:  # pragma: no cover - optional dependency
    pyperclip = None
    _PYPERCLIP_ERROR = e
else:
    _PYPERCLIP_ERROR = None

try:
    import pygetwindow as gw
    _GW_ERROR = None
except Exception as e:
    gw = None
    _GW_ERROR = e

__all__ = [
    "drag_drop",
    "resize_window",
    "copy_to_clipboard",
    "get_clipboard",
]

from error_logger import log_error

MODULE_NAME = "automation_actions"


def drag_drop(x1: int, y1: int, x2: int, y2: int, duration: float = 0.2) -> str:
    """Drag the mouse from (x1, y1) to (x2, y2)."""
    if _PYAUTOGUI_ERROR:
        return f"pyautogui not available: {_PYAUTOGUI_ERROR}"
    try:
        pyautogui.moveTo(x1, y1)
        pyautogui.dragTo(x2, y2, duration=duration)
        return f"Dragged from ({x1},{y1}) to ({x2},{y2})"
    except Exception as e:
        log_error(f"[{MODULE_NAME}] drag_drop error: {e}")
        return f"Error dragging: {e}"


def resize_window(title: str, width: int, height: int) -> str:
    """Resize the first window matching title."""
    if _GW_ERROR:
        return f"pygetwindow not available: {_GW_ERROR}"
    try:
        matches = gw.getWindowsWithTitle(title)
        if not matches:
            return f"Window '{title}' not found"
        win = matches[0]
        win.resizeTo(width, height)
        return f"Resized '{title}' to {width}x{height}"
    except Exception as e:
        log_error(f"[{MODULE_NAME}] resize_window error: {e}")
        return f"Error resizing window: {e}"


def copy_to_clipboard(text: str) -> str:
    """Copy text to the system clipboard."""
    if _PYPERCLIP_ERROR:
        return f"pyperclip not available: {_PYPERCLIP_ERROR}"
    try:
        pyperclip.copy(text)
        return "Text copied to clipboard"
    except Exception as e:
        log_error(f"[{MODULE_NAME}] copy_to_clipboard error: {e}")
        return f"Error copying to clipboard: {e}"


def get_clipboard() -> str:
    """Return current text from the clipboard."""
    if _PYPERCLIP_ERROR:
        return f"pyperclip not available: {_PYPERCLIP_ERROR}"
    try:
        return pyperclip.paste()
    except Exception as e:
        log_error(f"[{MODULE_NAME}] get_clipboard error: {e}")
        return f"Error reading clipboard: {e}"


def get_info():
    return {
        "name": MODULE_NAME,
        "description": "Automation helpers for drag/drop, window resizing and clipboard.",
        "functions": [
            "drag_drop",
            "resize_window",
            "copy_to_clipboard",
            "get_clipboard",
        ],
    }


def get_description() -> str:
    """Return a short summary of this module."""
    return "Provides drag-drop, window resize and clipboard utilities via pyautogui."


def register(registry=None):
    """Register this module with ``ModuleRegistry``."""
    from module_manager import ModuleRegistry

    registry = registry or ModuleRegistry()
    registry.register(
        MODULE_NAME,
        {
            "drag_drop": drag_drop,
            "resize_window": resize_window,
            "copy_to_clipboard": copy_to_clipboard,
            "get_clipboard": get_clipboard,
            "get_info": get_info,
        },
    )

# register()  # Optional auto-registration
