"""Global hotkey to cancel assistant speech and tasks."""

try:
    import keyboard
except Exception as e:  # pragma: no cover - optional dep
    keyboard = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

from assistant import cancel_processing
from modules.tts_manager import stop_speech

HOTKEY = 'ctrl+shift+c'

__all__ = ["start_hotkey", "trigger"]


def start_hotkey():
    if keyboard is None:
        return f"keyboard module missing: {_IMPORT_ERROR}"
    keyboard.add_hotkey(HOTKEY, trigger)
    return f"Hotkey {HOTKEY} registered"


def trigger():
    stop_speech()
    cancel_processing()


def get_description() -> str:
    return "Registers a global hotkey to interrupt speech and cancel tasks."
