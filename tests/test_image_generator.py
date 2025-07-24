import base64
import importlib
import os
import types

import pytest


def fake_post(url, json=None, headers=None, timeout=60):
    class Dummy:
        def raise_for_status(self):
            pass

        def json(self):
            data = base64.b64encode(b"img").decode()
            return {"data": [{"b64_json": data}]}

    return Dummy()


@pytest.fixture(autouse=True)
def _patch_requests(monkeypatch):
    mod = types.ModuleType("requests")
    mod.post = fake_post
    monkeypatch.setitem(importlib.sys.modules, "requests", mod)
    yield


def test_generate_image(monkeypatch, tmp_path):
    os.environ["OPENAI_API_KEY"] = "test"
    ig = importlib.import_module("modules.image_generator")
    monkeypatch.chdir(tmp_path)
    result = ig.generate_image("a cat")
    assert result.endswith(".png")
    assert os.path.exists(result)

