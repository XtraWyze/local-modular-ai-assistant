from tests.test_assistant_utils import import_assistant
import scan_registry


class DummyWidget:
    def insert(self, *a, **kw):
        pass
    def see(self, *a, **kw):
        pass


def test_scan_voice_commands(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    calls = []
    monkeypatch.setattr(assistant, 'speak', lambda msg, **kw: calls.append(msg))
    assistant.set_listening(True)

    scan_registry.system_data = {'summary': 'ok'}
    scan_registry.device_data = ['d1']
    scan_registry.network_data = ['n1']

    assistant.process_input('refresh device scan', DummyWidget())
    import time
    for _ in range(20):
        if assistant.get_state() == 'idle':
            break
        time.sleep(0.05)
    assert 'refreshed' in assistant.last_ai_response
