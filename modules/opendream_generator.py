from __future__ import annotations

"""OpenDream text-to-3D model generator utilities."""

import os
from typing import Optional

from . import gpu
from modules.utils import project_path
from error_logger import log_error

try:
    import opendream  # type: ignore
except Exception as e:  # pragma: no cover - optional dependency
    opendream = None  # type: ignore
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

MODULE_NAME = "opendream_generator"

__all__ = ["generate_model", "get_info", "get_description"]


def generate_model(
    prompt: str,
    *,
    quality: int = 32,
    save_dir: str = "generated_3d",
    name: str | None = None,
) -> str:
    """Generate a 3D model using OpenDream.

    Parameters
    ----------
    prompt:
        Text description of the object.
    quality:
        Quality level passed to the OpenDream backend.
    save_dir:
        Directory to save the resulting model.
    name:
        Optional file name without extension.
    """
    if opendream is None:
        return f"Missing dependencies: {_IMPORT_ERROR}"

    try:
        model = getattr(opendream, "generate", lambda *a, **k: None)(
            prompt, quality=quality
        )
        if not hasattr(model, "save"):
            return "Pipeline did not return a model"

        if not os.path.isabs(save_dir):
            save_dir = project_path(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, f"{name or 'opendream_model'}.obj")
        model.save(filename)
        return filename
    except Exception as exc:  # pragma: no cover - safety net
        log_error(f"[opendream] {exc}")
        return f"Error: {exc}"


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": "Generate 3D models using OpenDream.",
        "functions": ["generate_model"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Local OpenDream 3D model generation utilities."
