import os
import pytest
import tkinter as tk
from tkinter import ttk

from gui.plugin import GuiTabRegistry
from config_loader import ConfigLoader

if not os.environ.get("DISPLAY"):
    pytest.skip("GUI not available", allow_module_level=True)


def test_gui_registry_loads_tabs():
    root = tk.Tk()
    notebook = ttk.Notebook(root)
    output = tk.Text(root)
    loader = GuiTabRegistry()
    loader.load_tabs(notebook, ConfigLoader(), output, root)
    names = [name for name, _ in loader.get_frames()]
    assert "config_editor" in names
    assert "macros" in names
    assert "module_generator" in names
    assert "image_generator" in names
    assert "speech_learning" in names
    root.destroy()
