import json
import importlib


def test_add_wake_phrase(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text("{}")
    pm = importlib.import_module('phrase_manager')
    monkeypatch.setattr(pm, 'CONFIG_PATH', str(cfg_file), raising=False)
    pm.config = {}

    msg = pm.add_wake_phrase("jarvis")
    assert "jarvis" in json.loads(cfg_file.read_text())["wake_phrases"]
    assert "jarvis" in pm.config["wake_phrases"]
    assert "Added" in msg

    msg_dup = pm.add_wake_phrase("jarvis")
    assert "already" in msg_dup


def test_add_sleep_and_cancel_phrase(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text("{}")
    pm = importlib.import_module('phrase_manager')
    monkeypatch.setattr(pm, 'CONFIG_PATH', str(cfg_file), raising=False)
    pm.config = {}

    pm.add_sleep_phrase("good night")
    pm.add_cancel_phrase("abort")
    saved = json.loads(cfg_file.read_text())
    assert "good night" in saved["sleep_phrases"]
    assert "abort" in saved["cancel_phrases"]



