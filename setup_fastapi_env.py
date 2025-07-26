#!/usr/bin/env python
"""Create a lightweight virtual environment for the FastAPI server."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

VENV_DIR = Path("api_env")
DEPS = ["fastapi", "uvicorn[standard]"]


def _run(cmd: list[str]) -> None:
    print(" ".join(cmd))
    subprocess.check_call(cmd)


def _python_exe() -> Path:
    name = "python.exe" if os.name == "nt" else "python"
    folder = "Scripts" if os.name == "nt" else "bin"
    return VENV_DIR / folder / name


def create_venv() -> None:
    if not VENV_DIR.exists():
        _run([sys.executable, "-m", "venv", str(VENV_DIR)])


def install_deps() -> None:
    py = _python_exe()
    _run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    _run([str(py), "-m", "pip", "install"] + DEPS)


def main() -> None:
    create_venv()
    install_deps()
    activate = (
        f"{VENV_DIR}\\Scripts\\activate" if os.name == "nt" else f"source {VENV_DIR}/bin/activate"
    )
    print("\nEnvironment ready. Activate with:\n" + activate)
    print("Then run: uvicorn your_module:app --reload")


if __name__ == "__main__":  # pragma: no cover - manual usage
    main()
