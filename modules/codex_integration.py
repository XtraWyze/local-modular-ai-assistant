"""Codex integration utilities."""

import os
import time
import requests

from error_logger import log_error
from module_manager import ModuleRegistry

MODULE_NAME = "codex_integration"

__all__ = ["CodexClient", "learn_new_automation", "get_info", "get_description"]


class CodexClient:
    """Simple wrapper for the OpenAI Codex API."""

    def __init__(self, engine: str = "code-davinci-002"):
        self.engine = engine
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("OPENAI_API_KEY not set")
        self.url = "https://api.openai.com/v1/completions"

    def generate_code(self, prompt: str) -> str:
        """Return generated code for ``prompt`` or empty string on failure."""
        payload = {
            "model": self.engine,
            "prompt": prompt,
            "max_tokens": 256,
            "temperature": 0,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(self.url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return data.get("choices", [{}])[0].get("text", "")
        except Exception as exc:  # pragma: no cover - network failure
            log_error(f"[Codex] API error: {exc}")
            return ""


def learn_new_automation(description: str) -> str:
    """Generate a new automation module via Codex and load it."""
    prompt = f"Write a new automation module for my local AI assistant that {description}."\
             " Provide only Python code."
    try:
        client = CodexClient()
        code = client.generate_code(prompt)
        if not code:
            return "No code returned"
        os.makedirs("modules", exist_ok=True)
        filename = f"automation_{int(time.time())}.py"
        path = os.path.join("modules", filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        import sys
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        ModuleRegistry().auto_discover("modules")
        return path
    except Exception as exc:  # pragma: no cover - catch-all
        log_error(f"[Codex] learn_new_automation failed: {exc}")
        return f"Error: {exc}"


def get_info():
    return {
        "name": MODULE_NAME,
        "description": "OpenAI Codex integration for generating new modules.",
        "functions": ["CodexClient", "learn_new_automation"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Utilities for querying OpenAI Codex to scaffold new modules."

