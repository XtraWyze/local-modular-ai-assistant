import importlib
import sys
import types


def test_tts_load_error(monkeypatch):
    """Model loading errors should be caught and returned as a message."""
    np_stub = types.ModuleType("numpy")
    np_stub.array = lambda x: x
    sd_stub = types.ModuleType("sounddevice")
    sd_stub.play = lambda *a, **kw: None
    sd_stub.wait = lambda: None
    monkeypatch.setitem(sys.modules, "numpy", np_stub)
    monkeypatch.setitem(sys.modules, "sounddevice", sd_stub)

    api_stub = types.ModuleType("TTS.api")
    def fail(*a, **kw):
        raise RuntimeError("load fail")
    api_stub.TTS = fail
    tts_stub = types.ModuleType("TTS")
    tts_stub.api = api_stub
    monkeypatch.setitem(sys.modules, "TTS", tts_stub)
    monkeypatch.setitem(sys.modules, "TTS.api", api_stub)

    tts = importlib.import_module("modules.tts_integration")
    importlib.reload(tts)

    result = tts.speak("hello", async_play=False)
    assert result.startswith("[TTS] load error:")
