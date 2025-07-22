"""Load Python macros from the ``macros`` directory as plugins."""

import importlib.util
import types
import os
from error_logger import log_error

MACRO_DIR = "macros"
MODULE_NAME = "macro_loader"

__all__ = ["load_macro", "list_macros"]

_loaded = {}

def load_macro(path: str) -> types.ModuleType | None:
    """Dynamically load a macro script by path."""
    if not os.path.isfile(path):
        return None
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    except Exception as e:  # pragma: no cover - macro errors
        log_error(f"[macro_loader] Failed to load {path}: {e}")
        return None
    _loaded[name] = mod
    return mod


def list_macros() -> list[str]:
    """Return available Python macro names."""
    if not os.path.isdir(MACRO_DIR):
        return []
    files = [f[:-3] for f in os.listdir(MACRO_DIR) if f.endswith('.py')]
    return files


def get_description() -> str:
    return "Loads Python scripts from the macros folder for execution as plugins."
