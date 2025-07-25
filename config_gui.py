"""Simple Tkinter GUI for editing config.json settings."""

import json
import tkinter as tk
from tkinter import messagebox
import memory_manager as mm

CONFIG_FILE = "config.json"


def load_config() -> dict:
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def open_memory_window():
    """Display and edit stored memory and the max memory setting."""
    cfg = load_config()
    mm.load_memory()
    win = tk.Toplevel()
    win.title("Memory Editor")

    tk.Label(win, text="Max Memory Entries").pack()
    max_var = tk.StringVar(value=str(cfg.get("memory_max", mm.MEMORY_MAX)))
    tk.Entry(win, textvariable=max_var, width=10).pack()

    mem_box = tk.Text(win, width=60, height=20)
    mem_box.pack(fill="both", expand=True)
    mem_box.insert("1.0", "\n".join(mm.memory.get("texts", [])))

    def save():
        try:
            new_max = int(max_var.get())
        except Exception:
            new_max = mm.MEMORY_MAX
        cfg["memory_max"] = new_max
        mm.MEMORY_MAX = new_max
        save_config(cfg)

        lines = mem_box.get("1.0", tk.END).strip().splitlines()
        mm.memory["texts"] = lines
        mm.memory["vectors"] = [mm.get_model().encode([t])[0] for t in lines]
        mm.prune_memory(mm.MEMORY_MAX)
        mm.save_memory(mm.memory)
        messagebox.showinfo("Saved", "Memory updated")

    tk.Button(win, text="Save", command=save).pack(pady=5)
    return win

def open_config_window():
    cfg = load_config()
    win = tk.Tk()
    win.title("Assistant Settings")
    entries = {}
    for i, (key, value) in enumerate(cfg.items()):
        tk.Label(win, text=key).grid(row=i, column=0, sticky="w")
        var = tk.StringVar(value=str(value))
        tk.Entry(win, textvariable=var, width=40).grid(row=i, column=1)
        entries[key] = var

    def save():
        for k, var in entries.items():
            try:
                val = json.loads(var.get())
            except Exception:
                val = var.get()
            cfg[k] = val
        save_config(cfg)
        messagebox.showinfo("Saved", "Configuration saved")

    tk.Button(win, text="Save", command=save).grid(columnspan=2)
    tk.Button(win, text="Edit Memory", command=open_memory_window).grid(columnspan=2)
    win.mainloop()

if __name__ == "__main__":
    open_config_window()
