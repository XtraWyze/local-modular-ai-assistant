"""Codex integration utilities."""

import os
import time
import importlib

from error_logger import log_error
from module_manager import ModuleRegistry
from modules.api_keys import get_api_key

MODULE_NAME = "codex_integration"

__all__ = ["CodexClient", "learn_new_automation", "get_info", "get_description"]


class CodexClient:
    """Simple wrapper for various code-generation APIs."""

    def __init__(self, engine: str = "code-davinci-002", provider: str = "openai"):
        self.engine = engine
        self.provider = provider.lower()
        self.api_key = get_api_key(self.provider)
        if not self.api_key:
            raise EnvironmentError(f"{self.provider} API key not set")
        if self.provider == "anthropic":
            self.url = "https://api.anthropic.com/v1/complete"
        elif self.provider == "google":
            self.url = (
                "https://generativelanguage.googleapis.com/v1beta2/models/"
                "text-bison-001:generateText"
            )
        else:
            self.url = "https://api.openai.com/v1/completions"

    def generate_code(self, prompt: str) -> str:
        """Return generated code for ``prompt`` or empty string on failure."""
        if self.provider == "anthropic":
            payload = {
                "model": self.engine,
                "prompt": prompt,
                "max_tokens_to_sample": 300,
            }
            headers = {
                "x-api-key": self.api_key,
                "content-type": "application/json",
            }
        elif self.provider == "google":
            payload = {
                "prompt": {"text": prompt},
                "temperature": 0.2,
            }
            headers = {"content-type": "application/json"}
            self.url += f"?key={self.api_key}"
        else:
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
            requests = importlib.import_module("requests")
            resp = requests.post(self.url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            if self.provider == "anthropic":
                return data.get("completion", "")
            if self.provider == "google":
                return data.get("candidates", [{}])[0].get("output", "")
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

