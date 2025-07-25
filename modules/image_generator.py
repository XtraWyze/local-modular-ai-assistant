"""Image generation utilities using external APIs like OpenAI DALL-E."""

from __future__ import annotations

import base64
import os
from typing import Optional, Tuple

import requests

try:  # optional dependency for local generation
    from diffusers import StableDiffusionPipeline
    from PIL import Image  # type: ignore
except Exception as e:  # pragma: no cover - optional
    StableDiffusionPipeline = None  # type: ignore
    Image = None  # type: ignore
    _DIFFUSERS_ERROR = e
else:  # pragma: no cover - optional
    _DIFFUSERS_ERROR = None

from error_logger import log_error
from modules.api_keys import get_api_key

MODULE_NAME = "image_generator"

__all__ = ["generate_image", "get_info", "get_description"]


def _parse_size(size: str) -> Tuple[int, int]:
    """Return ``(width, height)`` parsed from ``size`` string."""
    try:
        w, h = size.lower().split("x")
        return int(w), int(h)
    except Exception:
        return 512, 512


def _generate_openai(prompt: str, size: str, save_dir: str) -> str:
    prov = "openai"
    api_key = get_api_key(prov)
    if not api_key:
        return "Missing API key"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "n": 1,
        "size": size,
        "response_format": "b64_json",
    }
    try:
        resp = requests.post(
            "https://api.openai.com/v1/images/generations",
            json=payload,
            headers=headers,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        b64 = data.get("data", [{}])[0].get("b64_json")
        if not b64:
            return "No image data returned"
        image_bytes = base64.b64decode(b64)
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, f"image_{len(os.listdir(save_dir)) + 1}.png")
        with open(filename, "wb") as f:
            f.write(image_bytes)
        return filename
    except Exception as exc:  # pragma: no cover - network or file failure
        log_error(f"[image_generator] {exc}")
        return f"Error: {exc}"


def _generate_local(prompt: str, size: str, save_dir: str, model_id: str) -> str:
    if StableDiffusionPipeline is None:
        return f"Diffusers unavailable: {_DIFFUSERS_ERROR}"
    width, height = _parse_size(size)
    try:
        pipe = StableDiffusionPipeline.from_pretrained(model_id)
        pipe = pipe.to("cpu")
        result = pipe(prompt, height=height, width=width)
        img = result.images[0]
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, f"image_{len(os.listdir(save_dir)) + 1}.png")
        img.save(filename)
        return filename
    except Exception as exc:  # pragma: no cover - pipeline failure
        log_error(f"[image_generator.local] {exc}")
        return f"Error: {exc}"


def generate_image(
    prompt: str,
    *,
    provider: str = "openai",
    size: str = "512x512",
    save_dir: str = "generated_images",
    model_id: str = "runwayml/stable-diffusion-v1-5",
) -> str:
    """Generate an image from ``prompt`` and save it locally.

    Parameters
    ----------
    prompt:
        Text description of the desired image.
    provider:
        ``"openai"`` for DALL·E or ``"diffusers"`` for a local Stable Diffusion model.
    size:
        Image resolution string, e.g. ``"512x512"``.
    save_dir:
        Folder to store generated images.
    model_id:
        Model identifier passed to ``diffusers`` when ``provider='diffusers'``.

    Returns
    -------
    str
        Path to the saved image on success, otherwise an error message.
    """
    prov = provider.lower()
    if prov in {"openai", "dall-e"}:
        return _generate_openai(prompt, size, save_dir)
    if prov in {"diffusers", "local"}:
        return _generate_local(prompt, size, save_dir, model_id)
    return f"Provider '{provider}' not supported"


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": (
            "Generate images from text prompts using DALL-E or a local"
            " Stable Diffusion pipeline."
        ),
        "functions": ["generate_image"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Utilities to create images from text prompts via OpenAI or diffusers."
