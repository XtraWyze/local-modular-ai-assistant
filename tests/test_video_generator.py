import base64
import importlib
import os
import types
from pathlib import Path

import pytest


def mock_post(url, json=None, headers=None, timeout=120):
    mock_post.last_payload = json

    class Dummy:
        def raise_for_status(self):
            pass

        def json(self):
            data = base64.b64encode(b"video").decode()
            return {"video": data}

    return Dummy()


@pytest.fixture(autouse=True)
def _patch_requests(monkeypatch):
    mod = types.ModuleType("requests")
    mod.post = mock_post
    monkeypatch.setitem(importlib.sys.modules, "requests", mod)
    yield


def test_generate_cloud_video(monkeypatch, tmp_path):
    os.environ["VEO3_API_KEY"] = "test"
    vg = importlib.import_module("modules.video_generator")
    monkeypatch.chdir(tmp_path)
    result = vg.generate_video("a cat")
    assert result.endswith(".mp4")
    assert os.path.exists(result)
    assert mock_post.last_payload["model"] == "veo-3"


class DummyPipeline:
    @classmethod
    def from_pretrained(cls, path):
        DummyPipeline.path = path
        return cls()

    def to(self, device):
        return self

    def __call__(self, prompt, num_frames=16):
        from PIL import Image

        DummyPipeline.prompt = prompt
        frame = Image.new("RGB", (8, 8), "red")
        return types.SimpleNamespace(frames=[frame] * num_frames)


class DummyAutocast:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


def test_generate_local_video(monkeypatch, tmp_path):
    diffusers_mod = types.ModuleType("diffusers")
    diffusers_mod.StableVideoDiffusionPipeline = DummyPipeline
    monkeypatch.setitem(importlib.sys.modules, "diffusers", diffusers_mod)

    torch_mod = types.ModuleType("torch")
    torch_mod.autocast = lambda *_a, **_k: DummyAutocast()
    torch_mod.float16 = None
    monkeypatch.setitem(importlib.sys.modules, "torch", torch_mod)

    vg = importlib.import_module("modules.video_generator")
    importlib.reload(vg)

    monkeypatch.setattr(vg.gpu, "get_device", lambda: "cpu")
    monkeypatch.setattr(vg.gpu, "autocast", lambda *_a, **_k: DummyAutocast())

    result = vg.generate_video(
        "dog",
        source="local",
        local_model_path="path/to/model",
        device="cpu",
        save_dir=str(tmp_path),
    )
    assert result.endswith(".gif")
    assert Path(result).exists()
    assert DummyPipeline.path == "path/to/model"
    assert DummyPipeline.prompt == "dog"

