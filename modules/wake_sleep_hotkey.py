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
_registered = []

__all__ = ["start_hotkeys", "trigger_wake", "trigger_sleep"]


def start_hotkeys():
    """Register the wake and sleep hotkeys using current settings."""
    return set_hotkeys(WAKE_HOTKEY, SLEEP_HOTKEY)


def set_hotkeys(wake: str, sleep: str):
    """Assign ``wake`` and ``sleep`` hotkeys and register them."""
    global WAKE_HOTKEY, SLEEP_HOTKEY
    if keyboard is None:
        return f"keyboard module missing: {_IMPORT_ERROR}"

    # remove any previously registered hotkeys
    for hk in list(_registered):
        try:
            keyboard.remove_hotkey(hk)
        except Exception:  # pragma: no cover - removal failure
            pass
        _registered.remove(hk)

    WAKE_HOTKEY = wake
    SLEEP_HOTKEY = sleep
    keyboard.add_hotkey(WAKE_HOTKEY, trigger_wake)
    keyboard.add_hotkey(SLEEP_HOTKEY, trigger_sleep)
    _registered.extend([WAKE_HOTKEY, SLEEP_HOTKEY])
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
