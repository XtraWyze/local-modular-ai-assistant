import importlib

import modules.imagine_generator as im_gen


def test_imagine_local(monkeypatch):
    calls = {}

    def mock_sd(prompt, path, *, device=None, save_dir="generated_images"):
        calls["sd"] = (prompt, path, device, save_dir)
        return "sd.png"

    monkeypatch.setattr(im_gen.sd, "generate_image", mock_sd)
    out = im_gen.imagine("cat", source="local", sd_model_path="model", device="cpu")
    assert out == "sd.png"
    assert calls["sd"] == ("cat", "model", "cpu", "generated_images")


def test_imagine_cloud(monkeypatch):
    calls = {}

    def mock_cloud(prompt, *, model="dall-e-3", size="512x512", save_dir="generated_images"):
        calls["cloud"] = (prompt, model, size, save_dir)
        return "cloud.png"

    monkeypatch.setattr(im_gen.ig, "generate_image", mock_cloud)
    out = im_gen.imagine(
        "dog",
        source="cloud",
        model="dall-e-2",
        size="256x256",
        save_dir="imgs",
    )
    assert out == "cloud.png"
    assert calls["cloud"] == ("dog", "dall-e-2", "256x256", "imgs")
