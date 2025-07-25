"""CUDA GPU helper utilities."""

from __future__ import annotations

try:
    import torch
except Exception as e:  # pragma: no cover - optional
    torch = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

MODULE_NAME = "gpu"

__all__ = [
    "is_available",
    "get_devices",
    "get_device",
    "autocast",
    "get_info",
    "get_description",
]


def is_available() -> bool:
    """Return ``True`` if CUDA is available."""
    return torch is not None and bool(getattr(torch.cuda, "is_available", lambda: False)())


def get_devices() -> list[str]:
    """Return list of CUDA devices like ``"cuda:0"``."""
    if not is_available():
        return []
    count = int(getattr(torch.cuda, "device_count", lambda: 0)())
    return [f"cuda:{i}" for i in range(count)]


def get_device(default: str = "cpu") -> str:
    """Return the default device string (``"cuda"`` or ``default``)."""
    return "cuda" if is_available() else default


def autocast(device: str | None = None):
    """Return a context manager for torch autocast if using CUDA."""
    if torch is None:
        class _NullCtx:
            def __enter__(self):
                return None
            def __exit__(self, exc_type, exc, tb):
                return False
        return _NullCtx()
    if device is None:
        device = get_device()
    if device.startswith("cuda"):
        return torch.autocast(device)
    class _NullCtx:
        def __enter__(self):
            return None
        def __exit__(self, exc_type, exc, tb):
            return False
    return _NullCtx()


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": "Utilities for checking CUDA availability and contexts.",
        "functions": ["is_available", "get_devices", "get_device", "autocast"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "GPU management utilities providing CUDA access information."

