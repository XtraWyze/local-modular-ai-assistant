from __future__ import annotations

"""Stable DreamFusion text-to-3D model generator utilities."""

import os
from typing import Optional

from . import gpu
from modules.utils import project_path
from error_logger import log_error

try:
    from dreamfusion import DreamFusionPipeline  # type: ignore
except Exception as e:  # pragma: no cover - optional dependency
    DreamFusionPipeline = None  # type: ignore
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

MODULE_NAME = "stable_dreamfusion_generator"

__all__ = ["generate_model", "load_model", "get_info", "get_description"]

_pipeline: Optional[DreamFusionPipeline] = None
_model_path: str | None = None


def load_model(model_path: str, device: str | None = None) -> str:
    """Load a DreamFusion pipeline from ``model_path``."""
    global _pipeline, _model_path
    if DreamFusionPipeline is None or torch is None:
        return f"Missing dependencies: {_IMPORT_ERROR or _TORCH_ERROR}"

    if device is None:
        device = gpu.get_device()

    if _pipeline is not None and _model_path == model_path:
        return "loaded"

    try:
        pipe = DreamFusionPipeline.from_pretrained(model_path)
        pipe = pipe.to(device)
    except Exception as exc:  # pragma: no cover - loading may fail
        log_error(f"[dreamfusion] load failed: {exc}")
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
    """Generate a 3D model using Stable DreamFusion."""
    if DreamFusionPipeline is None or torch is None:
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
        filename = os.path.join(save_dir, f"{name or 'dreamfusion_model'}.obj")
        model_data.save(filename)
        return filename
    except Exception as exc:  # pragma: no cover - safety net
        log_error(f"[dreamfusion] {exc}")
        return f"Error: {exc}"


def get_info() -> dict:
    return {
        "name": MODULE_NAME,
        "description": "Generate 3D models locally using Stable DreamFusion.",
        "functions": ["generate_model"],
    }


def get_description() -> str:
    return "Local Stable DreamFusion 3D model generation utilities."
