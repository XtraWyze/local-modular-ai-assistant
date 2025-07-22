from tests.test_assistant_utils import import_assistant

class DummyWidget:
    def insert(self, *a, **kw):
        pass
    def see(self, *a, **kw):
        pass

def test_process_input_plan(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    monkeypatch.setattr(assistant, 'speak', lambda *a, **kw: None)
    queued = []
    monkeypatch.setattr(assistant, 'queue_command', lambda t, w: queued.append(t))
    assistant.process_input('plan open app then close app', DummyWidget())
    assert queued == ['open app', 'close app']
