from __future__ import annotations

"""Utility functions for managing API keys for external providers."""

import json
import os
from typing import Dict

from config_loader import ConfigLoader

# Supported provider identifiers
PROVIDERS = ["openai", "anthropic", "google"]

MODULE_NAME = "api_keys"

__all__ = [
    "apply_keys_from_config",
    "save_api_keys",
    "get_api_key",
    "get_info",
    "get_description",
]

# Initialize configuration loader
_config_loader = ConfigLoader()
_config = _config_loader.config


def apply_keys_from_config() -> None:
    """Set environment variables from the API keys stored in config."""
    api_cfg = _config.get("api_keys", {})
    for prov in PROVIDERS:
        key = api_cfg.get(prov)
        if key:
            os.environ[f"{prov.upper()}_API_KEY"] = key


def save_api_keys(keys: Dict[str, str]) -> None:
    """Persist ``keys`` into ``config.json`` and update the environment."""
    api_cfg = _config.setdefault("api_keys", {})
    for prov in PROVIDERS:
        if prov in keys:
            api_cfg[prov] = keys[prov]
    with open(_config_loader.path, "w", encoding="utf-8") as f:
        json.dump(_config, f, indent=2)
    apply_keys_from_config()


def get_api_key(provider: str) -> str:
    """Return API key for ``provider`` from environment or config."""
    env_name = f"{provider.upper()}_API_KEY"
    return os.getenv(env_name) or _config.get("api_keys", {}).get(provider, "")


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": "Manage API keys for external services.",
        "functions": ["apply_keys_from_config", "save_api_keys", "get_api_key"],
    }


def get_description() -> str:
    """Return a short summary of this module."""
    return "Utilities for storing API keys and applying them to the environment."


# Apply keys at import so other modules can rely on environment variables
apply_keys_from_config()
