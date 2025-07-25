"""Manage user-defined command macros.

This module allows recording sequences of text commands
and replaying them later. Macros are stored in
``command_macros.json`` in the current working directory.
"""

from __future__ import annotations

import json
import os
from typing import Callable, Dict, List, Optional

FILE_PATH = "command_macros.json"

_current_name: Optional[str] = None
_current_commands: List[str] = []

__all__ = [
    "start_recording",
    "record_command",
    "stop_recording",
    "is_recording",
    "list_macros",
    "run_macro",
    "edit_macro",
    "get_description",
]


def _load() -> Dict[str, List[str]]:
    if os.path.isfile(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save(data: Dict[str, List[str]]) -> None:
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def start_recording(name: str) -> str:
    """Begin recording a macro named ``name``."""
    global _current_name, _current_commands
    if _current_name:
        return f"Already recording macro {_current_name}"
    _current_name = name.strip()
    _current_commands = []
    return f"Recording macro '{_current_name}'. Say 'stop macro' to finish."


def record_command(cmd: str) -> None:
    """Append ``cmd`` to the current macro if recording."""
    if _current_name:
        _current_commands.append(cmd.strip())


def stop_recording() -> str:
    """Stop recording and persist the macro."""
    global _current_name, _current_commands
    if not _current_name:
        return "Not currently recording"
    data = _load()
    data[_current_name] = _current_commands
    _save(data)
    name = _current_name
    _current_name = None
    _current_commands = []
    return f"Saved macro '{name}'"


def is_recording() -> bool:
    return _current_name is not None


def list_macros() -> List[str]:
    """Return names of saved command macros."""
    return list(_load().keys())


def run_macro(name: str, executor: Callable[[str], str | None]) -> str:
    """Execute each command in macro ``name`` using ``executor``."""
    data = _load()
    cmds = data.get(name)
    if not cmds:
        return f"Macro '{name}' not found"
    for cmd in cmds:
        executor(cmd)
    return f"Ran macro '{name}'"


def edit_macro(name: str, commands: List[str]) -> str:
    """Replace ``name`` macro with ``commands``."""
    data = _load()
    if name not in data:
        return f"Macro '{name}' not found"
    data[name] = [c.strip() for c in commands]
    _save(data)
    return f"Updated macro '{name}'"


def get_description() -> str:
    return "Record and run text command macros."
