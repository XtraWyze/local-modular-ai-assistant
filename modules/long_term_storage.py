"""long_term_storage.py
SQLite-based long-term storage for text entries.
"""

import sqlite3
from datetime import datetime
from error_logger import log_error

DB_FILE = "assistant_memory.db"
TABLE = "memory"

__all__ = ["initialize", "save_entry", "fetch_recent"]


def initialize(config=None):
    """Create the database table if it doesn't exist."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {TABLE} (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, timestamp TEXT)"
            )
    except Exception as e:  # pragma: no cover - simple logging
        log_error(f"[long_term_storage] init error: {e}")


def save_entry(text: str) -> bool:
    """Persist a text entry with timestamp."""
    try:
        ts = datetime.utcnow().isoformat()
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                f"INSERT INTO {TABLE} (text, timestamp) VALUES (?, ?)",
                (text, ts),
            )
        return True
    except Exception as e:  # pragma: no cover - simple logging
        log_error(f"[long_term_storage] save_entry error: {e}")
        return False


def fetch_recent(limit: int = 10):
    """Return the most recent text entries."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            rows = conn.execute(
                f"SELECT text, timestamp FROM {TABLE} ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return rows
    except Exception as e:  # pragma: no cover - simple logging
        log_error(f"[long_term_storage] fetch_recent error: {e}")
        return []


def get_info():
    return {
        "name": "long_term_storage",
        "description": "SQLite-based persistent storage for text entries.",
        "functions": ["initialize", "save_entry", "fetch_recent"],
    }


def get_description() -> str:
    """Return a short summary of this module."""
    return "Stores and retrieves conversation history in a local SQLite database."


def register(registry=None):
    """Register this module with ``ModuleRegistry``."""
    from module_manager import ModuleRegistry

    registry = registry or ModuleRegistry()
    registry.register(
        "long_term_storage",
        {
            "initialize": initialize,
            "save_entry": save_entry,
            "fetch_recent": fetch_recent,
            "get_info": get_info,
        },
    )
