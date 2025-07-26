"""Voice macro learning system for assistant commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, List, Iterable

from error_logger import log_error

MACRO_DIR = "macros"

__all__ = ["learn_macro", "run_macro"]


def learn_macro(
    get_command: Callable[[], str],
    steps: int = 5,
    on_prompt: Callable[[str], None] | None = None,
) -> Path | None:
    """Record ``steps`` commands using ``get_command`` and save as a macro.

    Parameters
    ----------
    get_command:
        Callable returning the next command string from the assistant.
    steps:
        Number of commands to record before asking for the macro name.
    on_prompt:
        Optional callback to present prompts to the user (e.g. TTS or print).

    Returns
    -------
    Path | None
        Path to the saved macro file or ``None`` if cancelled.
    """
    cmds: List[str] = []
    for _ in range(steps):
        cmd = get_command().strip()
        if cmd.lower() == "cancel":
            if on_prompt:
                on_prompt("Macro recording cancelled.")
            return None
        cmds.append(cmd)
    if on_prompt:
        on_prompt("Please provide a name for this macro or say cancel.")
    name = get_command().strip()
    if not name or name.lower() == "cancel":
        if on_prompt:
            on_prompt("Macro recording cancelled.")
        return None
    Path(MACRO_DIR).mkdir(exist_ok=True)
    path = Path(MACRO_DIR) / f"{name}.json"
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cmds, f, indent=2)
    except Exception as exc:  # pragma: no cover - disk errors
        log_error(f"[macro_learning] failed to save {name}: {exc}")
        return None
    if on_prompt:
        on_prompt(f"Saved macro {name}.")
    return path


def run_macro(name: str, executor: Callable[[str], None]) -> str:
    """Run macro ``name`` executing each command via ``executor``."""
    path = Path(MACRO_DIR) / f"{name}.json"
    if not path.exists():
        return f"Macro '{name}' not found"
    try:
        with open(path, "r", encoding="utf-8") as f:
            commands: Iterable[str] = json.load(f)
    except Exception as exc:  # pragma: no cover - json errors
        log_error(f"[macro_learning] failed to load {name}: {exc}")
        return f"Error running macro {name}"
    for cmd in commands:
        executor(cmd)
    return f"Ran macro {name}"
