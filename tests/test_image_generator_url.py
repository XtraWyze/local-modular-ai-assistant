import importlib
import sys
import types

MODULE_PATH = "modules.image_generator"


def reload_mod():
    if MODULE_PATH in sys.modules:
        del sys.modules[MODULE_PATH]
    return importlib.import_module(MODULE_PATH)


def test_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    mod = reload_mod()
    result = mod.generate_image_url("cat")
    assert "missing" in result.lower()


def test_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    mod = reload_mod()
    dummy_url = "http://example.com/img.png"

    if hasattr(mod.openai, "OpenAI"):
        class DummyClient:
            def __init__(self, *a, **kw):
                pass
            class images:
                @staticmethod
                def generate(*_a, **_kw):
                    return types.SimpleNamespace(data=[types.SimpleNamespace(url=dummy_url)])
        monkeypatch.setattr(mod.openai, "OpenAI", DummyClient)
    else:
        monkeypatch.setattr(
            mod.openai.Image,
            "create",
            lambda **_k: {"data": [{"url": dummy_url}]},
        )

    url = mod.generate_image_url("A cat")
    assert url == dummy_url

