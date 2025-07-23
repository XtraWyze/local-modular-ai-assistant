try:
    import pytesseract
    import pyautogui
    import requests
    from schedule import every
    from PIL import Image
    import cv2
    import numpy as np
except Exception as e:  # pragma: no cover - optional dependencies
    pytesseract = None
    pyautogui = None
    requests = None
    every = lambda *a, **k: None
    Image = None
    cv2 = None
    np = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None
import os
import sys
import subprocess
import shutil
from io import StringIO
import contextlib
from datetime import datetime
from .automation_actions import (
    drag_drop,
    resize_window,
    copy_to_clipboard,
    get_clipboard,
)
try:
    from .audio_tools import transcribe_speaker, detect_sound
except Exception:  # pragma: no cover - optional optional dependencies
    def transcribe_speaker(duration: int = 5) -> str:  # pragma: no cover - fallback
        """Attempt basic speaker transcription if deps are installed."""
        try:
            import sounddevice as _sd
            import numpy as _np
            import speech_recognition as sr
        except Exception:
            return ""
        try:
            rec = _sd.rec(int(duration * 16000), samplerate=16000, channels=1, dtype="int16")
            _sd.wait()
            audio = sr.AudioData(rec.tobytes(), 16000, 2)
            return sr.Recognizer().recognize_google(audio)
        except Exception:
            return ""

    def detect_sound(threshold: int = 500, duration: int = 2) -> bool:  # pragma: no cover
        try:
            import sounddevice as _sd
            import numpy as _np
        except Exception:
            return False
        try:
            rec = _sd.rec(int(duration * 16000), samplerate=16000, channels=1, dtype="int16")
            _sd.wait()
            arr = _np.frombuffer(rec.tobytes(), dtype=_np.int16)
            rms = _np.sqrt(_np.mean(arr.astype(_np.float32) ** 2))
            return rms > threshold
        except Exception:
            return False

# ========== OCR & IMAGE TOOLS ==========

if not _IMPORT_ERROR and sys.platform.startswith("win"):
    tesseract_cmd = os.environ.get(
        "TESSERACT_CMD", r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    )
    if os.path.exists(tesseract_cmd):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

def save_ocr_log(name: str, text: str) -> None:
    """Write OCR output ``text`` to a timestamped log file."""
    filename = f"ocr_log_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def see_screen():
    """Capture screen and extract text using OCR"""
    if _IMPORT_ERROR:
        return f"Dependency missing: {_IMPORT_ERROR}"
    screenshot = pyautogui.screenshot()
    text = pytesseract.image_to_string(screenshot)
    save_ocr_log("full", text)
    return f"Screen says:\n{text.strip()[:800] or 'No text found.'}"

def see_region(x: int, y: int, w: int, h: int):
    """Capture a screen region and extract text using OCR"""
    if _IMPORT_ERROR:
        return f"Dependency missing: {_IMPORT_ERROR}"
    region_img = pyautogui.screenshot(region=(x, y, w, h))
    text = pytesseract.image_to_string(region_img)
    save_ocr_log(f"region_{x}_{y}", text)
    return f"Region ({x},{y},{w},{h}) says:\n{text.strip()[:800] or 'No text found.'}"

