# modules/pyautogui_tools.py

try:
    import pyautogui
except Exception as e:  # pragma: no cover - optional dependency
    pyautogui = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None
from error_logger import log_error

MODULE_NAME = "pyautogui_tools"

__all__ = [
    "click",
    "move",
    "type_text",
    "press",
    "screenshot",
    "locate_on_screen",
    "get_mouse_position",
]

def click(x=None, y=None, clicks=1, interval=0.1, button='left'):
    """Click at the specified position, or current mouse position if not specified."""
    if _IMPORT_ERROR:
        return f"pyautogui not available: {_IMPORT_ERROR}"
    try:
        pyautogui.click(x=x, y=y, clicks=clicks, interval=interval, button=button)
        return f"Clicked at ({x}, {y}) with button {button}."
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Click error: {e}")
        return f"[pyautogui_tools Error] {str(e)}"

def move(x, y, duration=0.2):
    """Move mouse to (x, y) over a given duration."""
    if _IMPORT_ERROR:
        return f"pyautogui not available: {_IMPORT_ERROR}"
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return f"Moved mouse to ({x}, {y})."
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Move error: {e}")
        return f"[pyautogui_tools Error] {str(e)}"

def type_text(text, interval=0.05):
    """Type text at the current cursor position."""
    if _IMPORT_ERROR:
        return f"pyautogui not available: {_IMPORT_ERROR}"
    try:
        pyautogui.write(text, interval=interval)
        return f"Typed: {text}"
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Type error: {e}")
        return f"[pyautogui_tools Error] {str(e)}"

def press(key):
    """Press a single key."""
    if _IMPORT_ERROR:
        return f"pyautogui not available: {_IMPORT_ERROR}"
    try:
        pyautogui.press(key)
        return f"Pressed key: {key}"
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Press key error: {e}")
        return f"[pyautogui_tools Error] {str(e)}"

def screenshot(region=None, path=None):
    """
    Take a screenshot of the full screen or a region.
    region: (left, top, width, height)
    path: if provided, saves the screenshot to this file
    Returns: PIL Image object or path to file.
    """
    if _IMPORT_ERROR:
        return f"pyautogui not available: {_IMPORT_ERROR}"
    try:
        img = pyautogui.screenshot(region=region)
        if path:
            img.save(path)
            return f"Screenshot saved to {path}"
        return img
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Screenshot error: {e}")
        return f"[pyautogui_tools Error] {str(e)}"

def locate_on_screen(image, region=None, confidence=0.8):
    """
    Locate an image on the screen.
    Returns (x, y, width, height) if found, else None.
    """
    if _IMPORT_ERROR:
        return f"pyautogui not available: {_IMPORT_ERROR}"
    try:
        box = pyautogui.locateOnScreen(image, region=region, confidence=confidence)
        if box:
            return tuple(box)
        return None
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Locate image error: {e}")
        return f"[pyautogui_tools Error] {str(e)}"

def get_mouse_position():
    """Get the current mouse cursor position as (x, y)."""
    if _IMPORT_ERROR:
        return (0, 0)
    try:
        pos = pyautogui.position()
        return (pos.x, pos.y)
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Mouse position error: {e}")
        return f"[pyautogui_tools Error] {str(e)}"

def get_info():
    """
    Return a description of this module for registry purposes.
    """
    return {
        "name": MODULE_NAME,
        "description": "Screen automation tools using pyautogui: mouse, keyboard, screenshot, and image location.",
        "functions": [
            "click", "move", "type_text", "press",
            "screenshot", "locate_on_screen", "get_mouse_position"
        ]
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Low-level screen automation using pyautogui for clicking, typing and screenshots."

# --- Plugin Registration ---
def register():
    """
    Register this module's functions with the assistant's plugin system.
    """
    from module_manager import ModuleRegistry
    ModuleRegistry.register(MODULE_NAME, {
        "click": click,
        "move": move,
        "type_text": type_text,
        "press": press,
        "screenshot": screenshot,
        "locate_on_screen": locate_on_screen,
        "get_mouse_position": get_mouse_position,
        "get_info": get_info
    })

# Uncomment if you want auto-registration:
# register()
