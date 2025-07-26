import importlib
import types

import modules.stable_fast_3d as fast3d
import modules.shap_e_generator as shap_e
import modules.opendream_generator as opendream
import modules.stable_dreamfusion_generator as dreamfusion


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


def run_generate_model(prompt_widget, status_widget, tool_var, model_var, device_var, dir_var, name_var, quality_var):
    prompt = prompt_widget.get("1.0", None).strip()
    if not prompt:
        status_widget.config(text="Enter a prompt first.")
        return
    tool = tool_var.get()
    if tool == "Stable Fast 3D":
        return fast3d.generate_model(
            prompt,
            model_var.get(),
            device=device_var.get(),
            save_dir=dir_var.get(),
            name=name_var.get() or None,
        )
    if tool == "Shap-E":
        return shap_e.generate_model(
            prompt,
            device=device_var.get(),
            save_dir=dir_var.get(),
            name=name_var.get() or None,
        )
    if tool == "OpenDream":
        return opendream.generate_model(
            prompt,
            quality=quality_var.get(),
            save_dir=dir_var.get(),
            name=name_var.get() or None,
        )
    return dreamfusion.generate_model(
        prompt,
        model_var.get(),
        device=device_var.get(),
        save_dir=dir_var.get(),
        name=name_var.get() or None,
    )


def test_generate_model_routes(monkeypatch):
    calls = {}
    monkeypatch.setattr(
        fast3d,
        "generate_model",
        lambda *a, **k: calls.setdefault("fast", []).append((a, k)) or "a.obj",
    )
    monkeypatch.setattr(
        shap_e,
        "generate_model",
        lambda *a, **k: calls.setdefault("shap", []).append((a, k)) or "b.obj",
    )
    monkeypatch.setattr(
        opendream,
        "generate_model",
        lambda *a, **k: calls.setdefault("open", []).append((a, k)) or "c.obj",
    )
    monkeypatch.setattr(
        dreamfusion,
        "generate_model",
        lambda *a, **k: calls.setdefault("dream", []).append((a, k)) or "d.obj",
    )

    vars = dict(
        prompt_widget=DummyText("cube"),
        status_widget=DummyStatus(),
        model_var=DummyVar("model"),
        device_var=DummyVar("cpu"),
        dir_var=DummyVar("models"),
        name_var=DummyVar("cube"),
        quality_var=DummyVar(64),
    )

    run_generate_model(tool_var=DummyVar("Stable Fast 3D"), **vars)
    run_generate_model(tool_var=DummyVar("Shap-E"), **vars)
    run_generate_model(tool_var=DummyVar("OpenDream"), **vars)
    run_generate_model(tool_var=DummyVar("Stable DreamFusion"), **vars)

    assert calls == {
        "fast": [(("cube", "model"), {"device": "cpu", "save_dir": "models", "name": "cube"})],
        "shap": [(("cube",), {"device": "cpu", "save_dir": "models", "name": "cube"})],
        "open": [(("cube",), {"quality": 64, "save_dir": "models", "name": "cube"})],
        "dream": [(("cube", "model"), {"device": "cpu", "save_dir": "models", "name": "cube"})],
    }
