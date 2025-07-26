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


def run_generate_image(img_prompt, img_status, source_var, sd_model_var, sd_device_var, size_var, dir_var, name_var):
    prompt = img_prompt.get("1.0", None).strip()
    if not prompt:
        img_status.config(text="Enter a prompt first.")
        return
    if source_var.get() == "local":
        return sd_gen.generate_image(
            prompt,
            sd_model_var.get(),
            device=sd_device_var.get(),
            save_dir=dir_var.get(),
            name=name_var.get() or None,
        )
    return image_gen.generate_image(
        prompt,
        size=size_var.get(),
        save_dir=dir_var.get(),
        name=name_var.get() or None,
    )


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
        dir_var=DummyVar("imgs"),
        name_var=DummyVar("test"),
    )

    run_generate_image(**vars)

    assert calls.get("sd") == [(
        ('cat', 'model'),
        {'device': 'cpu', 'save_dir': 'imgs', 'name': 'test'},
    )]
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
        dir_var=DummyVar("imgs"),
        name_var=DummyVar("foo"),
    )

    run_generate_image(**vars)

    assert calls.get("ig") == [(
        ('dog',),
        {'size': '256x256', 'save_dir': 'imgs', 'name': 'foo'},
    )]
    assert calls.get("sd") is None
