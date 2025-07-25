from __future__ import annotations

"""Utilities for the GUI Web Activity tab."""

import webbrowser
from typing import List, Optional

try:
    from tkinterweb import HtmlFrame  # type: ignore
except Exception as e:  # pragma: no cover - optional dependency
    HtmlFrame = None  # type: ignore
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

from urllib.parse import quote_plus

from error_logger import log_error

MODULE_NAME = "web_activity"

__all__ = ["load_url", "get_history", "create_search_url", "get_info", "get_description"]

_HISTORY: List[str] = []


def create_search_url(query: str) -> str:
    """Return a search engine URL if ``query`` is not already a URL."""
    if query.startswith("http"):
        return query
    return f"https://www.google.com/search?q={quote_plus(query)}"


def load_url(url: str, html_view: Optional[object] = None) -> None:
    """Load ``url`` into ``html_view`` if possible, else open in browser.

    Parameters
    ----------
    url:
        The URL to open.
    html_view:
        Optional :class:`tkinterweb.HtmlFrame` instance. If ``None`` or loading
        fails, the URL is opened in the user's default browser.
    """
    if html_view and hasattr(html_view, "load_website"):
        try:
            html_view.load_website(url)
        except Exception as exc:  # pragma: no cover - loading may fail
            log_error(f"[{MODULE_NAME}] failed to load {url}: {exc}")
            webbrowser.open(url)
    else:
        webbrowser.open(url)
    _HISTORY.append(url)


def get_history() -> List[str]:
    """Return the list of previously loaded URLs."""
    return list(_HISTORY)


def get_info() -> dict:
    """Return module metadata."""
    return {
        "name": MODULE_NAME,
        "functions": ["load_url", "get_history", "create_search_url"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Utility helpers for the GUI web activity tab."
