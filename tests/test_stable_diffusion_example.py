import importlib
import sys
import types
from pathlib import Path

MODULE_PATH = "examples.stable_diffusion_example"


def reload_module(monkeypatch):
    if MODULE_PATH in sys.modules:
        del sys.modules[MODULE_PATH]
    return importlib.import_module(MODULE_PATH)


def test_preview_image_with_pillow(monkeypatch, tmp_path):
    mod = reload_module(monkeypatch)
    path = tmp_path / "img.png"
    path.write_text("img")

    class DummyImg:
        def show(self):
            DummyImg.shown = True

    class DummyPIL:
        @staticmethod
        def open(p):
            assert p == str(path)
            return DummyImg()

    monkeypatch.setattr(mod, "Image", DummyPIL)
    web_calls = []
    monkeypatch.setattr(mod.webbrowser, "open", lambda u: web_calls.append(u))

    mod.preview_image(str(path))
    assert getattr(DummyImg, "shown", False)
    assert not web_calls


def test_preview_image_fallback(monkeypatch, tmp_path):
    mod = reload_module(monkeypatch)
    path = tmp_path / "img.png"
    path.write_text("img")

    monkeypatch.setattr(mod, "Image", None)
    urls = []
    monkeypatch.setattr(mod.webbrowser, "open", lambda u: urls.append(u))

    mod.preview_image(str(path))
    assert urls and urls[0].startswith("file://")


def test_main(monkeypatch, tmp_path, capsys):
    def mock_generate_image(prompt, model, device=None):
        file_path = tmp_path / "out.png"
        file_path.write_text("fake")
        return str(file_path)

    sd_mod = types.SimpleNamespace(generate_image=mock_generate_image)
    monkeypatch.setitem(sys.modules, "modules.stable_diffusion_generator", sd_mod)
    mod = reload_module(monkeypatch)

    monkeypatch.setattr(mod, "preview_image", lambda p: None)

    mod.main([
        "--prompt",
        "hello",
        "--model",
        "path",
        "--device",
        "cpu",
    ])
    out = capsys.readouterr().out
    assert "Image saved to" in out
