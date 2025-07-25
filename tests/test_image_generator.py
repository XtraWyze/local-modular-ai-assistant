import base64
import importlib
import os
import types

try:
    from PIL import Image
except Exception:
    Image = None
import pytest

pytestmark = pytest.mark.skipif(Image is None, reason="Pillow not available")


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


def fake_pipeline_from_pretrained(model_id):
    class DummyPipe:
        def to(self, device):
            return self

        def __call__(self, prompt, height=None, width=None):
            from PIL import Image
            return types.SimpleNamespace(images=[Image.new("RGB", (width or 64, height or 64))])

    return DummyPipe()


@pytest.fixture(autouse=True)
def _patch_diffusers(monkeypatch):
    mod = types.ModuleType("diffusers")
    mod.StableDiffusionPipeline = types.SimpleNamespace(from_pretrained=fake_pipeline_from_pretrained)
    monkeypatch.setitem(importlib.sys.modules, "diffusers", mod)
    yield


def test_generate_image(monkeypatch, tmp_path):
    os.environ["OPENAI_API_KEY"] = "test"
    ig = importlib.import_module("modules.image_generator")
    monkeypatch.chdir(tmp_path)
    result = ig.generate_image("a cat")
    assert result.endswith(".png")
    assert os.path.exists(result)


def test_generate_image_local(monkeypatch, tmp_path):
    ig = importlib.import_module("modules.image_generator")
    monkeypatch.chdir(tmp_path)
    result = ig.generate_image("a cat", provider="diffusers", size="64x64")
    assert result.endswith(".png")
    assert os.path.exists(result)

