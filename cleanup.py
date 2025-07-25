"""Remove cached files and logs from the repository."""
from __future__ import annotations

import shutil
from pathlib import Path

from error_logger import log_error

STATE_FILES = [
    "assistant_memory.json",
    "assistant_state.json",
    "learned_actions.json",
    "learned_macros.yaml",
    "learned_launchers.json",
]

PATTERNS = [
    "**/__pycache__",
    "**/*.py[cod]",
    "**/*.log",
    "**/*.db",
    ".pytest_cache",
]


def remove_path(path: Path) -> None:
    """Delete a file or directory if it exists."""
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)
        print(f"Removed {path}")
    except Exception as exc:  # pragma: no cover - unlikely
        log_error("Failed to remove", context=str(path))
        print(f"Failed to remove {path}: {exc}")


def cleanup(repo_dir: Path) -> None:
    """Remove cache directories, logs, and state files under ``repo_dir``."""
    for pattern in PATTERNS:
        for p in repo_dir.glob(pattern):
            remove_path(p)
    for name in STATE_FILES:
        target = repo_dir / name
        if target.exists():
            remove_path(target)


def main() -> None:
    cleanup(Path(__file__).resolve().parent)


if __name__ == "__main__":
    main()
