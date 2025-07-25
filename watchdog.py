"""Automatic restart decorator for critical loops/functions."""

from functools import wraps
import time
from typing import Callable, Any, Optional

from error_logger import log_error


def watchdog(
    delay: float = 1.0,
    phrase: str = "Restarting module due to error",
    speak_func: Optional[Callable[[str], Any]] = None,
):
    """Return a decorator that restarts ``func`` if it crashes.

    Parameters
    ----------
    delay : float, optional
        Seconds to wait before restarting after an error.
    phrase : str, optional
        Message announced via ``speak_func`` when restarting.
    speak_func : Callable[[str], Any], optional
        Text-to-speech function used to announce restarts.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:  # pragma: no cover - runtime depends on user func
                    log_error(f"[watchdog:{func.__name__}] {exc}")
                    if speak_func:
                        try:
                            speak_func(phrase)
                        except Exception as speak_exc:  # pragma: no cover - speak may fail
                            log_error(f"[watchdog:speak] {speak_exc}")
                    time.sleep(delay)
        return wrapper

    return decorator


def get_description() -> str:
    """Return description string for discovery."""

    return (
        "Decorator that restarts a function after logging errors and announcing via TTS."
    )

