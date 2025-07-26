"""Dynamic plugin loader for skill modules.

This module loads all Python files from the configured ``skills`` directory,
imports their top-level callables, and registers them in a global registry.
Modules without any callable functions are ignored. When initialized, it prints
all loaded plugin names and their exported functions.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict

from error_logger import log_error

__all__ = ["PluginRegistry", "registry"]


class PluginRegistry:
    """Manage loading and registration of skill plugins."""

    def __init__(self, skills_dir: str | os.PathLike = "skills") -> None:
        self.skills_dir = Path(skills_dir)
        self.modules: Dict[str, ModuleType] = {}
        self.functions: Dict[str, Callable] = {}
        self.load_all()
        if self.functions:
            self._print_summary()

    # internal helpers -------------------------------------------------
    def _import_module(self, name: str, path: Path) -> ModuleType | None:
        spec = importlib.util.spec_from_file_location(f"skills.{name}", path)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        except Exception as e:  # pragma: no cover - runtime errors
            log_error(f"[plugin_loader] Failed to import {name}: {e}")
            return None
        return mod

    def _register_functions(self, name: str, mod: ModuleType) -> bool:
        funcs = {
            fn: getattr(mod, fn)
            for fn in dir(mod)
            if callable(getattr(mod, fn)) and not fn.startswith("_")
        }
        if not funcs:
            return False
        self.modules[name] = mod
        self.functions.update(funcs)
        return True

    def _print_summary(self) -> None:
        print("[PluginLoader] Loaded plugins:")
        for mod_name, mod in self.modules.items():
            funcs = [fn for fn in dir(mod) if callable(getattr(mod, fn)) and not fn.startswith("_")]
            print(f"  - {mod_name}: {', '.join(funcs)}")

    # public API -------------------------------------------------------
    def load_all(self) -> None:
        """Load all plugins from ``self.skills_dir``."""
        if not self.skills_dir.exists():
            return
        for path in self.skills_dir.glob("*.py"):
            if path.name == "__init__.py":
                continue
            name = path.stem
            mod = self._import_module(name, path)
            if mod:
                self._register_functions(name, mod)

    def get_functions(self) -> Dict[str, Callable]:
        """Return a mapping of function names to callables."""
        return dict(self.functions)


# Global registry instance used throughout the assistant
registry = PluginRegistry()
