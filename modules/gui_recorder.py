"""Simple GUI for recording and playing automation macros."""

try:
    import tkinter as tk
    from tkinter import messagebox
    import pyautogui
except Exception as e:  # pragma: no cover - optional deps
    tk = None
    pyautogui = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

MACRO_DIR = "macros"
MODULE_NAME = "gui_recorder"

__all__ = ["record_gui", "play_gui", "open_recorder_window"]


def record_gui(name: str) -> str:
    """Record actions until ESC is pressed and save to a JSON file."""
    if _IMPORT_ERROR:
        return f"pyautogui not available: {_IMPORT_ERROR}"
    events = pyautogui.record()
    import json
    import os
    os.makedirs(MACRO_DIR, exist_ok=True)
    path = os.path.join(MACRO_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(events, f)
    return path


def play_gui(name: str) -> str:
    """Play back a recorded macro by name."""
    if _IMPORT_ERROR:
        return f"pyautogui not available: {_IMPORT_ERROR}"
    import json
    import os
    path = os.path.join(MACRO_DIR, f"{name}.json")
    if not os.path.isfile(path):
        return f"Macro '{name}' not found"
    with open(path, "r", encoding="utf-8") as f:
        events = json.load(f)
    pyautogui.play(events)
    return f"Played {name}"


def open_recorder_window():
    """Open a small Tkinter window to start/stop recording."""
    if tk is None:
        return "Tkinter not available"
    win = tk.Tk()
    win.title("Macro Recorder")
    name_var = tk.StringVar(value="macro1")
    tk.Label(win, text="Macro name:").pack()
    tk.Entry(win, textvariable=name_var).pack()
    def start_rec():
        win.withdraw()
        path = record_gui(name_var.get())
        messagebox.showinfo("Saved", f"Macro saved to {path}")
        win.deiconify()
    tk.Button(win, text="Record", command=start_rec).pack()
    win.mainloop()


def get_description() -> str:
    return "GUI to record pyautogui actions and save them as macros."
