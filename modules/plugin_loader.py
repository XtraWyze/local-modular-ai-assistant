"""Simple plugin loader that reads manifest files."""

import json
import importlib
import os
from error_logger import log_error

MODULE_NAME = "plugin_loader"
MANIFEST_NAME = "plugin.json"

__all__ = ["load_plugins"]


def load_plugins(directory: str = "modules") -> dict:
    """Load plugins that contain a ``plugin.json`` manifest."""
    loaded = {}
    for item in os.listdir(directory):
        path = os.path.join(directory, item)
        manifest = os.path.join(path, MANIFEST_NAME)
        if os.path.isdir(path) and os.path.isfile(manifest):
            try:
                with open(manifest, "r", encoding="utf-8") as f:
                    info = json.load(f)
                mod_name = info.get("module")
                if mod_name:
                    mod = importlib.import_module(mod_name)
                    loaded[mod_name] = mod
            except Exception as e:  # pragma: no cover - plugin errors
                log_error(f"[plugin_loader] {e}")
    return loaded


def get_description() -> str:
    return "Loads plugins with plugin.json manifests from a directory."
