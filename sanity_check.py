"""Module import sanity checker for the Local Modular AI Assistant.

This script attempts to import a list of core modules and prints the result for
each. It is useful during development to ensure that optional dependencies are
available and that there are no syntax errors preventing imports.
"""

from __future__ import annotations

import importlib
import sys
from typing import Iterable


MODULES: list[str] = [
    "assistant",
    "orchestrator",
    "android_gui_app",
    "android_cli_assistant",
    "build_apk",
    "cleanup",
    "vision_tools",
    "memory_tools",
    "voice_control",
    "macros",
    "tools",
    "gui_assistant",
    "cli_assistant",
]


def check_module(name: str) -> str:
    """Import ``name`` and return a human friendly status string."""
    try:
        importlib.import_module(name)
    except ImportError as exc:  # module not found or optional dependency missing
        return f"\u274c {name}: {exc}"
    except Exception as exc:  # pragma: no cover - unpredictable errors
        return f"\u26a0\ufe0f {name}: {exc}"
    return f"\u2705 {name}"


def run_checks(mod_names: Iterable[str]) -> None:
    """Attempt to import each module and print a status line."""
    for mod in mod_names:
        print(check_module(mod))


def main() -> None:
    """Entry point for command-line execution."""
    run_checks(MODULES)


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
