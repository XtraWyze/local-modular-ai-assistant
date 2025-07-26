"""System volume utilities using pycaw."""

import sys
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import (
    IAudioEndpointVolume,
    MMDeviceEnumerator,
    EDataFlow,
    ERole,
)

from error_logger import log_error

MODULE_NAME = "system_volume"

__all__ = ["set_volume", "get_volume"]


def _get_endpoint():
    """Return the IAudioEndpointVolume interface for the default device."""
    enumerator = MMDeviceEnumerator()
    device = enumerator.GetDefaultAudioEndpoint(
        EDataFlow.eRender, ERole.eMultimedia
    )
    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


def set_volume(percent: int) -> str:
    """Set master volume to ``percent`` (0-100)."""
    try:
        value = int(percent)
        assert 0 <= value <= 100
    except Exception:
        return "Volume must be 0-100"

    if not sys.platform.startswith("win"):
        return "Volume control only supported on Windows"

    try:
        endpoint = _get_endpoint()
        endpoint.SetMasterVolumeLevelScalar(value / 100.0, None)
        return f"Volume set to {value}%"
    except Exception as e:  # pragma: no cover - OS specific
        log_error(f"[{MODULE_NAME}] set_volume error: {e}")
        return f"Error setting volume: {e}"


def get_volume() -> int:
    """Return current master volume level as an integer percentage."""
    if not sys.platform.startswith("win"):
        return 0
    try:
        endpoint = _get_endpoint()
        level = endpoint.GetMasterVolumeLevelScalar()
        return int(level * 100)
    except Exception as e:  # pragma: no cover - OS specific
        log_error(f"[{MODULE_NAME}] get_volume error: {e}")
        return 0


def get_info():
    """Return module metadata."""
    return {
        "name": MODULE_NAME,
        "description": "Get or set the system volume.",
        "functions": ["set_volume", "get_volume"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Control the system master volume level."


def register(registry=None):
    """Register this module with ``ModuleRegistry``."""
    from module_manager import ModuleRegistry

    registry = registry or ModuleRegistry()
    registry.register(
        MODULE_NAME,
        {
            "set_volume": set_volume,
            "get_volume": get_volume,
            "get_info": get_info,
        },
    )

# register()
