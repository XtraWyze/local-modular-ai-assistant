"""Unified interface for cloud and local image generation."""

from __future__ import annotations

from typing import Optional, Callable

from error_logger import log_error

from . import image_generator as ig
from . import stable_diffusion_generator as sd

MODULE_NAME = "imagine_generator"

_gui_callback: Callable[..., str] | None = None

def set_gui_callback(func: Callable[..., str] | None) -> None:
    """Register a GUI callback for real-time image generation."""
    global _gui_callback
    _gui_callback = func

__all__ = ["imagine", "get_info", "get_description", "set_gui_callback"]


def imagine(
    prompt: str,
    *,
    source: str = "cloud",
    model: str = "dall-e-3",
    size: str = "512x512",
    save_dir: str = "generated_images",
    name: str | None = None,
    sd_model_path: str | None = None,
    device: str | None = None,
) -> str:
    """Generate an image using the specified backend.

    Parameters
    ----------
    prompt:
        Text description of the desired image.
    source:
        ``"cloud"`` uses :mod:`modules.image_generator`.
        ``"local"`` uses :mod:`modules.stable_diffusion_generator`.
    model:
        Model identifier for the cloud provider.
    size:
        Image resolution for the cloud provider.
    save_dir:
        Directory to store the generated image.
    name:
        Optional file name for the image without extension. Invalid characters
        are stripped and ``.png`` is appended.
    sd_model_path:
        Path to the Stable Diffusion model when ``source`` is ``"local"``.
    device:
        Torch device string for local generation.
    """
    if _gui_callback is not None:
        try:
            return _gui_callback(
                prompt,
                source=source,
                model=model,
                size=size,
                save_dir=save_dir,
                name=name,
                sd_model_path=sd_model_path,
                device=device,
            )
        except Exception as exc:  # pragma: no cover - callback failures
            log_error(f"[imagine_generator] gui callback error: {exc}")

    if source == "local":
        if not sd_model_path:
            return "Stable Diffusion model path required"
        return sd.generate_image(
            prompt,
            sd_model_path,
            device=device,
            save_dir=save_dir,
            name=name,
        )
    return ig.generate_image(
        prompt,
        model=model,
        size=size,
        save_dir=save_dir,
        name=name,
    )


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": get_description(),
        "functions": ["imagine"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Generate images via cloud APIs or local Stable Diffusion."
