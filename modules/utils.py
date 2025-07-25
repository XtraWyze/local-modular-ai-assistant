# utils.py

import os
import sys
import re
from pathlib import Path

__all__ = ["resource_path", "project_path", "chunk_text", "clean_for_tts"]

def resource_path(relative_path: str) -> str:
    """Return absolute path for ``relative_path`` inside packaged app."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def project_path(*parts: str) -> str:
    """Return an absolute path within the project directory.

    This resolves paths relative to the repository root so modules can
    reliably access bundled data regardless of the current working
    directory.
    """
    root = Path(__file__).resolve().parents[1]
    return str(root.joinpath(*parts))

def chunk_text(text: str, max_length: int = 220) -> list[str]:
    """Split ``text`` into sentence chunks no longer than ``max_length``."""
    sentences = re.split(r'(?<=[.?!])\s+', text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) < max_length:
            current += " " + s
        else:
            if current.strip():
                chunks.append(current.strip())
            current = s
    if current.strip():
        chunks.append(current.strip())
    return chunks

def clean_for_tts(text: str) -> str:
    """Remove unsupported characters for TTS output."""
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r'[®+/=]', '', text)
    text = re.sub(r'[^a-zA-Z0-9.,?!:"\'\- \n]', '', text)
    return text
def get_info():
    """Return metadata about this module for discovery."""
    return {
        "name": "utils",
        "description": "General utility functions used across the assistant.",
        # List the functions actually provided by this module
        "functions": [
            "resource_path",
            "project_path",
            "chunk_text",
            "clean_for_tts",
        ]
    }


def get_description() -> str:
    """Return a short summary of this module."""
    return "General helper utilities for file paths and text cleaning."
