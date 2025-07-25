"""Dynamic loader for user skill plugins.

This module automatically imports all ``.py`` files in the configured
``skills`` directory and keeps them up to date. Public callables are
registered so the orchestrator can invoke them by name.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict

from error_logger import log_error

__all__ = ["SkillRegistry", "registry"]


class SkillRegistry:
    """Manage skill plugin modules and their exported functions."""

    def __init__(self, skills_dir: str | os.PathLike = "skills") -> None:
        self.skills_dir = Path(skills_dir)
        self.modules: Dict[str, ModuleType] = {}
        self.mtimes: Dict[str, float] = {}
        self.functions: Dict[str, Callable] = {}
        self.load_all()

    def _import_module(self, name: str, path: Path) -> ModuleType | None:
        spec = importlib.util.spec_from_file_location(f"skills.{name}", path)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        except Exception as e:  # pragma: no cover - runtime import errors
            log_error(f"[SkillLoader] Failed to import {name}: {e}")
            return None
        return mod

    def _register_functions(self, name: str, mod: ModuleType) -> None:
        names = getattr(mod, "__all__", None)
        if names is None:
            names = [n for n in dir(mod) if callable(getattr(mod, n)) and not n.startswith("_")]
        for fn in names:
            func = getattr(mod, fn, None)
            if callable(func):
                self.functions[fn] = func

    def load_all(self) -> None:
        """Load all skill modules from ``self.skills_dir``."""
        if not self.skills_dir.exists():
            return
        for path in self.skills_dir.glob("*.py"):
            if path.name == "__init__.py":
                continue
            self._load(path.stem, path)

    def _load(self, name: str, path: Path) -> None:
        mod = self._import_module(name, path)
        if not mod:
            return
        self.modules[name] = mod
        self.mtimes[name] = os.path.getmtime(path)
        self._register_functions(name, mod)

    def reload_modified(self) -> None:
        """Reload modules that were added or changed on disk."""
        if not self.skills_dir.exists():
            return
        # New or updated files
        for path in self.skills_dir.glob("*.py"):
            if path.name == "__init__.py":
                continue
            name = path.stem
            mtime = os.path.getmtime(path)
            if name not in self.mtimes or mtime != self.mtimes[name]:
                self._load(name, path)
        # Removed files
        for name in list(self.modules):
            path = self.skills_dir / f"{name}.py"
            if not path.exists():
                self.modules.pop(name, None)
                self.mtimes.pop(name, None)
                for fn in list(self.functions):
                    func = self.functions[fn]
                    if getattr(func, "__module__", "").endswith(name):
                        self.functions.pop(fn, None)

    def get_functions(self) -> Dict[str, Callable]:
        """Return currently registered skill functions."""
        return dict(self.functions)


# Default registry used by the orchestrator
registry = SkillRegistry()
