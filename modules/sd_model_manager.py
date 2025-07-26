"""Manage saved Stable Diffusion model paths."""

from __future__ import annotations

import json
import os
from typing import List

from modules.utils import resource_path

MODULE_NAME = "sd_model_manager"
MODELS_FILE = resource_path("sd_models.json")

model_paths: List[str] = []

__all__ = [
    "load_models",
    "save_models",
    "add_model",
    "remove_model",
    "get_info",
    "get_description",
]


def load_models() -> List[str]:
    """Load saved model paths from :data:`MODELS_FILE`."""
    global model_paths
    try:
        with open(MODELS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            model_paths = [str(p) for p in data if isinstance(p, str)]
        else:
            model_paths = []
    except Exception:
        model_paths = []
    return model_paths


def save_models(models: List[str] | None = None) -> None:
    """Persist ``models`` to :data:`MODELS_FILE`."""
    if models is None:
        models = model_paths
    with open(MODELS_FILE, "w", encoding="utf-8") as f:
        json.dump(models, f, indent=2)


def add_model(path: str) -> None:
    """Add ``path`` to :data:`model_paths` and save."""
    if not path:
        return
    if path not in model_paths:
        model_paths.append(path)
        save_models()


def remove_model(path: str) -> bool:
    """Remove ``path`` from :data:`model_paths` if present."""
    try:
        model_paths.remove(path)
        save_models()
        return True
    except ValueError:
        return False


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": get_description(),
        "functions": [
            "load_models",
            "save_models",
            "add_model",
            "remove_model",
        ],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Manage saved Stable Diffusion model paths."


# Initialize on import
load_models()
