import importlib
import sys

import pytest

MODULE_PATH = "examples.openai_chat_example"


def reload_module():
    """Reload the example module to apply environment changes."""
    if MODULE_PATH in sys.modules:
        del sys.modules[MODULE_PATH]
    return importlib.import_module(MODULE_PATH)


def test_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    mod = reload_module()
    result = mod.send_test_message("Hi")
    assert "missing" in result.lower()


def test_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    # Patch the OpenAI client to avoid network access
    mod = reload_module()

    class DummyResp:
        class Choice:
            def __init__(self):
                self.message = type("msg", (), {"content": "pong"})

        def __init__(self):
            self.choices = [self.Choice()]

    if hasattr(mod.openai, "OpenAI"):
        class DummyClient:
            def __init__(self, *a, **kw):
                pass

            class chat:
                class completions:
                    @staticmethod
                    def create(**_k):
                        return DummyResp()
        monkeypatch.setattr(mod.openai, "OpenAI", DummyClient)
    else:
        monkeypatch.setattr(mod.openai.ChatCompletion, "create", lambda **_k: DummyResp())

    result = mod.send_test_message("Ping")
    assert result == "pong"
