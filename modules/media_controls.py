"""Media playback and volume control with multiple fallbacks.

Primary control uses the optional :mod:`keyboard` library.  If that is not
available or fails, Windows virtual key events via :mod:`ctypes` are attempted
followed by :mod:`pyautogui` presses.  This ensures media commands work even
when some dependencies are missing.
"""

import sys
from error_logger import log_error

try:  # pragma: no cover - optional runtime dependency
    import keyboard
except Exception as e:  # pragma: no cover - optional dep
    keyboard = None
    _IMPORT_ERROR = e
else:  # pragma: no cover - optional dep
    _IMPORT_ERROR = None

try:  # pragma: no cover - optional runtime dependency
    import pyautogui
except Exception:  # pragma: no cover - optional dep
    pyautogui = None

MODULE_NAME = "media_controls"

__all__ = [
    "play_pause",
    "next_track",
    "previous_track",
    "volume_up",
    "volume_down",
]

# Mapping of ``keyboard`` key names to pyautogui names and Windows VK codes
_MEDIA_KEYS = {
    "play/pause media": ("playpause", 0xB3),
    "next track": ("nexttrack", 0xB0),
    "previous track": ("prevtrack", 0xB1),
    "volume up": ("volumeup", 0xAF),
    "volume down": ("volumedown", 0xAE),
}


def _send_key_win32(vk: int) -> None:
    """Send a virtual key code using the Windows API."""
    import ctypes

    KEYEVENTF_KEYUP = 0x0002
    user32 = ctypes.windll.user32
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def _send_key(name: str) -> str:
    """Send a media key using available backends."""
    err = None
    if keyboard is not None:
        try:
            keyboard.send(name)
            return "ok"
        except Exception as e:  # pragma: no cover - OS specific
            log_error(f"[{MODULE_NAME}] keyboard send error: {e}")
            err = e

    key_info = _MEDIA_KEYS.get(name)
    if key_info and sys.platform.startswith("win"):
        try:
            _send_key_win32(key_info[1])
            return "ok"
        except Exception as e:  # pragma: no cover - OS specific
            log_error(f"[{MODULE_NAME}] win32 send error: {e}")
            if err is None:
                err = e

    if key_info and pyautogui is not None:
        try:  # pragma: no cover - simple send
            pyautogui.press(key_info[0])
            return "ok"
        except Exception as e:  # pragma: no cover - OS specific
            log_error(f"[{MODULE_NAME}] pyautogui send error: {e}")
            if err is None:
                err = e

    if keyboard is None and err is None:
        return f"keyboard module missing: {_IMPORT_ERROR}"
    return f"Error sending key: {err}" if err else "Error sending key"


def play_pause() -> str:
    """Toggle play/pause."""
    result = _send_key("play/pause media")
    return "Play/Pause pressed" if result == "ok" else result


def next_track() -> str:
    """Skip to the next track."""
    result = _send_key("next track")
    return "Next track pressed" if result == "ok" else result


def previous_track() -> str:
    """Go to the previous track."""
    result = _send_key("previous track")
    return "Previous track pressed" if result == "ok" else result


def volume_up() -> str:
    """Increase the system volume."""
    result = _send_key("volume up")
    return "Volume up pressed" if result == "ok" else result


def volume_down() -> str:
    """Decrease the system volume."""
    result = _send_key("volume down")
    return "Volume down pressed" if result == "ok" else result


def get_info():
    return {
        "name": MODULE_NAME,
        "description": "Control system media playback and volume.",
        "functions": [
            "play_pause",
            "next_track",
            "previous_track",
            "volume_up",
            "volume_down",
        ],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Send OS media keys for play/pause, track skipping and volume."


def register(registry=None):
    from module_manager import ModuleRegistry

    registry = registry or ModuleRegistry()
    registry.register(
        MODULE_NAME,
        {
            "play_pause": play_pause,
            "next_track": next_track,
            "previous_track": previous_track,
            "volume_up": volume_up,
            "volume_down": volume_down,
            "get_info": get_info,
        },
    )

# register()
