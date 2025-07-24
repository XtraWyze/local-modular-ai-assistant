try:
    import pygetwindow as gw
    _IMPORT_ERROR = None
except Exception as e:  # pragma: no cover - optional dependency
    gw = None
    _IMPORT_ERROR = e
try:
    import pyautogui
except Exception as e:  # pragma: no cover - optional dependency
    pyautogui = None
    _PYAUTOGUI_ERROR = e
else:
    _PYAUTOGUI_ERROR = None
import time
import os
import platform
import subprocess
import ctypes
from ctypes import wintypes

__all__ = [
    "focus_window",
    "minimize_window",
    "list_windows",
    "move_window",
    "list_open_windows",
    "list_taskbar_windows",
    "close_taskbar_item",
    "click_ui_element",
    "learn_new_button",
]

def _windows_fallback() -> list[str]:
    """Fallback window title listing for Windows using ctypes."""
    titles: list[str] = []
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible

    def foreach(hwnd: wintypes.HWND, lParam: wintypes.LPARAM) -> bool:
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            title = buff.value
            if title:
                titles.append(title)
        return True

    EnumWindows(EnumWindowsProc(foreach), 0)
    return titles


def _wmctrl_fallback() -> list[str]:
    """Fallback window title listing using the ``wmctrl`` CLI."""
    try:
        output = subprocess.check_output(["wmctrl", "-lp"], text=True)
    except Exception:
        return []
    titles = []
    for line in output.splitlines():
        parts = line.split(None, 3)
        if len(parts) >= 4:
            title = parts[3].strip()
            if title:
                titles.append(title)
    return titles


def list_open_windows() -> list[str]:
    """Return titles of currently open windows."""
    if gw is not None and not _IMPORT_ERROR:
        return [w for w in gw.getAllTitles() if w.strip()]

    system = platform.system()
    if system == "Windows":
        return _windows_fallback()
    return _wmctrl_fallback()


def list_taskbar_windows():
    """Return titles of windows visible on the taskbar."""
    return list_open_windows()


def close_taskbar_item(index: int):
    """Robustly close the window at `index`."""
    if index < 0:
        return False, f"Invalid window index: {index}"
    if gw is None or _IMPORT_ERROR:
        return False, f"pygetwindow not available: {_IMPORT_ERROR}" if _IMPORT_ERROR else "pygetwindow not available"
    windows = [w for w in gw.getAllWindows() if w.title.strip()]
    if index >= len(windows):
        return False, f"Invalid window index: {index}"
    win = windows[index]

    # 1) Native close()
    try:
        win.activate()
        win.close()
        time.sleep(0.5)
        if win not in gw.getAllWindows():
            return True, f"Closed window '{win.title}'"
    except Exception:
        pass

    # 2) Alt+F4 fallback
    try:
        win.activate()
        pyautogui.hotkey('alt', 'f4')
        time.sleep(0.5)
        if win not in gw.getAllWindows():
            return True, f"Closed via Alt+F4 '{win.title}'"
    except Exception:
        pass

    # 3) OS kill as last resort
    try:
        title = win.title
        if platform.system() == 'Windows':
            subprocess.run(
                ['taskkill', '/FI', f'WINDOWTITLE eq {title}', '/T', '/F'],
                check=True
            )
        else:
            subprocess.run(['pkill', '-f', title], check=True)
        return True, f"Killed process for '{title}'"
    except Exception as e:
        return False, f"All close attempts failed for '{win.title}': {e}"

def focus_window(partial_title):
    """Bring the first window matching ``partial_title`` to the front."""
    if _IMPORT_ERROR:
        return False, f"pygetwindow not available: {_IMPORT_ERROR}"
    matches = [w for w in gw.getAllTitles() if partial_title.lower() in w.lower()]
    if not matches:
        return False, f"No window found containing '{partial_title}'"
    win = gw.getWindowsWithTitle(matches[0])[0]
    win.activate()
    time.sleep(0.5)
    return True, f"Activated window: {matches[0]}"

def move_window(title, x, y):
    """Move the first window matching title to (x, y)."""
    if _IMPORT_ERROR:
        return False, f"pygetwindow not available: {_IMPORT_ERROR}"
    matches = gw.getWindowsWithTitle(title)
    if not matches:
        return False, f"Window '{title}' not found"
    win = matches[0]
    win.moveTo(x, y)
    return True, f"Moved '{title}' to ({x}, {y})"

def minimize_window(partial_title: str):
    """Minimize the first window containing ``partial_title`` in its title."""
    if _IMPORT_ERROR:
        return False, f"pygetwindow not available: {_IMPORT_ERROR}"
    matches = [w for w in gw.getAllTitles() if partial_title.lower() in w.lower()]
    if not matches:
        return False, f"No window found containing '{partial_title}'"
    win = gw.getWindowsWithTitle(matches[0])[0]
    try:
        win.minimize()
        return True, f"Minimized window: {matches[0]}"
    except Exception as e:  # pragma: no cover - OS specific
        return False, f"Failed to minimize '{matches[0]}': {e}"

def list_windows():
    """Alias for list_open_windows for API consistency."""
    return list_open_windows()

def click_ui_element(image_path, confidence=0.8):
    """Try to locate and click a UI element; if not found, prompt to learn."""
    if _PYAUTOGUI_ERROR:
        return False, f"pyautogui not available: {_PYAUTOGUI_ERROR}"
    loc = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
    if loc:
        pyautogui.click(loc)
        return True, f"Clicked '{image_path}'"
    return False, f"Could not find '{image_path}' on screen"

def learn_new_button(app, action, speak):
    """Interactive: prompts user to capture a button template."""
    speak(f"Move your mouse over the {action} button in {app}, then press Enter.")
    input("Move your mouse over the button and press Enter...")
    if _PYAUTOGUI_ERROR:
        return False
    x, y = pyautogui.position()
    region = (x - 20, y - 20, 40, 40)
    screenshot = pyautogui.screenshot(region=region)
    folder = "button_images"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{app.lower()}_{action.lower()}.png")
    screenshot.save(filename)
    speak(f"Saved new template for {action} in {app}.")
    print(f"Saved as {filename}")
    return filename

def get_info():
    return {
        "name": "window_tools",
        "description": "Tools for interacting with and automating OS windows.",
        "functions": [
            "focus_window",
            "minimize_window",
            "list_windows",
            "move_window",
            "list_taskbar_windows",
            "close_taskbar_item",
        ]
    }


def get_description() -> str:
    """Return a short summary of this module."""
    return (
        "Utilities for listing taskbar windows, focusing them, moving or "
        "minimizing windows, and closing by index."
    )
