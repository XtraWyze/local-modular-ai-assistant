# vision_tools.py
try:
    import pytesseract
    import pyautogui
    from screeninfo import get_monitors
    import cv2
    import numpy as np
    from PIL import Image
except Exception as e:  # pragma: no cover - optional dependencies
    pytesseract = None
    pyautogui = None
    get_monitors = lambda: []
    cv2 = None
    np = None
    Image = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None
import os
import sys

__all__ = [
    "screenshot",
    "find_on_screen",
    "analyze_image",
    "see_screen",
    "see_region",
    "click_image",
    "list_monitors",
]
from error_logger import log_error
from datetime import datetime

# Configure Tesseract only on Windows when available
if not _IMPORT_ERROR and sys.platform.startswith("win"):
    tesseract_cmd = os.environ.get(
        "TESSERACT_CMD", r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    )
    if os.path.exists(tesseract_cmd):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

def save_ocr_log(name: str, text: str) -> str:
    """Save OCR ``text`` to a timestamped file and return its path."""
    filename = f"ocr_log_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return f"OCR saved to {filename}"

def list_monitors():
    """Return available monitor geometry using screeninfo and total virtual size."""
    if _IMPORT_ERROR:
        return []
    monitors = get_monitors()
    virtual_width, virtual_height = pyautogui.size()
    return [
        {
            "index": i,
            "x": m.x,
            "y": m.y,
            "width": m.width,
            "height": m.height,
        }
        for i, m in enumerate(monitors)
    ] + [{"index": "virtual", "width": virtual_width, "height": virtual_height}]

def _get_monitor_region(index: int) -> tuple[int, int, int, int]:
    """Return ``(x, y, w, h)`` tuple for monitor ``index``."""
    monitors = get_monitors()
    if index < 0 or index >= len(monitors):
        raise IndexError(f"Monitor {index} not found")
    m = monitors[index]
    return (m.x, m.y, m.width, m.height)

def see_screen(monitor: int | None = None, log: bool = True):
    """Capture full screen or a monitor and return OCR text"""
    if _IMPORT_ERROR:
        return f"Missing dependency: {_IMPORT_ERROR}"
    region = None
    if monitor is not None:
        try:
            region = _get_monitor_region(monitor)
        except IndexError as e:
            return str(e)
    try:
        img = pyautogui.screenshot(region=region)
        text = pytesseract.image_to_string(img)
        if log:
            save_ocr_log("full" if monitor is None else f"monitor_{monitor}", text)
        try:
            from modules import debug_panel
            debug_panel.add_ocr_result(text.strip())
        except Exception:
            pass
        return f"Screen says:\n{text.strip()[:800] or 'No text found.'}"
    except Exception as e:  # pragma: no cover - safety net
        log_error(f"[vision_tools] see_screen failed: {e}")
        return f"Error capturing screen: {e}"

def see_region(x: int, y: int, w: int, h: int, monitor: int | None = None, log: bool = True):
    """Capture a region and OCR it. Coordinates are relative to the monitor if provided."""
    if _IMPORT_ERROR:
        return f"Missing dependency: {_IMPORT_ERROR}"
    if monitor is not None:
        try:
            mx, my, _, _ = _get_monitor_region(monitor)
            x += mx
            y += my
        except IndexError as e:
            return str(e)
    try:
        img = pyautogui.screenshot(region=(x, y, w, h))
        text = pytesseract.image_to_string(img)
        if log:
            label = (
                f"region_{x}_{y}" if monitor is None else f"monitor{monitor}_{x}_{y}"
            )
            save_ocr_log(label, text)
        try:
            from modules import debug_panel
            debug_panel.add_ocr_result(text.strip())
        except Exception:
            pass
        return f"Region ({x},{y},{w},{h}) says:\n{text.strip()[:800] or 'No text found.'}"
    except Exception as e:  # pragma: no cover - safety net
        log_error(f"[vision_tools] see_region failed: {e}")
        return f"Error capturing region: {e}"

def click_image(
    template_path: str,
    confidence: float = 0.8,
    monitor: int | None = None,
    region: tuple[int, int, int, int] | None = None,
) -> str:
    """Find an image on screen and click its center."""
    if _IMPORT_ERROR:
        return f"Missing dependency: {_IMPORT_ERROR}"
    if monitor is not None:
        try:
            region = _get_monitor_region(monitor)
        except IndexError as e:
            return str(e)
    try:
        screen = pyautogui.screenshot(region=region)
        screen_np = np.array(screen)
        screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            return f"Error: Could not load template image from {template_path}"

        res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= confidence)

        if loc[0].size > 0:
            y, x = loc[0][0], loc[1][0]
            h, w = template.shape
            pyautogui.click(x + w // 2, y + h // 2)
            return f"Clicked image match at ({x}, {y})"
        return "No matching image found."
    except Exception as e:  # pragma: no cover - handle pyautogui/cv2 errors
        log_error(f"[vision_tools] click_image failed: {e}")
        return f"Error clicking image: {e}"

def screenshot(path: str | None = None, monitor: int | None = None, region: tuple[int, int, int, int] | None = None):
    """Take a screenshot of the full screen, a monitor, or a region."""
    if _IMPORT_ERROR:
        return f"Missing dependency: {_IMPORT_ERROR}"
    if monitor is not None:
        try:
            region = _get_monitor_region(monitor)
        except IndexError as e:
            return str(e)
    try:
        img = pyautogui.screenshot(region=region)
        if path:
            img.save(path)
            return path
        return img
    except Exception as e:  # pragma: no cover
        log_error(f"[vision_tools] screenshot failed: {e}")
        return f"Error capturing screenshot: {e}"

def find_on_screen(
    template_path: str,
    confidence: float = 0.8,
    monitor: int | None = None,
    region: tuple[int, int, int, int] | None = None,
) -> tuple[int, int] | None:
    """Return coordinates of template on screen if found."""
    if _IMPORT_ERROR:
        return f"Missing dependency: {_IMPORT_ERROR}"
    if monitor is not None:
        try:
            region = _get_monitor_region(monitor)
        except IndexError as e:
            return str(e)
    loc = pyautogui.locateCenterOnScreen(template_path, confidence=confidence, region=region)
    if loc:
        return loc
    return None

def analyze_image(path: str):
    """Run OCR on an image from disk."""
    if _IMPORT_ERROR:
        return f"Missing dependency: {_IMPORT_ERROR}"
    if not os.path.exists(path):
        return f"File not found: {path}"
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        try:
            from modules import debug_panel
            debug_panel.add_ocr_result(text.strip())
        except Exception:
            pass
        return text.strip()[:800] or "No text found."
    except Exception as e:  # pragma: no cover
        log_error(f"[vision_tools] analyze_image failed: {e}")
        return f"Error analyzing image: {e}"
def get_info():
    return {
        "name": "vision_tools",
        "description": "Image and screen vision utilities.",
        "functions": [
            "screenshot",
            "find_on_screen",
            "analyze_image",
            "see_screen",
            "see_region",
            "click_image",
            "list_monitors",
        ],
    }


def get_description() -> str:
    """Return a short summary of this module."""
    return "Screen capture and computer vision helpers including OCR and template matching."
