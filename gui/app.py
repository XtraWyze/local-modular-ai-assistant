from __future__ import annotations

"""Main GUI assembly using plugin-based tabs."""

import asyncio
import tkinter as tk
from tkinter import ttk

from config_loader import ConfigLoader
from gui.plugin import GuiTabRegistry
from gui.voice_interface import VoiceInterface


def _build_base_ui(root: tk.Tk) -> tuple[ttk.Notebook, tk.Text]:
    """Create the base notebook and output widget."""
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    main_tab = ttk.Frame(notebook)
    notebook.add(main_tab, text="Assistant")

    output = tk.Text(main_tab, height=20, wrap=tk.WORD)
    output.pack(fill="both", expand=True, padx=10, pady=10)
    return notebook, output


async def run_gui() -> None:
    """Run the Tkinter GUI inside an asyncio event loop."""
    root = tk.Tk()
    root.title("AI Assistant")

    notebook, output = _build_base_ui(root)
    config_loader = ConfigLoader()

    # Load tab plugins
    registry = GuiTabRegistry()
    registry.load_tabs(notebook, config_loader, output, root)

    voice = VoiceInterface(config_loader.config.get("vosk_model_path", ""))
    voice.start_listening(output)

    # simple event loop integration
    while True:
        root.update()
        await asyncio.sleep(0.01)


def main() -> None:
    asyncio.run(run_gui())
