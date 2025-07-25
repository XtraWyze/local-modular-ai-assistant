"""Utility decorator to restart functions if they crash."""

from __future__ import annotations

import functools
import time
import traceback
from typing import Callable, TypeVar, Any

from error_logger import log_error

F = TypeVar("F", bound=Callable[..., Any])


def watchdog(max_restarts: int = 3, delay: float = 1.0) -> Callable[[F], F]:
    """Return a decorator that restarts ``func`` on exception.

    Parameters
    ----------
    max_restarts : int
        Maximum number of times to retry calling ``func`` before giving up.
    delay : float
        Seconds to wait before each retry.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:  # pragma: no cover - log then retry
                    attempts += 1
                    log_error(
                        f"[Watchdog] {func.__name__} crashed: {exc}",
                        context=traceback.format_exc(),
                    )
                    if attempts > max_restarts:
                        raise
                    time.sleep(delay)
        return wrapper  # type: ignore[return-value]

    return decorator


def get_description() -> str:
    """Return a short summary of this module."""
    return "Decorator that restarts a function if it raises an exception."