def click_image(template_path: str, confidence=0.8):
    """Find template image on screen and click it if found"""
    if _IMPORT_ERROR:
        return f"Dependency missing: {_IMPORT_ERROR}"
    screen = pyautogui.screenshot()
    screen_np = np.array(screen)
    screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= confidence)
    if loc[0].size > 0:
        y, x = loc[0][0], loc[1][0]
        pyautogui.click(x + template.shape[1] // 2, y + template.shape[0] // 2)
        return f"Clicked image match at ({x}, {y})"
    else:
        return "No matching image found."

# ========== APP SHORTCUTS ==========

APP_ALIASES = {
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "explorer": r"C:\Windows\explorer.exe",
    "notepad": r"C:\Windows\System32\notepad.exe"
}

# ========== SYSTEM/INPUT TOOLS ==========

def open_app(name_or_path):
    """Launch an application or file.

    ``name_or_path`` may be a friendly name defined in :data:`APP_ALIASES`
    (e.g. ``"notepad"``) or a direct executable/file path.  The function
    simply calls :func:`os.startfile` on the resolved path and returns a
    confirmation string.
    """
    path = APP_ALIASES.get(name_or_path.lower(), name_or_path)
    os.startfile(path)
    return f"Opened {path}"

def close_app(name: str):
    """Close a window or process matching ``name``.

    The function first attempts to find a window whose title contains
    ``name`` using ``pyautogui.getWindowsWithTitle``.  If found, the most
    recently returned window is closed.  If no matching window exists,
    a process with that name is terminated (``taskkill``/``pkill``).
    """

    # Try window-based closing if pyautogui is available
    if pyautogui and hasattr(pyautogui, "getWindowsWithTitle"):
        try:
            matches = pyautogui.getWindowsWithTitle(name)
        except Exception:
            matches = []
        if matches:
            win = matches[-1]
            try:
                win.activate()
            except Exception:
                pass
            try:
                win.close()
                return f"Closed window '{win.title}'"
            except Exception as e:  # pragma: no cover - OS specific
                return f"Failed to close window '{win.title}': {e}"

    # Fallback to killing by process name
    if sys.platform.startswith("win"):
        subprocess.run(f"taskkill /IM {name}.exe /F", shell=True)
    else:
        subprocess.run(["pkill", "-f", name])
    return f"Closed process {name}"

def click_at(x: int, y: int):
    """Click the mouse at screen coordinates ``(x, y)``."""
    if _IMPORT_ERROR:
        return f"Dependency missing: {_IMPORT_ERROR}"
    pyautogui.click(x, y)
    return f"Clicked at ({x},{y})"

def type_text(text: str):
    """Type ``text`` using the keyboard at the current cursor."""
    if _IMPORT_ERROR:
        return f"Dependency missing: {_IMPORT_ERROR}"
    pyautogui.write(text, interval=0.05)
    return f"Typed: {text}"

def copy_file(src: str, dst: str):
    """Copy ``src`` to ``dst`` preserving metadata."""
    shutil.copy2(src, dst)
    return f"Copied {src} → {dst}"

def move_file(src: str, dst: str):
    """Move ``src`` to ``dst``."""
    shutil.move(src, dst)
    return f"Moved {src} → {dst}"

# ========== UTILITY FUNCTIONS ==========

_REMINDERS = []
def schedule_reminder(msg: str, at_time: str):
    """Schedule a daily reminder using ``schedule``."""
    if _IMPORT_ERROR:
        return f"Dependency missing: {_IMPORT_ERROR}"
    def job():
        print(f"[Reminder] {msg}")
    every().day.at(at_time).do(job)
    _REMINDERS.append((msg, at_time))
    return f"Reminder set @ {at_time}: {msg}"

def fetch_url(url: str):
    """Return up to the first 500 characters of ``url`` using ``requests``."""
    if _IMPORT_ERROR or requests is None:
        return f"Dependency missing: {_IMPORT_ERROR}"
    resp = requests.get(url)
    return resp.text[:500]

def run_python(code: str):
    """Execute arbitrary Python code. **Use with caution.**"""
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        exec(code, {})
    output = buf.getvalue().strip()
    return output or "Executed Python code."

# Additional helper functions referenced by get_info
def random_string(length: int = 8) -> str:
    """Return a random alphanumeric string."""
    import random
    import string
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def timestamp(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Return the current timestamp formatted as a string."""
    return datetime.now().strftime(fmt)

def parse_args(text: str) -> list[str]:
    """Very small helper to split command-like text into arguments."""
    return text.split()

# ========== EXPORTS ==========

__all__ = [
    "open_app", "close_app", "click_at", "type_text",
    "copy_file", "move_file", "schedule_reminder",
    "fetch_url", "run_python", "see_screen",
    "see_region", "click_image",
    "drag_drop", "resize_window",
    "copy_to_clipboard", "get_clipboard",
    "transcribe_speaker", "detect_sound"
]
def get_info():
    return {
        "name": "tools",
        "description": "Miscellaneous helper functions.",
        "functions": ["random_string", "timestamp", "parse_args"]
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Collection of helper utilities for OCR, system commands and scheduling."
