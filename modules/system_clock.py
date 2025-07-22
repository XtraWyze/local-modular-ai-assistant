"""System clock utilities."""

from datetime import datetime
import subprocess
import sys

__all__ = ["get_system_time", "set_system_time"]

def get_system_time(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Return the current system time formatted with ``fmt``."""
    return datetime.now().strftime(fmt)

def set_system_time(dt_string: str) -> str:
    """Set the system clock to ``dt_string`` (YYYY-MM-DD HH:MM:SS)."""
    dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
    if sys.platform.startswith("win"):
        date_str = dt.strftime("%m-%d-%Y")
        time_str = dt.strftime("%H:%M:%S")
        subprocess.run(["cmd", "/c", f"date {date_str}"], check=False)
        subprocess.run(["cmd", "/c", f"time {time_str}"], check=False)
    else:
        formatted = dt.strftime("%m%d%H%M%Y.%S")
        subprocess.run(["date", formatted], check=False)
    return f"System time set to {dt_string}"

def get_info():
    return {
        "name": "system_clock",
        "description": "Helper functions for reading or setting the system clock.",
        "functions": ["get_system_time", "set_system_time"],
    }

def get_description() -> str:
    """Return a short description of this module."""
    return "Utilities for reading or setting the system clock."
