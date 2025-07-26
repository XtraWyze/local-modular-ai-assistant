import os
import types
import importlib

import pytest

from module_manager import ModuleRegistry


def mock_post(url, json=None, headers=None, timeout=60):
    class Dummy:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"text": "def demo():\n    return True"}]}

    return Dummy()


@pytest.fixture(autouse=True)
def _patch_requests(monkeypatch):
    mod = types.ModuleType("requests")
    mod.post = mock_post
    monkeypatch.setitem(importlib.sys.modules, "requests", mod)
    yield


def test_generate_code(monkeypatch):
    os.environ["OPENAI_API_KEY"] = "test"
    ci = importlib.import_module("modules.codex_integration")
    client = ci.CodexClient(engine="test")
    code = client.generate_code("print('hi')")
    assert "def demo" in code


def test_learn_new_automation(monkeypatch, tmp_path):
    os.environ["OPENAI_API_KEY"] = "test"
    ci = importlib.import_module("modules.codex_integration")
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    import sys
    if "modules" in sys.modules:
        monkeypatch.delitem(sys.modules, "modules")
    path = ci.learn_new_automation("does something")
    assert path.endswith(".py")
    assert os.path.exists(path)
    # ensure registry loads without error
    reg = ModuleRegistry().auto_discover("modules")
    assert reg.get_module(f"modules.{os.path.basename(path)[:-3]}")

