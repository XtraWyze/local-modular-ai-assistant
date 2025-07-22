from tests.test_assistant_utils import import_assistant

class DummyWidget:
    def insert(self, *a, **kw):
        pass
    def see(self, *a, **kw):
        pass

def test_polite_open_command(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    monkeypatch.setattr(assistant, 'speak', lambda *a, **kw: None)
    monkeypatch.setattr(assistant, 'build_shortcut_map', lambda: {}, raising=False)
    calls = []
    monkeypatch.setattr(assistant, 'open_shortcut', lambda text, mp: calls.append(text) or 'ok', raising=False)
    assistant.process_input('Could you please open notepad?', DummyWidget())
    assert calls == ['open notepad']
