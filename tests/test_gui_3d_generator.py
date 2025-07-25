import modules.stable_fast_3d as fast3d
import os
import shutil


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


def run_generate_3d(prompt_widget, status_widget, model_var, device_var, dir_var, name_var):
    prompt = prompt_widget.get("1.0", None).strip()
    if not prompt:
        status_widget.config(text="Enter a prompt first.")
        return
    return fast3d.generate_model(
        prompt,
        model_var.get(),
        device=device_var.get(),
        save_dir=dir_var.get(),
        name=name_var.get() or None,
    )


def test_generate_model(monkeypatch):
    calls = {}
    monkeypatch.setattr(
        fast3d,
        "generate_model",
        lambda *a, **k: calls.setdefault("gen", []).append((a, k)) or "cube.obj",
    )

    vars = dict(
        prompt_widget=DummyText("cube"),
        status_widget=DummyStatus(),
        model_var=DummyVar("model"),
        device_var=DummyVar("cpu"),
        dir_var=DummyVar("models"),
        name_var=DummyVar("cube"),
    )

    run_generate_3d(**vars)

    assert calls["gen"] == [(
        ("cube", "model"),
        {"device": "cpu", "save_dir": "models", "name": "cube"},
    )]


def run_save_model(current_path, status_widget, dest):
    if not current_path or not os.path.exists(current_path):
        status_widget.config(text="No model to save.")
        return None
    shutil.copy(current_path, dest)
    status_widget.config(text=f"Saved to {dest}")
    return dest


def test_save_model_no_file(tmp_path):
    status = DummyStatus()
    result = run_save_model("", status, tmp_path / "x.obj")
    assert result is None
    assert status.text == "No model to save."

