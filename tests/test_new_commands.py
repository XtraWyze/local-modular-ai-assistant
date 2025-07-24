import importlib
import types
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


def test_process_input_pause_music(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    monkeypatch.setattr(assistant, 'speak', lambda *a, **kw: None)
    mc = importlib.import_module('modules.media_controls')
    calls = []
    monkeypatch.setattr(mc, 'play_pause', lambda: calls.append('pause') or 'ok')
    assistant.set_listening(True)
    assistant.process_input('pause music', DummyWidget())
    assert calls == ['pause']


def test_process_input_skip_song(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    monkeypatch.setattr(assistant, 'speak', lambda *a, **kw: None)
    mc = importlib.import_module('modules.media_controls')
    calls = []
    monkeypatch.setattr(mc, 'next_track', lambda: calls.append('skip') or 'ok')
    assistant.set_listening(True)
    assistant.process_input('skip song', DummyWidget())
    assert calls == ['skip']


def test_process_input_type_text(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    monkeypatch.setattr(assistant, 'speak', lambda *a, **kw: None)
    typed = []
    fake_kb = types.SimpleNamespace(write=lambda t: typed.append(t))
    monkeypatch.setattr(assistant, 'keyboard', fake_kb, raising=False)
    assistant.set_listening(True)
    assistant.process_input('type hello world', DummyWidget())
    assert typed == ['hello world']


def test_process_input_move_mouse(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    monkeypatch.setattr(assistant, 'speak', lambda *a, **kw: None)
    moved = []
    fake_pg = types.SimpleNamespace(
        moveTo=lambda x, y, duration=1: moved.append((x, y)),
        write=lambda *a, **k: None,
        press=lambda *a, **k: None,
        click=lambda *a, **k: None,
    )
    monkeypatch.setattr(assistant, 'pyautogui', fake_pg, raising=False)
    assistant.set_listening(True)
    assistant.process_input('move mouse to 10 20', DummyWidget())
    assert moved == [(10, 20)]
