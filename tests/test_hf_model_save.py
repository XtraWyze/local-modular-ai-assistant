import importlib
import json
import os
import sys
import pytest

@pytest.mark.skipif(os.environ.get("DISPLAY") is None, reason="GUI not available")
def test_save_hf_models(monkeypatch, tmp_path):
    cfg = {"pro_mode": True, "hf_tts_model": "", "hf_stt_model": ""}
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps(cfg))

    from config_loader import ConfigLoader as CL
    monkeypatch.setattr("config_loader.ConfigLoader", lambda path='config.json': CL(str(cfg_file)))

    monkeypatch.setenv("PYTEST_CURRENT_TEST", "1")
    if "gui_assistant" in sys.modules:
        del sys.modules["gui_assistant"]
    ga = importlib.import_module("gui_assistant")
    ga.hf_tts_var.set("tts")
    ga.save_hf_tts_model()
    ga.hf_stt_var.set("stt")
    ga.save_hf_stt_model()

    saved = json.loads(cfg_file.read_text())
    assert saved["hf_tts_model"] == "tts"
    assert saved["hf_stt_model"] == "stt"
