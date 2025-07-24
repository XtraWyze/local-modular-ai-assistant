from modules import speech_learning

class DummyRec:
    def __init__(self):
        self.count = 0

    def listen(self, mic, *a, **kw):
        self.count += 1
        return f"audio{self.count}"

    def recognize_google(self, audio):
        return f"heard {audio}"

class DummyMic:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass

def test_read_sentences_mock():
    rec = DummyRec()
    mic = DummyMic()
    sentences = ["one", "two"]
    out = speech_learning.read_sentences(sentences, recognizer=rec, microphone=mic)
    assert out == ["heard audio1", "heard audio2"]


class SilentRec:
    def listen(self, mic, timeout=1, phrase_time_limit=6):
        return "audio"

    def recognize_google(self, audio):
        raise Exception("no speech")


def test_cancel_after_timeout(monkeypatch):
    rec = SilentRec()
    mic = DummyMic()

    fake = {"t": 0.0}

    def fake_time():
        fake["t"] += 1.0
        return fake["t"]

    monkeypatch.setattr(speech_learning, "time", type("T", (), {"time": fake_time, "sleep": lambda x: None}))

    out = speech_learning.read_sentences(["one"], recognizer=rec, microphone=mic, pause_secs=0, cancel_after=5)
    assert out == [""]


def test_get_description():
    assert isinstance(speech_learning.get_description(), str)
