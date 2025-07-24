"""Hotkeys to wake or sleep the assistant."""

try:
    import keyboard
except Exception as e:  # pragma: no cover - optional dependency
    keyboard = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

from assistant import is_listening, set_listening, cancel_processing
from modules.tts_manager import stop_speech

WAKE_HOTKEY = 'ctrl+shift+w'
SLEEP_HOTKEY = 'ctrl+shift+s'

__all__ = ["start_hotkeys", "trigger_wake", "trigger_sleep"]


def start_hotkeys():
    """Register the wake and sleep hotkeys."""
    if keyboard is None:
        return f"keyboard module missing: {_IMPORT_ERROR}"
    keyboard.add_hotkey(WAKE_HOTKEY, trigger_wake)
    keyboard.add_hotkey(SLEEP_HOTKEY, trigger_sleep)
    return f"Hotkeys {WAKE_HOTKEY}, {SLEEP_HOTKEY} registered"


def trigger_wake():
    """Wake the assistant if currently sleeping."""
    if not is_listening():
        set_listening(True)


def trigger_sleep():
    """Put the assistant to sleep and cancel active tasks."""
    if is_listening():
        stop_speech()
        cancel_processing()
        set_listening(False)


def get_description() -> str:
    """Return a short description of this module."""
    return "Hotkeys for waking or sleeping the assistant."
