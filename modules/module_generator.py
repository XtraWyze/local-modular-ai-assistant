"""Generate new assistant modules using OpenAI Codex."""

from __future__ import annotations

import os
import time
from typing import Optional

from error_logger import log_error
from module_manager import ModuleRegistry
from modules.codex_integration import CodexClient

MODULE_NAME = "module_generator"

__all__ = [
    "generate_module",
    "generate_module_interactive",
    "save_module_code",
    "get_info",
    "get_description",
]


def generate_module(description: str, name: Optional[str] = None, provider: str = "openai") -> str:
    """Generate a Python module via Codex.

    Parameters
    ----------
    description:
        Plain English description of what the module should do.
    name:
        Optional module name. A timestamped name is used if omitted.

    Returns
    -------
    str
        Path to the generated module on success, otherwise an error message.
    """

    prompt = (
        "Create a Python module for my local AI assistant. The module should "
        f"{description}. Provide only code."
    )
    try:
        client = CodexClient(provider=provider)
        code = client.generate_code(prompt)
        if not code:
            return "No code returned"
        module_name = name or f"codex_module_{int(time.time())}"
        module_path = os.path.join("modules", f"{module_name}.py")
        os.makedirs("modules", exist_ok=True)
        with open(module_path, "w", encoding="utf-8") as f:
            f.write(code)
        if os.getcwd() not in os.sys.path:
            os.sys.path.insert(0, os.getcwd())
        ModuleRegistry().auto_discover("modules")
        return module_path
    except Exception as exc:  # pragma: no cover - network or file failure
        log_error(f"[module_generator] failed: {exc}")
        return f"Error: {exc}"


def generate_module_interactive(description: str, name: Optional[str] = None, provider: str = "openai") -> str:
    """Generate a module with preview and confirmation.

    This helper prints the generated code to the console and prompts the
    user to confirm before saving the file and loading the module.

    Parameters
    ----------
    description:
        Plain English description of what the module should do.
    name:
        Optional module name. A timestamped name is used if omitted.

    Returns
    -------
    str
        Path to the generated module on success, otherwise a message
        indicating cancellation or error.
    """

    prompt = (
        "Create a Python module for my local AI assistant. The module should "
        f"{description}. Provide only code."
    )
    try:
        client = CodexClient(provider=provider)
        code = client.generate_code(prompt)
        if not code:
            return "No code returned"

        print("=== Module Preview ===")
        print(code)
        confirm = input("Save this module? (y/n): ").strip().lower()
        if not confirm.startswith("y"):
            return "Generation cancelled."

        module_name = name or f"codex_module_{int(time.time())}"
        module_path = os.path.join("modules", f"{module_name}.py")
        os.makedirs("modules", exist_ok=True)
        with open(module_path, "w", encoding="utf-8") as f:
            f.write(code)
        if os.getcwd() not in os.sys.path:
            os.sys.path.insert(0, os.getcwd())
        ModuleRegistry().auto_discover("modules")
        return module_path
    except Exception as exc:  # pragma: no cover - network or file failure
        log_error(f"[module_generator] interactive failed: {exc}")
        return f"Error: {exc}"


def save_module_code(code: str, name: Optional[str] = None) -> str:
    """Save a generated module ``code`` and load it."""

    try:
        module_name = name or f"codex_module_{int(time.time())}"
        module_path = os.path.join("modules", f"{module_name}.py")
        os.makedirs("modules", exist_ok=True)
        with open(module_path, "w", encoding="utf-8") as f:
            f.write(code)
        if os.getcwd() not in os.sys.path:
            os.sys.path.insert(0, os.getcwd())
        ModuleRegistry().auto_discover("modules")
        return module_path
    except Exception as exc:  # pragma: no cover - file failure
        log_error(f"[module_generator] save failed: {exc}")
        return f"Error: {exc}"


def get_info() -> dict:
    """Return metadata about this module."""
    return {
        "name": MODULE_NAME,
        "description": "Generates new modules on demand using Codex.",
        "functions": [
            "generate_module",
            "generate_module_interactive",
            "save_module_code",
        ],
    }


def get_description() -> str:
    """Short summary describing the module."""
    return "Utilities for generating assistant modules using OpenAI Codex."
