"""Dynamic loader for skill plugins.

Imports all Python files in the given directory and returns a mapping
of callable names to callables. Functions starting with an underscore
are ignored.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict

from error_logger import log_error

__all__ = ["load_skills"]


def _import_module(path: Path) -> ModuleType | None:
    name = path.stem
    spec = importlib.util.spec_from_file_location(f"skills.{name}", path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    except Exception as e:  # pragma: no cover - plugin import errors
        log_error(f"[skill_loader] Failed to load {path}: {e}")
        return None
    return mod


def load_skills(directory: str = "skills") -> Dict[str, Callable]:
    """Load Python skill plugins from ``directory``.

    Parameters
    ----------
    directory:
        Path to a folder containing ``.py`` files.

    Returns
    -------
    dict
        Mapping of function names to callables that were loaded.
    """
    funcs: Dict[str, Callable] = {}
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return funcs

    for path in dir_path.glob("*.py"):
        if path.name == "__init__.py":
            continue
        mod = _import_module(path)
        if not mod:
            continue
        for name in dir(mod):
            if name.startswith("_"):
                continue
            obj = getattr(mod, name)
            if callable(obj):
                funcs[name] = obj
    return funcs
