from __future__ import annotations

"""Config editor GUI tab."""

import json
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass

from config_gui import open_memory_window
from config_validator import validate_config


@dataclass
class ConfigEditorTab:
    notebook: ttk.Notebook
    config_loader
    output: tk.Text

    def register(self, root: tk.Tk) -> ttk.Frame:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Config Editor")
        self.text = tk.Text(frame, wrap=tk.WORD)
        self.text.pack(fill="both", expand=True, padx=10, pady=10)

        btn = ttk.Frame(frame)
        btn.pack(pady=(0, 10))
        ttk.Button(btn, text="Reload", command=self.load).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn, text="Save", command=self.save).pack(side=tk.LEFT)
        ttk.Button(btn, text="Edit Memory", command=open_memory_window).pack(side=tk.LEFT, padx=5)

        self.load()
        return frame

    # ------------------------------------------------------------------
    def load(self) -> None:
        try:
            with open(self.config_loader.path, "r", encoding="utf-8") as f:
                data = f.read()
        except Exception as exc:
            data = f"Error loading config: {exc}\n"
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, data)

    def save(self) -> None:
        raw = self.text.get("1.0", tk.END)
        try:
            cfg = json.loads(raw)
        except Exception as exc:
            self.output.insert(tk.END, f"[CONFIG ERROR] {exc}\n")
            return
        errors = validate_config(cfg)
        if errors:
            self.output.insert(
                tk.END, "[CONFIG VALIDATION ERROR]\n" + "\n".join(errors) + "\n"
            )
            return
        with open(self.config_loader.path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        self.config_loader.config = cfg
        self.output.insert(tk.END, "[SYSTEM] Config saved.\n")


def register_gui_tab(notebook: ttk.Notebook, config_loader, output, root):
    return ConfigEditorTab(notebook, config_loader, output).register(root)
