import importlib
import json
import os
import sys
import pytest


@pytest.mark.skipif(os.environ.get("DISPLAY") is None, reason="GUI not available")
def test_save_settings_writes_hide(monkeypatch, tmp_path):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "1")
    base = json.load(open("config.json", "r"))
    base["hide_cmd_window"] = True
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps(base))
    from config_loader import ConfigLoader as CL
    monkeypatch.setattr("config_loader.ConfigLoader", lambda path='config.json': CL(str(cfg_path)))
    if "gui_assistant" in sys.modules:
        del sys.modules["gui_assistant"]
    ga = importlib.import_module("gui_assistant")
    ga.hide_cmd_var.set(False)
    ga.save_settings()
    saved = json.loads(cfg_path.read_text())
    assert saved["hide_cmd_window"] is False

