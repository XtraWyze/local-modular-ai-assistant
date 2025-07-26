from __future__ import annotations

"""Image generator tab."""

import os
import threading
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass

from modules import gpu, image_generator, sd_generator
try:
    from PIL import Image, ImageTk
except Exception:  # pragma: no cover - optional
    Image = ImageTk = None


@dataclass
class ImageGeneratorUI:
    notebook: ttk.Notebook

    def register(self, root: tk.Tk) -> ttk.Frame:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Image Generator")

        self.prompt = tk.Text(frame, height=4)
        self.prompt.pack(fill="x", padx=10, pady=(10, 0))

        self.source_var = tk.StringVar(value="cloud")
        ttk.Label(frame, text="Source:").pack(anchor="w", padx=10, pady=(5, 0))
        self.source_menu = ttk.OptionMenu(frame, self.source_var, "cloud", "cloud", "local", command=self.toggle_source)
        self.source_menu.pack(anchor="w", padx=10)

        self.sd_model_var = tk.StringVar(value="")
        ttk.Label(frame, text="SD Model Path:").pack(anchor="w", padx=10, pady=(5, 0))
        self.sd_model_entry = ttk.Entry(frame, textvariable=self.sd_model_var, width=50)
        self.sd_model_entry.pack(fill="x", padx=10)

        self.sd_device_var = tk.StringVar(value=gpu.get_device())
        ttk.Label(frame, text="Device:").pack(anchor="w", padx=10, pady=(5, 0))
        self.sd_device_menu = ttk.OptionMenu(frame, self.sd_device_var, "cpu", "cpu", "cuda")
        self.sd_device_menu.pack(anchor="w", padx=10)

        self.size_var = tk.StringVar(value="512x512")
        ttk.Label(frame, text="Size:").pack(anchor="w", padx=10, pady=(5, 0))
        ttk.OptionMenu(frame, self.size_var, "512x512", "256x256", "512x512", "1024x1024").pack(anchor="w", padx=10)

        self.toggle_source()

        self.preview = ttk.Label(frame)
        self.preview.pack(pady=10)
        self.status = ttk.Label(frame, text="")
        self.status.pack(anchor="w", padx=10, pady=(5, 0))
        ttk.Button(frame, text="Generate Image", command=self.generate).pack(pady=5)
        return frame

    # --------------------------------------------------------------
    def toggle_source(self, *_args) -> None:
        state = tk.NORMAL if self.source_var.get() == "local" else tk.DISABLED
        self.sd_model_entry.config(state=state)
        self.sd_device_menu.config(state=state)

    def generate(self) -> None:
        prompt = self.prompt.get("1.0", tk.END).strip()
        if not prompt:
            self.status.config(text="Enter a prompt first.")
            return
        self.status.config(text="Generating...")

        def _run() -> None:
            if self.source_var.get() == "local":
                path = sd_generator.generate_image(
                    prompt,
                    self.sd_model_var.get(),
                    device=self.sd_device_var.get(),
                )
            else:
                path = image_generator.generate_image(prompt, size=self.size_var.get())

            def _update() -> None:
                if path.endswith(".png") and os.path.exists(path):
                    if Image and ImageTk:
                        try:
                            img = Image.open(path)
                            photo = ImageTk.PhotoImage(img)
                            self.preview.configure(image=photo)
                            self.preview.image = photo
                        except Exception:
                            self.preview.configure(image="")
                    self.status.config(text=f"Saved to {path}")
                else:
                    self.preview.configure(image="")
                    self.status.config(text=path)

            self.status.after(0, _update)

        threading.Thread(target=_run, daemon=True).start()


def register_gui_tab(notebook: ttk.Notebook, config_loader, output, root):
    return ImageGeneratorUI(notebook).register(root)
