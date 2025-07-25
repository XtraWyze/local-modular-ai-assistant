"""Image generation utilities using external APIs like OpenAI DALL-E."""

from __future__ import annotations

import base64
import os
from typing import Optional

import requests

from error_logger import log_error
from modules.api_keys import get_api_key

MODULE_NAME = "image_generator"

__all__ = ["generate_image", "get_info", "get_description"]


def generate_image(
    prompt: str,
    *,
    provider: str = "openai",
    model: str = "dall-e-3",
    size: str = "512x512",
    save_dir: str = "generated_images",
) -> str:
    """Generate an image from ``prompt`` and save it locally.

    Parameters
    ----------
    prompt:
        Text description of the desired image.
    provider:
        API provider identifier. Currently only ``"openai"`` is supported.
    model:
        Model identifier for the provider, e.g. ``"dall-e-3"``.
    size:
        Image resolution string (for providers that support it), e.g. ``"512x512"``.
    save_dir:
        Folder to store generated images.

    Returns
    -------
    str
        Path to the saved image on success, otherwise an error message.
    """
    prov = provider.lower()
    if prov != "openai":
        return f"Provider '{provider}' not supported"

    api_key = get_api_key(prov)
    if not api_key:
        return "Missing API key"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "model": model,
        "n": 1,
        "size": size,
        "response_format": "b64_json",
    }
    try:
        resp = requests.post("https://api.openai.com/v1/images/generations", json=payload, headers=headers, timeout=60)
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


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": "Generate images from text prompts using DALL-E or similar APIs.",
        "functions": ["generate_image"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Utilities to create images from text prompts via external APIs."
