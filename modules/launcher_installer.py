"""Download and install game launchers from the web."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

try:
    import requests
except Exception as e:  # pragma: no cover - optional dependency
    requests = None  # type: ignore
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

import webbrowser

MODULE_NAME = "launcher_installer"
LAUNCHERS_FILE = "learned_launchers.json"
EPIC_URL = (
    "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/installer/download/"
    "EpicGamesLauncherInstaller.msi"
)

__all__ = [
    "browse",
    "register_launcher",
    "install_launcher",
    "install_epic_launcher",
    "get_description",
]


def _load_launchers() -> Dict[str, str]:
    if os.path.isfile(LAUNCHERS_FILE):
        with open(LAUNCHERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_launchers(data: Dict[str, str]) -> None:
    with open(LAUNCHERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def browse(url: str) -> str:
    """Open ``url`` in the user's default browser."""
    webbrowser.open(url)
    return f"opened {url}"


def register_launcher(name: str, url: str) -> str:
    """Remember ``url`` for launcher ``name`` in ``LAUNCHERS_FILE``."""
    data = _load_launchers()
    data[name] = url
    _save_launchers(data)
    return f"registered {name}"


def _download_file(url: str, dest: Path, timeout: int = 60) -> Path:
    if requests is None:
        raise ImportError(_IMPORT_ERROR)
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    return dest


def _install_file(path: Path) -> str:
    if sys.platform.startswith("win"):
        try:
            subprocess.run([str(path)], check=True)
            return "installed"
        except Exception as exc:  # pragma: no cover - installation failure
            return f"install failed: {exc}"
    return f"downloaded to {path}"  # manual install for non-Windows


def install_launcher(name: str, dest_dir: str = ".") -> str:
    """Download and run the launcher identified by ``name``."""
    data = _load_launchers()
    url = data.get(name)
    if not url:
        return f"no launcher named {name}"
    dest = Path(dest_dir) / Path(url).name
    try:
        _download_file(url, dest)
        return _install_file(dest)
    except Exception as exc:  # pragma: no cover - network failure
        return f"error: {exc}"


def install_epic_launcher(dest_dir: str = ".") -> str:
    """Download and install the Epic Games Launcher."""
    register_launcher("epic", EPIC_URL)
    return install_launcher("epic", dest_dir)


def get_description() -> str:
    return "Downloads and installs game launchers like Epic Games."

