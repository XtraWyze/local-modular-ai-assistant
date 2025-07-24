"""System load monitoring utilities using psutil."""

from __future__ import annotations

import time
from typing import Any

from error_logger import log_error

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - psutil optional
    psutil = None

MODULE_NAME = "system_load"

__all__ = ["is_overloaded", "wait_for_load", "get_info", "get_description"]


def _get_cpu_mem() -> tuple[float, float]:
    """Return current CPU percent and memory percent usage."""
    if psutil is None:
        return 0.0, 0.0
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        return float(cpu), float(mem)
    except Exception as exc:  # pragma: no cover - runtime
        log_error(f"[{MODULE_NAME}] load query failed: {exc}")
        return 0.0, 0.0


def is_overloaded(cpu_thresh: float = 90.0, mem_thresh: float = 90.0) -> bool:
    """Return ``True`` if CPU or memory usage exceeds thresholds."""
    cpu, mem = _get_cpu_mem()
    return cpu >= cpu_thresh or mem >= mem_thresh


def wait_for_load(
    cpu_target: float = 80.0,
    mem_target: float = 85.0,
    check_interval: float = 1.0,
    timeout: float = 30.0,
) -> bool:
    """Wait until system load drops below targets or timeout expires."""
    if psutil is None:
        return True
    end = time.time() + timeout
    while time.time() < end:
        if not is_overloaded(cpu_target, mem_target):
            return True
        time.sleep(check_interval)
    return False


def get_info() -> dict[str, Any]:
    """Return module metadata."""
    return {
        "name": MODULE_NAME,
        "description": "Monitor CPU and memory usage to avoid overload.",
        "functions": ["is_overloaded", "wait_for_load"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Provides system load checks and waiting utilities using psutil."
