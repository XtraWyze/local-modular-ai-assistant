"""Display a screenshot overlay for each step in a recorded macro."""

import os
import json

try:
    import tkinter as tk
    from PIL import Image, ImageTk, ImageDraw
    import pyautogui
except Exception as e:  # pragma: no cover - optional deps
    tk = None
    Image = None
    ImageTk = None
    ImageDraw = None
    pyautogui = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

from error_logger import log_error

MACRO_DIR = "macros"
MODULE_NAME = "overlay_preview"

__all__ = ["preview_macro"]


def preview_macro(name: str) -> str:
    """Show an overlay preview of ``name`` macro steps."""
    if _IMPORT_ERROR:
        return f"Missing dependency: {_IMPORT_ERROR}"
    path = os.path.join(MACRO_DIR, f"{name}.json")
    if not os.path.isfile(path):
        return f"Macro '{name}' not found"
    try:
        with open(path, "r", encoding="utf-8") as f:
            events = json.load(f)
    except Exception as e:
        log_error(f"[{MODULE_NAME}] load error: {e}")
        return f"Error loading macro: {e}"
    if tk is None:
        return "Tkinter not available"
    win = tk.Tk()
    win.title(f"Preview {name}")
    label = tk.Label(win)
    label.pack()
    info_var = tk.StringVar()
    tk.Label(win, textvariable=info_var).pack()

    idx = 0

    def show(idx: int):
        screenshot = pyautogui.screenshot()
        draw = ImageDraw.Draw(screenshot)
        event = events[idx]
        if "x" in event and "y" in event:
            r = 10
            draw.rectangle((event["x"] - r, event["y"] - r, event["x"] + r, event["y"] + r), outline="red", width=3)
        photo = ImageTk.PhotoImage(screenshot)
        label.configure(image=photo)
        label.image = photo
        info_var.set(f"Step {idx + 1}/{len(events)}: {event.get('type')}")

    def next_step():
        nonlocal idx
        idx += 1
        if idx >= len(events):
            win.destroy()
            return
        show(idx)

    tk.Button(win, text="Next", command=next_step).pack()
    show(idx)
    win.mainloop()
    return "Preview complete"


def get_description() -> str:
    return "Show screenshot overlays to verify recorded macro steps."
