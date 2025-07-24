"""Home Assistant REST API integration (disabled by default)."""

from __future__ import annotations

try:
    import requests
except Exception as e:  # pragma: no cover - optional dependency
    requests = None  # type: ignore
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

BASE_URL = ""
TOKEN = ""
ENABLED = False

__all__ = ["initialize", "call_service", "get_state", "get_description", "get_info"]


def initialize(config: dict | None = None) -> None:
    """Initialize connection settings from ``config``."""
    global BASE_URL, TOKEN, ENABLED
    config = config or {}
    BASE_URL = config.get("home_assistant_url", "").rstrip("/")
    TOKEN = config.get("home_assistant_token", "")
    ENABLED = bool(config.get("enable_home_assistant", False))


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def call_service(domain: str, service: str, data: dict | None = None) -> str:
    """Invoke ``service`` under ``domain`` with optional ``data``."""
    if not ENABLED:
        return "Home Assistant integration disabled"
    if requests is None:
        return f"requests not available: {_IMPORT_ERROR}"
    url = f"{BASE_URL}/api/services/{domain}/{service}"
    try:
        resp = requests.post(url, json=data or {}, headers=_headers(), timeout=5)
        resp.raise_for_status()
        return f"called {domain}.{service}"
    except Exception as exc:  # pragma: no cover - network failure
        return f"error calling service: {exc}"


def get_state(entity_id: str):
    """Return the state for ``entity_id`` or an error message."""
    if not ENABLED:
        return "Home Assistant integration disabled"
    if requests is None:
        return f"requests not available: {_IMPORT_ERROR}"
    url = f"{BASE_URL}/api/states/{entity_id}"
    try:
        resp = requests.get(url, headers=_headers(), timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # pragma: no cover - network failure
        return f"error getting state: {exc}"


def get_info() -> dict:
    return {
        "name": "home_assistant_integration",
        "description": "Minimal Home Assistant REST API client.",
        "functions": ["initialize", "call_service", "get_state"],
    }


def get_description() -> str:
    return "Optional Home Assistant integration for controlling smart devices."
