from __future__ import annotations

"""Simple plugin loader for GUI tabs."""

import importlib
import pkgutil
from types import ModuleType
from tkinter import ttk
from typing import List, Tuple


class GuiTabRegistry:
    """Load and register GUI tabs from the ``gui.tabs`` package."""

    def __init__(self, package: str = "gui.tabs") -> None:
        self.package = package
        self.modules: List[ModuleType] = []
        self.tabs: List[Tuple[str, ttk.Frame]] = []

    def load_tabs(
        self,
        notebook: ttk.Notebook,
        config_loader,
        output_widget,
        root,
    ) -> None:
        """Import all modules under ``self.package`` and call ``register_gui_tab``.

        Each plugin should define ``register_gui_tab(notebook, config_loader, output, root)``
        and return the created ``ttk.Frame``.
        """
        package = importlib.import_module(self.package)
        for _, name, _ in pkgutil.iter_modules(package.__path__):  # type: ignore[attr-defined]
            mod = importlib.import_module(f"{self.package}.{name}")
            if hasattr(mod, "register_gui_tab"):
                frame = mod.register_gui_tab(notebook, config_loader, output_widget, root)
                self.modules.append(mod)
                self.tabs.append((name, frame))

    def get_frames(self) -> List[Tuple[str, ttk.Frame]]:
        """Return the list of registered tab frames."""
        return list(self.tabs)
