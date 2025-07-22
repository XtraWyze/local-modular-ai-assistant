"""Tkinter visual editor for recorded macros."""

try:
    import tkinter as tk
    import json
    import os
except Exception as e:  # pragma: no cover - optional dependency
    tk = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

MACRO_DIR = "macros"

__all__ = ["open_editor"]


def open_editor(name: str):
    if tk is None:
        return "Tkinter not available"
    path = os.path.join(MACRO_DIR, f"{name}.json")
    if not os.path.isfile(path):
        return f"Macro {name} not found"
    with open(path, "r", encoding="utf-8") as f:
        events = json.load(f)
    win = tk.Tk()
    win.title(f"Edit macro {name}")
    text = tk.Text(win, width=60, height=20)
    text.pack()
    text.insert("1.0", json.dumps(events, indent=2))
    def save():
        with open(path, "w", encoding="utf-8") as f:
            json.dump(json.loads(text.get("1.0", tk.END)), f, indent=2)
    tk.Button(win, text="Save", command=save).pack()
    win.mainloop()


def get_description() -> str:
    return "Allows basic editing of saved macro JSON files via Tkinter."
