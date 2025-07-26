import importlib
import json
import os
import sys
import types
import pytest

@pytest.mark.skipif(os.environ.get("DISPLAY") is None, reason="GUI not available")
def test_pro_mode_toggle(monkeypatch, tmp_path):
    cfg = {"pro_mode": False, "tts_backend": "coqui", "stt_backend": "vosk"}
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps(cfg))

    from config_loader import ConfigLoader as CL
    monkeypatch.setattr("config_loader.ConfigLoader", lambda path='config.json': CL(str(cfg_file)))

    if "gui_assistant" in sys.modules:
        del sys.modules["gui_assistant"]

    ga = importlib.import_module("gui_assistant")
    monkeypatch.setattr(ga, "has_internet", lambda: True)
    ga.pro_var.set(True)
    ga.toggle_pro_mode()
    saved = json.loads(cfg_file.read_text())
    assert saved["pro_mode"] is True
    assert saved["tts_backend"] == "huggingface"
    assert saved["stt_backend"] == "huggingface"
