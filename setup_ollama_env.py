#!/usr/bin/env python
"""Create a virtual environment for running Ollama tools.

This script installs only the packages required to interact with an Ollama
server using its Python SDK. The environment is placed in ``ollama_env/``.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

VENV_DIR = Path("ollama_env")
DEPS = ["ollama"]


def _run(cmd: list[str]) -> None:
    """Run a shell command and exit on failure."""
    print(" ".join(cmd))
    subprocess.check_call(cmd)


def _python_exe() -> Path:
    """Return the Python executable within the virtual environment."""
    name = "python.exe" if os.name == "nt" else "python"
    folder = "Scripts" if os.name == "nt" else "bin"
    return VENV_DIR / folder / name


def create_venv() -> None:
    """Create the virtual environment if it does not exist."""
    if not VENV_DIR.exists():
        _run([sys.executable, "-m", "venv", str(VENV_DIR)])


def install_deps() -> None:
    """Install Ollama Python bindings inside the virtual environment."""
    py = _python_exe()
    _run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    _run([str(py), "-m", "pip", "install"] + DEPS)


def main() -> None:
    """Entry point for command-line usage."""
    create_venv()
    install_deps()
    activate = (
        f"{VENV_DIR}\\Scripts\\activate" if os.name == "nt" else f"source {VENV_DIR}/bin/activate"
    )
    print("\nEnvironment ready. Activate with:\n" + activate)
    print("Run your Ollama scripts using this Python interpreter.")


if __name__ == "__main__":  # pragma: no cover - manual usage
    main()
