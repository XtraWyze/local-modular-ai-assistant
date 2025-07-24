import os
import importlib
import types

import pytest

from module_manager import ModuleRegistry


def fake_post(url, json=None, headers=None, timeout=60):
    class Dummy:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"text": "def demo():\n    return True"}]}

    return Dummy()


@pytest.fixture(autouse=True)
def _patch_requests(monkeypatch):
    mod = types.ModuleType("requests")
    mod.post = fake_post
    monkeypatch.setitem(importlib.sys.modules, "requests", mod)
    yield


class DummyClient:
    def __init__(self, engine: str = "test") -> None:
        pass

    def generate_code(self, prompt: str) -> str:
        return "def demo():\n    return True"


@pytest.fixture(autouse=True)
def _patch_codex_client(monkeypatch):
    mg = importlib.import_module("modules.module_generator")
    monkeypatch.setattr(mg, "CodexClient", lambda: DummyClient())
    yield


def test_generate_module(monkeypatch, tmp_path):
    os.environ["OPENAI_API_KEY"] = "test"
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    import sys
    if "modules" in sys.modules:
        monkeypatch.delitem(sys.modules, "modules")

    mg = importlib.import_module("modules.module_generator")
    path = mg.generate_module("prints hello", name="demo_mod")
    assert path.endswith("demo_mod.py")
    assert os.path.exists(path)

    reg = ModuleRegistry().auto_discover("modules")
    assert reg.get_module("modules.demo_mod")
