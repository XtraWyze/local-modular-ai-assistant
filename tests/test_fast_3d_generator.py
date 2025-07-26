from pathlib import Path
import importlib
import types
import os


def dummy_pipeline_return(prompt: str):
    class FakeModel:
        def save(self, path):
            Path(path).write_text("fake 3d")

    return types.SimpleNamespace(model=FakeModel())


class DummyPipeline:
    @classmethod
    def from_pretrained(cls, path):
        DummyPipeline.path = path
        return cls()

    def to(self, device):
        return self

    def __call__(self, prompt):
        DummyPipeline.prompt = prompt
        return dummy_pipeline_return(prompt)


def test_generate_model(monkeypatch, tmp_path):
    diffusers_mod = types.ModuleType("diffusers")
    diffusers_mod.StableFast3DPipeline = DummyPipeline
    monkeypatch.setitem(importlib.sys.modules, "diffusers", diffusers_mod)

    torch_mod = types.ModuleType("torch")

    class DummyAutocast:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    torch_mod.autocast = lambda *_a, **_k: DummyAutocast()
    torch_mod.float16 = None
    monkeypatch.setitem(importlib.sys.modules, "torch", torch_mod)

    mod = importlib.import_module("modules.stable_fast_3d")
    importlib.reload(mod)

    outdir = tmp_path / "models"
    result = mod.generate_model(
        "a cube",
        "path/to/model",
        device="cpu",
        save_dir=str(outdir),
        name="cube",
    )
    assert result.endswith(".obj")
    assert Path(result).exists()
    assert DummyPipeline.path == "path/to/model"
    assert DummyPipeline.prompt == "a cube"
