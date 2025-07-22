"""Media playback and volume control using the ``keyboard`` library."""

from error_logger import log_error

try:  # pragma: no cover - optional runtime dependency
    import keyboard
except Exception as e:  # pragma: no cover - optional dep
    keyboard = None
    _IMPORT_ERROR = e
else:  # pragma: no cover - optional dep
    _IMPORT_ERROR = None

MODULE_NAME = "media_controls"

__all__ = [
    "play_pause",
    "next_track",
    "previous_track",
    "volume_up",
    "volume_down",
]


def _send_key(name: str) -> str:
    """Send a media key using ``keyboard`` if available."""
    if keyboard is None:
        return f"keyboard module missing: {_IMPORT_ERROR}"
    try:
        keyboard.send(name)
        return "ok"
    except Exception as e:  # pragma: no cover - OS specific
        log_error(f"[{MODULE_NAME}] key send error: {e}")
        return f"Error sending key: {e}"


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


def register():
    from module_manager import ModuleRegistry

    ModuleRegistry.register(
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
