import importlib
import types
import sys


def test_speak_speed(monkeypatch):
    # Stub numpy providing minimal array behavior
    class DummyArray(list):
        def __mul__(self, other):
            return DummyArray([x * other for x in self])
    np_stub = types.ModuleType("numpy")
    np_stub.array = lambda x: DummyArray(x)

    # Capture calls to sounddevice
    calls = []
    waited = []
    sd_stub = types.ModuleType("sounddevice")
    def sd_play(wav, rate):
        calls.append(rate)
    def sd_wait():
        waited.append(True)
    sd_stub.play = sd_play
    sd_stub.wait = sd_wait

    # Minimal TTS implementation
    class DummySynth:
        output_sample_rate = 22050
    class DummyTTS:
        def __init__(self, *args, **kwargs):
            self.synthesizer = DummySynth()
        def tts(self, text, speaker=None):
            return [0.0, 0.1, 0.2]

    TTS_api_stub = types.ModuleType("TTS.api")
    TTS_api_stub.TTS = lambda *args, **kwargs: DummyTTS()
    TTS_stub = types.ModuleType("TTS")
    TTS_stub.api = TTS_api_stub

    # Patch sys.modules so tts_integration imports these stubs
    monkeypatch.setitem(sys.modules, "numpy", np_stub)
    monkeypatch.setitem(sys.modules, "sounddevice", sd_stub)
    monkeypatch.setitem(sys.modules, "TTS", TTS_stub)
    monkeypatch.setitem(sys.modules, "TTS.api", TTS_api_stub)

    tts = importlib.import_module("modules.tts_integration")
    importlib.reload(tts)

    result = tts.speak("hello", async_play=False, speed=0.5)

    assert result == "[TTS] Done speaking."
    assert calls[-1] == int(DummySynth.output_sample_rate * 0.5)
    assert waited

    calls.clear()
    tts.config["tts_speed"] = 1.3
    result2 = tts.speak("test", async_play=False)
    assert result2 == "[TTS] Done speaking."
    assert calls[-1] == int(DummySynth.output_sample_rate * 1.3)
