"""Utility helpers for Hugging Face features."""

from __future__ import annotations

import socket

MODULE_NAME = "hf_utils"

__all__ = ["has_internet", "get_description", "get_info"]


def has_internet(host: str = "huggingface.co", port: int = 443, timeout: int = 3) -> bool:
    """Return ``True`` if ``host`` is reachable over TCP."""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": "Utility helpers for checking network connectivity.",
        "functions": ["has_internet"],
    }


def get_description() -> str:
    """Return short description."""
    return "Simple utilities for Hugging Face integrations."
