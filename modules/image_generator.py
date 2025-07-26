"""Image generation utilities using external APIs like OpenAI DALL-E."""

from __future__ import annotations

import base64
import os
from typing import Optional

import importlib
import types

try:
    import openai  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    openai = types.SimpleNamespace(
        Image=types.SimpleNamespace(create=lambda **_k: None),
    )

from error_logger import log_error
from modules.api_keys import get_api_key
from modules.utils import project_path

MODULE_NAME = "image_generator"

__all__ = [
    "generate_image",
    "generate_image_url",
    "get_info",
    "get_description",
]


def generate_image(
    prompt: str,
    *,
    provider: str = "openai",
    model: str = "dall-e-3",
    size: str = "512x512",
    save_dir: str = "generated_images",
    name: str | None = None,
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
        Folder within the project directory to store generated images. If an
        absolute path is provided it will be used as-is.
    name:
        Optional file name for the image without extension. Invalid characters
        are stripped and ``.png`` is appended.

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
        requests = importlib.import_module("requests")
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
        if not os.path.isabs(save_dir):
            save_dir = project_path(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        if name:
            safe = "".join(c for c in name if c.isalnum() or c in "-_")
            filename = os.path.join(save_dir, f"{safe}.png")
        else:
            filename = os.path.join(
                save_dir,
                f"image_{len(os.listdir(save_dir)) + 1}.png",
            )
        with open(filename, "wb") as f:
            f.write(image_bytes)
        return filename
    except Exception as exc:  # pragma: no cover - network or file failure
        log_error(f"[image_generator] {exc}")
        return f"Error: {exc}"


def generate_image_url(
    prompt: str,
    *,
    provider: str = "openai",
    model: str = "dall-e-3",
    size: str = "512x512",
) -> str:
    """Generate an image and return the direct URL instead of saving locally."""
    prov = provider.lower()
    if prov != "openai":
        return f"Provider '{provider}' not supported"

    api_key = get_api_key(prov)
    if not api_key:
        return "Missing API key"

    try:
        if hasattr(openai, "OpenAI") and callable(getattr(openai, "OpenAI", None)):
            client = openai.OpenAI(api_key=api_key)
            resp = client.images.generate(
                prompt=prompt,
                model=model,
                n=1,
                size=size,
            )
            return resp.data[0].url
        if hasattr(openai, "Image") and hasattr(openai.Image, "create"):
            resp = openai.Image.create(prompt=prompt, n=1, size=size)
            return resp["data"][0]["url"]
        return "OpenAI package unavailable"
    except Exception as exc:  # pragma: no cover - network failure
        log_error(f"[image_generator] {exc}")
        if not api_key:
            return "Missing API key"
        return f"Error: {exc}"


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": "Generate images from text prompts using DALL-E or similar APIs.",
        "functions": ["generate_image", "generate_image_url"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Utilities to create images from text prompts via external APIs."
