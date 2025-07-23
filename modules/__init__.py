"""Built-in plugin modules for the assistant."""

from importlib import import_module

# Ensure skills subpackage is available
try:
    import_module("modules.skills")
except Exception:  # pragma: no cover - skills may not exist yet
    pass


def get_description() -> str:
    """Return a short description of this package."""
    return "Collection of core modules providing automation, voice, and utility features."
