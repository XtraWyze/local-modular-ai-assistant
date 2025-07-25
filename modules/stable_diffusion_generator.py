"""Local Stable Diffusion image generator."""

from __future__ import annotations

import os
from typing import Optional

try:
    from diffusers import StableDiffusionPipeline
except Exception as e:  # pragma: no cover - optional dependency
    StableDiffusionPipeline = None
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

MODULE_NAME = "stable_diffusion_generator"

__all__ = ["generate_image", "load_model", "get_info", "get_description"]


_pipeline: Optional[StableDiffusionPipeline] = None
_model_path: str | None = None


def load_model(model_path: str, device: str = "cpu") -> str:
    """Load a Stable Diffusion pipeline from ``model_path``."""
    global _pipeline, _model_path
    if StableDiffusionPipeline is None or torch is None:
        return f"Missing dependencies: {_IMPORT_ERROR or _TORCH_ERROR}"

    if _pipeline is not None and _model_path == model_path:
        return "loaded"

    try:
        pipe = StableDiffusionPipeline.from_pretrained(model_path)
        pipe = pipe.to(device)
    except Exception as exc:  # pragma: no cover - loading may fail
        log_error(f"[stable_diffusion_generator] load failed: {exc}")
        return f"Failed to load model: {exc}"

    _pipeline = pipe
    _model_path = model_path
    return "loaded"


def generate_image(
    prompt: str,
    model_path: str,
    *,
    device: str = "cpu",
    save_dir: str = "generated_images",
) -> str:
    """Generate an image using a local Stable Diffusion model.

    Parameters
    ----------
    prompt:
        Text prompt describing the desired image.
    model_path:
        Filesystem path to the Stable Diffusion weights.
    device:
        PyTorch device string, e.g. ``"cpu"`` or ``"cuda"``.
    save_dir:
        Directory to store generated images.

    Returns
    -------
    str
        Path to the saved image on success, otherwise an error message.
    """
    if StableDiffusionPipeline is None or torch is None:
        return f"Missing dependencies: {_IMPORT_ERROR or _TORCH_ERROR}"

    if load_model(model_path, device) != "loaded":
        return f"Failed to load model from {model_path}"

    assert _pipeline is not None
    pipe = _pipeline

    try:
        if device.startswith("cuda"):
            ctx = torch.autocast(device)
        else:
            class _NullCtx:
                def __enter__(self):
                    return None
                def __exit__(self, exc_type, exc, tb):
                    return False
            ctx = _NullCtx()

        with ctx:
            result = pipe(prompt)
        image = result.images[0]
        if not hasattr(image, "save"):
            return "Pipeline did not return an image"

        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, f"sd_image_{len(os.listdir(save_dir))+1}.png")
        image.save(filename)
        return filename
    except Exception as exc:  # pragma: no cover - safety net
        log_error(f"[stable_diffusion_generator] {exc}")
        return f"Error: {exc}"


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": "Generate images locally using Stable Diffusion.",
        "functions": ["generate_image"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Local Stable Diffusion image generation utilities."

