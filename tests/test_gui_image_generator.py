import modules.image_generator as image_gen
import modules.stable_diffusion_generator as sd_gen

class DummyVar:
    def __init__(self, value=""):
        self.value = value
    def get(self):
        return self.value
    def set(self, val):
        self.value = val

class DummyText:
    def __init__(self, text=""):
        self.text = text
    def get(self, *_args, **_kwargs):
        return self.text

class DummyStatus:
    def __init__(self):
        self.text = ""
    def config(self, *, text: str):
        self.text = text


class DummyPreview:
    def __init__(self):
        self.path = ""

    def configure(self, **_kwargs):
        pass


def run_generate_image(img_prompt, img_status, source_var, sd_model_var, sd_device_var, size_var):
    prompt = img_prompt.get("1.0", None).strip()
    if not prompt:
        img_status.config(text="Enter a prompt first.")
        return
    if source_var.get() == "local":
        return sd_gen.generate_image(prompt, sd_model_var.get(), device=sd_device_var.get())
    return image_gen.generate_image(prompt, size=size_var.get())


def run_load_latest_image(img_preview, img_status, directory_var):
    path = image_gen.get_latest_image(directory_var.get())
    if not path:
        img_status.config(text="No images found")
        return None
    img_status.config(text=f"Loaded {path}")
    img_preview.path = path
    return path


def test_generate_image_local(monkeypatch):
    calls = {}
    monkeypatch.setattr(sd_gen, "generate_image", lambda *a, **k: calls.setdefault("sd", []).append((a, k)) or "sd.png")
    monkeypatch.setattr(image_gen, "generate_image", lambda *a, **k: calls.setdefault("ig", []).append((a, k)) or "ig.png")

    vars = dict(
        img_prompt=DummyText("cat"),
        img_status=DummyStatus(),
        source_var=DummyVar("local"),
        sd_model_var=DummyVar("model"),
        sd_device_var=DummyVar("cpu"),
        size_var=DummyVar("512x512"),
    )

    run_generate_image(**vars)

    assert calls.get("sd") == [(('cat', 'model'), {'device': 'cpu'})]
    assert calls.get("ig") is None


def test_generate_image_cloud(monkeypatch):
    calls = {}
    monkeypatch.setattr(sd_gen, "generate_image", lambda *a, **k: calls.setdefault("sd", []).append((a, k)) or "sd.png")
    monkeypatch.setattr(image_gen, "generate_image", lambda *a, **k: calls.setdefault("ig", []).append((a, k)) or "ig.png")

    vars = dict(
        img_prompt=DummyText("dog"),
        img_status=DummyStatus(),
        source_var=DummyVar("cloud"),
        sd_model_var=DummyVar("model"),
        sd_device_var=DummyVar("cuda"),
        size_var=DummyVar("256x256"),
    )

    run_generate_image(**vars)

    assert calls.get("ig") == [(('dog',), {'size': '256x256'})]
    assert calls.get("sd") is None


def test_load_latest_image(monkeypatch):
    monkeypatch.setattr(image_gen, "get_latest_image", lambda d: "foo.png")
    preview = DummyPreview()
    status = DummyStatus()
    result = run_load_latest_image(preview, status, DummyVar("dir"))
    assert result == "foo.png"
    assert status.text == "Loaded foo.png"
