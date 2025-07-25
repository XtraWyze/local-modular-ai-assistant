import importlib
import types
from pathlib import Path


def dummy_pipeline_return(prompt: str):
    class FakeImage:
        def save(self, path):
            Path(path).write_text("fake")

    return types.SimpleNamespace(images=[FakeImage()])


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


def test_generate_image(monkeypatch, tmp_path):
    diffusers_mod = types.ModuleType('diffusers')
    diffusers_mod.StableDiffusionPipeline = DummyPipeline
    monkeypatch.setitem(importlib.sys.modules, 'diffusers', diffusers_mod)

    torch_mod = types.ModuleType('torch')

    class DummyAutocast:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    torch_mod.autocast = lambda *_args, **_kwargs: DummyAutocast()
    torch_mod.float16 = None
    monkeypatch.setitem(importlib.sys.modules, 'torch', torch_mod)

    mod = importlib.import_module('modules.stable_diffusion_generator')
    importlib.reload(mod)

    outdir = tmp_path / 'imgs'
    result = mod.generate_image('a cat', 'path/to/model', device='cpu', save_dir=str(outdir))
    assert result.endswith('.png')
    assert Path(result).exists()
    assert DummyPipeline.path == 'path/to/model'
    assert DummyPipeline.prompt == 'a cat'

