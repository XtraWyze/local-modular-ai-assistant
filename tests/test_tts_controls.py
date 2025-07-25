import importlib
import json
import sys
import types


def setup_tts(monkeypatch, tmp_path):
    # stub numpy and sounddevice
    np_stub = types.ModuleType("numpy")
    np_stub.array = lambda x: x
    sd_stub = types.ModuleType("sounddevice")
    sd_stub.play = lambda *args, **kwargs: None
    sd_stub.wait = lambda: None
    TTS_api_stub = types.ModuleType("TTS.api")
    class DummySynth:
        output_sample_rate = 22050
    class DummyTTS:
        def __init__(self, *a, **k):
            self.synthesizer = DummySynth()
        def tts(self, text, speaker=None):
            return [0.0]
    TTS_api_stub.TTS = lambda *a, **k: DummyTTS()
    TTS_stub = types.ModuleType("TTS")
    TTS_stub.api = TTS_api_stub

    monkeypatch.setitem(sys.modules, "numpy", np_stub)
    monkeypatch.setitem(sys.modules, "sounddevice", sd_stub)
    monkeypatch.setitem(sys.modules, "TTS", TTS_stub)
    monkeypatch.setitem(sys.modules, "TTS.api", TTS_api_stub)

    tts = importlib.import_module("modules.tts_integration")
    importlib.reload(tts)

    cfg = {"tts_volume": 0.5, "tts_voice": None, "tts_speed": 1.0, "tts_model": "m"}
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(cfg))
    monkeypatch.setattr(tts, "CONFIG_PATH", str(config_path), raising=False)
    tts.config = cfg
    return tts, config_path


def test_set_volume_and_voice(monkeypatch, tmp_path):
    tts, cfg_file = setup_tts(monkeypatch, tmp_path)
    assert tts.set_volume(0.7) is True
    saved = json.loads(cfg_file.read_text())
    assert saved["tts_volume"] == 0.7
    assert tts.config["tts_volume"] == 0.7

    assert tts.set_voice("alice") is True
    saved = json.loads(cfg_file.read_text())
    assert saved["tts_voice"] == "alice"
    assert tts.config["tts_voice"] == "alice"

    # invalid volume
    err = tts.set_volume(1.5)
    assert err is not True


def test_set_speed(monkeypatch, tmp_path):
    tts, cfg_file = setup_tts(monkeypatch, tmp_path)

    assert tts.set_speed(1.2) is True
    saved = json.loads(cfg_file.read_text())
    assert saved["tts_speed"] == 1.2
    assert tts.config["tts_speed"] == 1.2

    assert tts.set_speed(2.5) is False
