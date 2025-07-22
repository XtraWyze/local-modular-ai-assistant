"""Media playback control using Windows hotkeys."""

import sys
import ctypes

from error_logger import log_error

MODULE_NAME = "media_controls"

VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3

__all__ = [
    "play_pause",
    "stop",
    "next_track",
    "previous_track",
]


def _send_vk(code: int) -> str:
    """Send a Windows media key event."""
    if not sys.platform.startswith("win"):
        return "Media controls only supported on Windows"
    try:
        KEYEVENTF_KEYUP = 0x0002
        ctypes.windll.user32.keybd_event(code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(code, 0, KEYEVENTF_KEYUP, 0)
        return "ok"
    except Exception as e:  # pragma: no cover - OS specific
        log_error(f"[{MODULE_NAME}] key send error: {e}")
        return f"Error sending key: {e}"


def play_pause() -> str:
    """Toggle play/pause."""
    result = _send_vk(VK_MEDIA_PLAY_PAUSE)
    return "Play/Pause pressed" if result == "ok" else result


def stop() -> str:
    """Stop playback."""
    result = _send_vk(VK_MEDIA_STOP)
    return "Stop pressed" if result == "ok" else result


def next_track() -> str:
    """Skip to the next track."""
    result = _send_vk(VK_MEDIA_NEXT_TRACK)
    return "Next track pressed" if result == "ok" else result


def previous_track() -> str:
    """Go to the previous track."""
    result = _send_vk(VK_MEDIA_PREV_TRACK)
    return "Previous track pressed" if result == "ok" else result


def get_info():
    return {
        "name": MODULE_NAME,
        "description": "Control Windows media playback using system hotkeys.",
        "functions": [
            "play_pause",
            "stop",
            "next_track",
            "previous_track",
        ],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Control Windows media playback with play/pause and track skipping."


def register():
    from module_manager import ModuleRegistry

    ModuleRegistry.register(
        MODULE_NAME,
        {
            "play_pause": play_pause,
            "stop": stop,
            "next_track": next_track,
            "previous_track": previous_track,
            "get_info": get_info,
        },
    )

# register()
