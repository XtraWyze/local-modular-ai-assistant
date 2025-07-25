import importlib

import modules.imagine_generator as im_gen


def test_imagine_local(monkeypatch):
    calls = {}

    def mock_sd(prompt, path, *, device=None, save_dir="generated_images", name=None):
        calls["sd"] = (prompt, path, device, save_dir, name)
        return "sd.png"

    monkeypatch.setattr(im_gen.sd, "generate_image", mock_sd)
    out = im_gen.imagine("cat", source="local", sd_model_path="model", device="cpu")
    assert out == "sd.png"
    assert calls["sd"] == ("cat", "model", "cpu", "generated_images", None)


def test_imagine_cloud(monkeypatch):
    calls = {}

    def mock_cloud(prompt, *, model="dall-e-3", size="512x512", save_dir="generated_images", name=None):
        calls["cloud"] = (prompt, model, size, save_dir, name)
        return "cloud.png"

    monkeypatch.setattr(im_gen.ig, "generate_image", mock_cloud)
    out = im_gen.imagine(
        "dog",
        source="cloud",
        model="dall-e-2",
        size="256x256",
        save_dir="imgs",
        name="foo",
    )
    assert out == "cloud.png"
    assert calls["cloud"] == ("dog", "dall-e-2", "256x256", "imgs", "foo")


def test_imagine_gui_callback(monkeypatch):
    calls = {}

    def gui_cb(prompt, **kwargs):
        calls["prompt"] = prompt
        calls.update(kwargs)
        return "gui.png"

    im_gen.set_gui_callback(gui_cb)
    monkeypatch.setattr(im_gen, "ig", importlib.import_module("modules.image_generator"))
    out = im_gen.imagine("frog")
    im_gen.set_gui_callback(None)
    assert out == "gui.png"
    assert calls["prompt"] == "frog"
