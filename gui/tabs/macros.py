from __future__ import annotations

"""Macro management tab."""

import os
import threading
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass

from error_logger import log_error


@dataclass
class MacroManager:
    notebook: ttk.Notebook
    output: tk.Text

    def register(self, root: tk.Tk) -> ttk.Frame:
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Hotkeys")

        self.name_var = tk.StringVar()
        ttk.Label(frame, text="Macro Name:").pack(anchor="w")
        self.entry = ttk.Entry(frame, textvariable=self.name_var)
        self.entry.pack(fill="x", pady=(0, 5))

        self.status = ttk.Label(frame, text="")
        self.status.pack(pady=(0, 10))

        ttk.Button(frame, text="Record Macro", command=self.start_recording).pack(pady=(0, 10))
        self.buttons_frame = ttk.Frame(frame)
        self.buttons_frame.pack(fill="both", expand=True)
        self.buttons: list[ttk.Button] = []
        for r in range(5):
            for c in range(6):
                btn = ttk.Button(self.buttons_frame, text=f"Slot {r * 6 + c + 1}")
                btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
                self.buttons.append(btn)
            self.buttons_frame.columnconfigure(c, weight=1)

        ttk.Button(frame, text="Edit Macros", command=self.edit_macros).pack(pady=(0, 5))
        self.update_buttons()
        return frame

    # --------------------------------------------------------------
    def _run_macro(self, name: str) -> None:
        from modules.automation_learning import play_macro

        result = play_macro(name)
        self.status.config(text=result)

    def update_buttons(self) -> None:
        from modules.automation_learning import list_macros

        macros = list_macros()
        for i, btn in enumerate(self.buttons):
            if i < len(macros):
                name = macros[i]
                btn.configure(text=name, state=tk.NORMAL, command=lambda n=name: self._run_macro(n))
            else:
                btn.configure(text=f"Slot {i + 1}", command=lambda: None, state=tk.DISABLED)

    def start_recording(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            self.status.config(text="Enter a macro name first.")
            return
        count = 3

        def record_thread() -> None:
            from modules import automation_learning

            path = automation_learning.record_macro(name)

            def _cb() -> None:
                self.status.config(text=f"Saved to {path}")
                self.update_buttons()

            self.status.after(0, _cb)

        def countdown_step() -> None:
            nonlocal count
            if count > 0:
                self.status.config(text=f"Recording in {count}...")
                self.status.after(1000, countdown_step)
                count -= 1
            else:
                self.status.config(text="Recording... Press ESC to stop.")
                threading.Thread(target=record_thread, daemon=True).start()

        countdown_step()

    def edit_macros(self) -> None:
        win = tk.Toplevel(self.notebook)
        win.title("Edit Macros")
        listbox = tk.Listbox(win)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        def _refresh() -> None:
            listbox.delete(0, tk.END)
            from modules.automation_learning import list_macros

            for m in list_macros():
                listbox.insert(tk.END, m)

        status = ttk.Label(win, text="")
        status.pack()

        def delete_selected() -> None:
            if not listbox.curselection():
                status.config(text="Select a macro first.")
                return
            name = listbox.get(listbox.curselection()[0])
            self._remove_macro(name)
            status.config(text=f"Deleted {name}")
            _refresh()

        def delete_all() -> None:
            for name in listbox.get(0, tk.END):
                self._remove_macro(name)
            status.config(text="All macros deleted")
            _refresh()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Delete Selected", command=delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete All", command=delete_all).pack(side=tk.LEFT, padx=5)

        _refresh()

    def _remove_macro(self, name: str) -> None:
        from modules.automation_learning import MACRO_DIR
        from state_manager import remove_action

        try:
            path = os.path.join(MACRO_DIR, f"{name}.json")
            if os.path.exists(path):
                os.remove(path)
        except Exception as exc:
            log_error(f"[GUI] remove macro error: {exc}")
        remove_action(name)
        self.update_buttons()


def register_gui_tab(notebook: ttk.Notebook, config_loader, output, root):
    return MacroManager(notebook, output).register(root)
