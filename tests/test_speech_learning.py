from modules import speech_learning

class DummyRec:
    def __init__(self):
        self.count = 0
    def listen(self, mic, phrase_time_limit=6):
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


def test_get_description():
    assert isinstance(speech_learning.get_description(), str)
