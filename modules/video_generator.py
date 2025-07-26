"""Video generation utilities using cloud Veo3 or local Stable Video Diffusion."""

from __future__ import annotations

import base64
import importlib
import os
from typing import Optional

from error_logger import log_error
from modules.api_keys import get_api_key
from modules.utils import project_path
from modules import gpu

try:
    from diffusers import StableVideoDiffusionPipeline
except Exception as e:  # pragma: no cover - optional dependency
    StableVideoDiffusionPipeline = None
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

MODULE_NAME = "video_generator"

__all__ = ["generate_video", "load_local_model", "get_info", "get_description"]

_pipeline: Optional[StableVideoDiffusionPipeline] = None
_model_path: str | None = None


def load_local_model(model_path: str, device: str | None = None) -> str:
    """Load a Stable Video Diffusion pipeline from ``model_path``."""
    global _pipeline, _model_path

    if StableVideoDiffusionPipeline is None or torch is None:
        return f"Missing dependencies: {_IMPORT_ERROR or _TORCH_ERROR}"

    if device is None:
        device = gpu.get_device()

    if _pipeline is not None and _model_path == model_path:
        return "loaded"

    try:
        pipe = StableVideoDiffusionPipeline.from_pretrained(model_path)
        pipe = pipe.to(device)
    except Exception as exc:  # pragma: no cover - model loading may fail
        log_error(f"[video_generator] load failed: {exc}")
        return f"Failed to load model: {exc}"

    _pipeline = pipe
    _model_path = model_path
    return "loaded"


def _save_gif(frames, filename: str, fps: int) -> None:
    if not frames:
        raise ValueError("No frames returned")
    frames[0].save(
        filename,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / max(1, fps)),
        loop=0,
    )


def _generate_local(
    prompt: str,
    model_path: str,
    *,
    device: str | None = None,
    num_frames: int = 16,
    fps: int = 8,
    save_dir: str = "generated_videos",
    name: str | None = None,
) -> str:
    if StableVideoDiffusionPipeline is None or torch is None:
        return f"Missing dependencies: {_IMPORT_ERROR or _TORCH_ERROR}"

    if device is None:
        device = gpu.get_device()

    if load_local_model(model_path, device) != "loaded":
        return f"Failed to load model from {model_path}"

    assert _pipeline is not None
    pipe = _pipeline

    try:
        ctx = gpu.autocast(device)
        with ctx:
            result = pipe(prompt, num_frames=num_frames)
        frames = getattr(result, "frames", None) or result
        if not os.path.isabs(save_dir):
            save_dir = project_path(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        if name:
            safe = "".join(c for c in name if c.isalnum() or c in "-_")
            filename = os.path.join(save_dir, f"{safe}.gif")
        else:
            filename = os.path.join(
                save_dir,
                f"video_{len(os.listdir(save_dir)) + 1}.gif",
            )
        _save_gif(frames, filename, fps)
        return filename
    except Exception as exc:  # pragma: no cover - generation failure
        log_error(f"[video_generator] {exc}")
        return f"Error: {exc}"


def _generate_cloud(
    prompt: str,
    *,
    model: str = "veo-3",
    num_frames: int = 16,
    fps: int = 8,
    save_dir: str = "generated_videos",
    name: str | None = None,
) -> str:
    api_key = get_api_key("veo3")
    if not api_key:
        return "Missing API key"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "model": model,
        "frames": num_frames,
        "fps": fps,
    }
    try:
        requests = importlib.import_module("requests")
        resp = requests.post(
            "https://api.veocloud.ai/v1/generate",  # fictional endpoint
            json=payload,
            headers=headers,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        b64 = data.get("video")
        if not b64:
            return "No video data returned"
        video_bytes = base64.b64decode(b64)
        if not os.path.isabs(save_dir):
            save_dir = project_path(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        if name:
            safe = "".join(c for c in name if c.isalnum() or c in "-_")
            filename = os.path.join(save_dir, f"{safe}.mp4")
        else:
            filename = os.path.join(save_dir, f"video_{len(os.listdir(save_dir)) + 1}.mp4")
        with open(filename, "wb") as f:
            f.write(video_bytes)
        return filename
    except Exception as exc:  # pragma: no cover - network failure
        log_error(f"[video_generator] {exc}")
        return f"Error: {exc}"


def generate_video(
    prompt: str,
    *,
    source: str = "cloud",
    model: str = "veo-3",
    num_frames: int = 16,
    fps: int = 8,
    save_dir: str = "generated_videos",
    local_model_path: str | None = None,
    device: str | None = None,
    name: str | None = None,
) -> str:
    """Generate a video from ``prompt`` using either cloud or local backend."""
    if source == "local":
        if not local_model_path:
            return "Local model path required"
        return _generate_local(
            prompt,
            local_model_path,
            device=device,
            num_frames=num_frames,
            fps=fps,
            save_dir=save_dir,
            name=name,
        )
    return _generate_cloud(
        prompt,
        model=model,
        num_frames=num_frames,
        fps=fps,
        save_dir=save_dir,
        name=name,
    )


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": get_description(),
        "functions": ["generate_video"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Create videos from text using cloud Veo3 or local Stable Video Diffusion."

