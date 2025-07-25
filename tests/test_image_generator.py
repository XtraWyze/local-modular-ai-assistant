import base64
import importlib
import os
import types
from pathlib import Path

import pytest


def mock_post(url, json=None, headers=None, timeout=60):
    """Return a dummy response object and capture the payload."""
    mock_post.last_payload = json

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
    mod.post = mock_post
    monkeypatch.setitem(importlib.sys.modules, "requests", mod)
    yield


def test_generate_image(monkeypatch, tmp_path):
    os.environ["OPENAI_API_KEY"] = "test"
    ig = importlib.import_module("modules.image_generator")
    monkeypatch.chdir(tmp_path)
    result = ig.generate_image("a cat")
    assert result.endswith(".png")
    assert os.path.exists(result)
    assert mock_post.last_payload["model"] == "dall-e-3"


def test_default_save_dir(monkeypatch):
    os.environ["OPENAI_API_KEY"] = "test"
    ig = importlib.import_module("modules.image_generator")
    project_root = Path(__file__).resolve().parents[1]

    monkeypatch.chdir(project_root / "examples")
    result = ig.generate_image("a tree")
    path = Path(result)
    assert path.parent == project_root / "generated_images"
    assert path.exists()
    path.unlink()

