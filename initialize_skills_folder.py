"""Utility to ensure the skills folder exists on startup."""

from __future__ import annotations

from pathlib import Path

from error_logger import log_info, log_error

__all__ = ["initialize_skills_folder"]


def initialize_skills_folder(path: str | Path = "skills") -> None:
    """Create the skills folder with example files if missing."""
    skills_path = Path(path)
    if skills_path.exists():
        return
    try:
        skills_path.mkdir(parents=True, exist_ok=True)
        (skills_path / "__init__.py").write_text("\n")
        (skills_path / "example_skill.py").write_text(
            """__all__=['hello']\n
def hello():\n    return 'hello world'\n"""
        )
        log_info("Skills folder initialized.")
    except Exception as exc:  # pragma: no cover - filesystem errors
        log_error(
            f"[initialize_skills_folder] failed to create skills folder: {exc}"
        )

