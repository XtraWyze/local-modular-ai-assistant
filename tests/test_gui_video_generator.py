import modules.video_generator as video_gen

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


def run_generate_video(video_prompt, video_status, source_var, model_var, device_var, fps_var):
    prompt = video_prompt.get("1.0", None).strip()
    if not prompt:
        video_status.config(text="Enter a prompt first.")
        return
    if source_var.get() == "local":
        return video_gen.generate_video(
            prompt,
            source="local",
            local_model_path=model_var.get(),
            device=device_var.get(),
            fps=int(fps_var.get()),
        )
    return video_gen.generate_video(prompt, fps=int(fps_var.get()))


def test_generate_video_local(monkeypatch):
    calls = {}
    def _gen(*a, **k):
        calls.setdefault("vid", []).append((a, k))
        return "v.mp4"
    monkeypatch.setattr(video_gen, "generate_video", _gen)

    vars = dict(
        video_prompt=DummyText("cat"),
        video_status=DummyStatus(),
        source_var=DummyVar("local"),
        model_var=DummyVar("model"),
        device_var=DummyVar("cpu"),
        fps_var=DummyVar("8"),
    )

    run_generate_video(**vars)

    assert calls["vid"][0][0][0] == "cat"
    assert calls["vid"][0][1]["source"] == "local"


def test_generate_video_cloud(monkeypatch):
    calls = {}
    def _gen(*a, **k):
        calls.setdefault("vid", []).append((a, k))
        return "v.mp4"
    monkeypatch.setattr(video_gen, "generate_video", _gen)

    vars = dict(
        video_prompt=DummyText("dog"),
        video_status=DummyStatus(),
        source_var=DummyVar("cloud"),
        model_var=DummyVar("model"),
        device_var=DummyVar("cuda"),
        fps_var=DummyVar("12"),
    )

    run_generate_video(**vars)

    assert calls["vid"][0][0][0] == "dog"
    assert calls["vid"][0][1].get("source") != "local"

