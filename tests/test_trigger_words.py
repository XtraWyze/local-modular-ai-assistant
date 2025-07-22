from tests.test_assistant_utils import import_assistant

class DummyWidget:
    def insert(self, *a, **kw):
        pass
    def see(self, *a, **kw):
        pass

def test_get_trigger_words_summary(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    summary = assistant.get_trigger_words_summary()
    assert "actions" in summary
    assert "enter" in summary


def test_process_input_trigger_words(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    monkeypatch.setattr(assistant, "speak", lambda *a, **kw: None)
    assistant.set_listening(True)
    assistant.process_input("what are the trigger words", DummyWidget())
    assert "actions" in assistant.last_ai_response
