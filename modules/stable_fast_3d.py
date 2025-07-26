"""Local Stable Fast 3D model generator."""

from __future__ import annotations

import os
from typing import Optional

from . import gpu

try:
    from diffusers import StableFast3DPipeline  # fictional example
except Exception as e:  # pragma: no cover - optional dependency
    StableFast3DPipeline = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

try:
    import torch
except Exception as e:  # pragma: no cover - optional dependency
    torch = None
    _TORCH_ERROR = e
else:
    _TORCH_ERROR = None

from error_logger import log_error
from modules.utils import project_path

MODULE_NAME = "stable_fast_3d"

__all__ = ["generate_model", "load_model", "get_info", "get_description"]

_pipeline: Optional[StableFast3DPipeline] = None
_model_path: str | None = None


def load_model(model_path: str, device: str | None = None) -> str:
    """Load a Stable Fast 3D pipeline from ``model_path``."""
    global _pipeline, _model_path
    if StableFast3DPipeline is None or torch is None:
        return f"Missing dependencies: {_IMPORT_ERROR or _TORCH_ERROR}"

    if device is None:
        device = gpu.get_device()

    if _pipeline is not None and _model_path == model_path:
        return "loaded"

    try:
        pipe = StableFast3DPipeline.from_pretrained(model_path)
        pipe = pipe.to(device)
    except Exception as exc:  # pragma: no cover - loading may fail
        log_error(f"[stable_fast_3d] load failed: {exc}")
        return f"Failed to load model: {exc}"

    _pipeline = pipe
    _model_path = model_path
    return "loaded"


def generate_model(
    prompt: str,
    model_path: str,
    *,
    device: str | None = None,
    save_dir: str = "generated_3d",
    name: str | None = None,
) -> str:
    """Generate a 3D model using a local Stable Fast 3D model."""
    if StableFast3DPipeline is None or torch is None:
        return f"Missing dependencies: {_IMPORT_ERROR or _TORCH_ERROR}"

    if device is None:
        device = gpu.get_device()

    if load_model(model_path, device) != "loaded":
        return f"Failed to load model from {model_path}"

    assert _pipeline is not None
    pipe = _pipeline

    try:
        ctx = gpu.autocast(device)
        with ctx:
            result = pipe(prompt)
        model_data = getattr(result, "model", None) or result
        if not hasattr(model_data, "save"):
            return "Pipeline did not return a model"

        if not os.path.isabs(save_dir):
            save_dir = project_path(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        if name:
            safe = "".join(c for c in name if c.isalnum() or c in "-_")
            filename = os.path.join(save_dir, f"{safe}.obj")
        else:
            filename = os.path.join(
                save_dir,
                f"model_{len(os.listdir(save_dir))+1}.obj",
            )
        model_data.save(filename)
        return filename
    except Exception as exc:  # pragma: no cover - safety net
        log_error(f"[stable_fast_3d] {exc}")
        return f"Error: {exc}"


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": "Generate 3D models locally using Stable Fast 3D.",
        "functions": ["generate_model"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Local Stable Fast 3D model generation utilities."

