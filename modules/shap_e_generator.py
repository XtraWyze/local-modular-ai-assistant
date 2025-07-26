from __future__ import annotations

"""Shap-E text-to-3D model generator utilities."""

import os

from . import gpu
from modules.utils import project_path
from error_logger import log_error

try:
    import shap_e  # type: ignore
except Exception as e:  # pragma: no cover - optional dependency
    shap_e = None  # type: ignore
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

MODULE_NAME = "shap_e_generator"

__all__ = ["generate_model", "get_info", "get_description"]


def generate_model(
    prompt: str,
    *,
    device: str | None = None,
    save_dir: str = "generated_3d",
    name: str | None = None,
) -> str:
    """Generate a 3D model using Shap-E."""
    if shap_e is None or torch is None:
        return f"Missing dependencies: {_IMPORT_ERROR or _TORCH_ERROR}"
    if device is None:
        device = gpu.get_device()
    try:
        model = getattr(shap_e, "generate", lambda *a, **k: None)(prompt, device=device)
        if not hasattr(model, "save"):
            return "Pipeline did not return a model"
        if not os.path.isabs(save_dir):
            save_dir = project_path(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, f"{name or 'shap_e_model'}.obj")
        model.save(filename)
        return filename
    except Exception as exc:  # pragma: no cover - safety net
        log_error(f"[shap_e] {exc}")
        return f"Error: {exc}"


def get_info() -> dict:
    return {
        "name": MODULE_NAME,
        "description": "Generate 3D models using Shap-E.",
        "functions": ["generate_model"],
    }


def get_description() -> str:
    return "Local Shap-E 3D model generation utilities."
