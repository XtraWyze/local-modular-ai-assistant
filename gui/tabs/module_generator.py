from __future__ import annotations

"""Module generator tab."""

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass

from modules import api_keys


@dataclass
class ModuleGeneratorUI:
    notebook: ttk.Notebook
    output: tk.Text

    def register(self, root: tk.Tk) -> ttk.Frame:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Module Generator")

        self.name_var = tk.StringVar()
        ttk.Label(frame, text="Module Name:").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Entry(frame, textvariable=self.name_var).pack(fill="x", padx=10)

        ttk.Label(frame, text="Description:").pack(anchor="w", padx=10, pady=(10, 0))
        self.desc = tk.Text(frame, height=4)
        self.desc.pack(fill="x", padx=10)

        api_frame = ttk.LabelFrame(frame, text="API Keys")
        api_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.openai_var = tk.StringVar(value="")
        self.anthropic_var = tk.StringVar(value="")
        self.google_var = tk.StringVar(value="")
        ttk.Label(api_frame, text="OpenAI:").grid(row=0, column=0, sticky="w")
        ttk.Entry(api_frame, textvariable=self.openai_var, width=40).grid(row=0, column=1, sticky="ew")
        ttk.Label(api_frame, text="Anthropic:").grid(row=1, column=0, sticky="w")
        ttk.Entry(api_frame, textvariable=self.anthropic_var, width=40).grid(row=1, column=1, sticky="ew")
        ttk.Label(api_frame, text="Google:").grid(row=2, column=0, sticky="w")
        ttk.Entry(api_frame, textvariable=self.google_var, width=40).grid(row=2, column=1, sticky="ew")
        api_frame.columnconfigure(1, weight=1)
        ttk.Button(api_frame, text="Save Keys", command=self.save_keys).grid(row=3, column=0, columnspan=2, pady=5)

        self.provider_var = tk.StringVar(value="openai")
        ttk.Label(frame, text="Provider:").pack(anchor="w", padx=10)
        ttk.OptionMenu(frame, self.provider_var, "openai", "openai", "anthropic", "google").pack(anchor="w", padx=10)

        ttk.Label(frame, text="Preview:").pack(anchor="w", padx=10, pady=(10, 0))
        self.preview = tk.Text(frame, height=15)
        self.preview.pack(fill="both", expand=True, padx=10)
        self.status = ttk.Label(frame, text="")
        self.status.pack(anchor="w", padx=10, pady=(5, 0))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Generate Preview", command=self.generate_preview).pack(side=tk.LEFT, padx=5)
        self.save_btn = ttk.Button(btn_frame, text="Save Module", state=tk.DISABLED, command=self.save)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", state=tk.DISABLED, command=self.cancel)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        self.current_code = ""
        return frame

    # --------------------------------------------------------------
    def save_keys(self) -> None:
        keys = {
            "openai": self.openai_var.get().strip(),
            "anthropic": self.anthropic_var.get().strip(),
            "google": self.google_var.get().strip(),
        }
        api_keys.save_api_keys(keys)
        self.status.config(text="API keys saved.")

    def generate_preview(self) -> None:
        desc = self.desc.get("1.0", tk.END).strip()
        if not desc:
            self.status.config(text="Enter a description first.")
            return
        try:
            from modules.module_generator import CodexClient

            client = CodexClient(provider=self.provider_var.get())
            code = client.generate_code(desc)
            if not code:
                self.status.config(text="No code returned")
                return
            self.preview.delete("1.0", tk.END)
            self.preview.insert("1.0", code)
            self.save_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.NORMAL)
            self.status.config(text="Preview generated. Click Save to keep it.")
            self.current_code = code
        except Exception as exc:
            self.status.config(text=f"Error: {exc}")

    def save(self) -> None:
        if not self.current_code:
            self.status.config(text="Generate code first.")
            return
        name = self.name_var.get().strip() or None
        try:
            from modules import module_generator

            path = module_generator.save_module_code(self.current_code, name=name)
            self.status.config(text=f"Saved to {path}")
            self.preview.delete("1.0", tk.END)
            self.save_btn.config(state=tk.DISABLED)
            self.cancel_btn.config(state=tk.DISABLED)
            self.current_code = ""
        except Exception as exc:
            self.status.config(text=f"Error: {exc}")

    def cancel(self) -> None:
        self.preview.delete("1.0", tk.END)
        self.save_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.DISABLED)
        self.current_code = ""
        self.status.config(text="Cancelled")


def register_gui_tab(notebook: ttk.Notebook, config_loader, output, root):
    return ModuleGeneratorUI(notebook, output).register(root)
