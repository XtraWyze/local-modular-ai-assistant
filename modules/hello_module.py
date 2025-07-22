"""
hello_module.py
A minimal sample module for plug-in auto-discovery!
"""

__all__ = ["say_hello"]

def initialize(config=None) -> None:
    """Initialize the sample module."""
    print("[hello_module] Initialized with config:", config)

def say_hello(name: str = "World") -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}!"

def shutdown() -> None:
    """Clean up module resources."""
    print("[hello_module] Shutdown called.")


def get_info():
    return {
        "name": "hello_module",
        "description": "Example plugin for testing module discovery.",
        "functions": ["say_hello"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "A minimal example plugin that says hello."


def register():
    from module_manager import ModuleRegistry
    ModuleRegistry.register("hello_module", {"say_hello": say_hello, "get_info": get_info})

