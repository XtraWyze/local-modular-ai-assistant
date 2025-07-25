import os
import importlib
import types

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


class DummyClient:
    def __init__(self, engine: str = "test") -> None:
        pass

    def generate_code(self, prompt: str) -> str:
        return "def demo():\n    return True"


@pytest.fixture(autouse=True)
def _patch_codex_client(monkeypatch):
    mg = importlib.import_module("modules.module_generator")
    monkeypatch.setattr(mg, "CodexClient", lambda *a, **k: DummyClient())
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


def test_generate_module_interactive_yes(monkeypatch, tmp_path):
    os.environ["OPENAI_API_KEY"] = "test"
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    import sys
    if "modules" in sys.modules:
        monkeypatch.delitem(sys.modules, "modules")

    mg = importlib.import_module("modules.module_generator")
    monkeypatch.setattr("builtins.input", lambda _: "y")
    path = mg.generate_module_interactive("prints hello", name="demo_mod2")
    assert path.endswith("demo_mod2.py")
    assert os.path.exists(path)

    reg = ModuleRegistry().auto_discover("modules")
    assert reg.get_module("modules.demo_mod2")


def test_generate_module_interactive_cancel(monkeypatch, tmp_path):
    os.environ["OPENAI_API_KEY"] = "test"
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    import sys
    if "modules" in sys.modules:
        monkeypatch.delitem(sys.modules, "modules")

    mg = importlib.import_module("modules.module_generator")
    monkeypatch.setattr("builtins.input", lambda _: "n")
    result = mg.generate_module_interactive("prints hello", name="demo_mod3")
    assert result == "Generation cancelled."
    assert not os.path.exists(os.path.join("modules", "demo_mod3.py"))


def test_save_module_code(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    import sys
    if "modules" in sys.modules:
        monkeypatch.delitem(sys.modules, "modules")

    mg = importlib.import_module("modules.module_generator")
    path = mg.save_module_code("def demo():\n    return True", name="demo_mod4")
    assert path.endswith("demo_mod4.py")
    assert os.path.exists(path)

    reg = ModuleRegistry().auto_discover("modules")
    assert reg.get_module("modules.demo_mod4")
