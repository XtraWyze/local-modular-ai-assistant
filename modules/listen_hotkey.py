"""Hotkey to toggle assistant listening state."""

try:
    import keyboard
except Exception as e:  # pragma: no cover - optional dependency
    keyboard = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

from assistant import is_listening, set_listening, cancel_processing
from modules.tts_manager import stop_speech

HOTKEY = 'alt+/'

__all__ = ["start_hotkey", "trigger"]


def start_hotkey():
    """Register the listening toggle hotkey."""
    if keyboard is None:
        return f"keyboard module missing: {_IMPORT_ERROR}"
    keyboard.add_hotkey(HOTKEY, trigger)
    return f"Hotkey {HOTKEY} registered"


def trigger():
    """Toggle listening; stop tasks if already listening."""
    if is_listening():
        stop_speech()
        cancel_processing()
        set_listening(False)
    else:
        set_listening(True)


def get_description() -> str:
    """Return a short description of this module."""
    return "Registers a hotkey to start or cancel voice listening."
