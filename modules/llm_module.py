"""Module wrapper for llm_interface."""
from llm_interface import generate_response

MODULE_NAME = "llm_module"

__all__ = ["chat"]

def chat(prompt: str, history=None, system_prompt=None):
    """Return LLM response for ``prompt``."""
    return generate_response(prompt, history=history or [], system_prompt=system_prompt)


def get_info():
    return {
        "name": MODULE_NAME,
        "description": "Interface to local LLM backend via LocalAI or text-generation-webui.",
        "functions": ["chat"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Wrapper around llm_interface for chatting with the local LLM backend."


def register(registry=None):  # pragma: no cover - simple delegation
    from module_manager import ModuleRegistry

    registry = registry or ModuleRegistry()
    registry.register(MODULE_NAME, {"chat": chat, "get_info": get_info})
