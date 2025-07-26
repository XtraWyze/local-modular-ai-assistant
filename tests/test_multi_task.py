from tests.test_assistant_utils import import_assistant


class DummyWidget:
    def insert(self, *a, **kw):
        pass

    def see(self, *a, **kw):
        pass


def test_process_input_multiple_commands(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    monkeypatch.setattr(assistant, 'speak', lambda *a, **kw: None)
    queued = []
    monkeypatch.setattr(assistant, 'queue_command', lambda t, w: queued.append(t))
    monkeypatch.setattr(assistant, '_run_next_in_queue', lambda: None)
    assistant.process_input('play music and open rocket league', DummyWidget())
    assert queued == []
