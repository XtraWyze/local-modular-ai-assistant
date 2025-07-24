import importlib
import types
from tests.test_assistant_utils import import_assistant


def test_start_hotkey_missing_keyboard(monkeypatch):
    hk = importlib.import_module('modules.listen_hotkey')
    monkeypatch.setattr(hk, 'keyboard', None)
    monkeypatch.setattr(hk, '_IMPORT_ERROR', RuntimeError('missing'))
    out = hk.start_hotkey()
    assert 'disabled' in out


def test_start_hotkey(monkeypatch):
    hk = importlib.import_module('modules.listen_hotkey')
    events = []
    fake_kb = types.SimpleNamespace(add_hotkey=lambda k, cb: events.append(k))
    monkeypatch.setattr(hk, 'keyboard', fake_kb)
    monkeypatch.setattr(hk, '_IMPORT_ERROR', None)
    out = hk.start_hotkey()
    assert 'disabled' in out
    assert events == []


def test_trigger_toggle(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    hk = importlib.import_module('modules.listen_hotkey')
    monkeypatch.setattr(hk, 'set_listening', assistant.set_listening)
    monkeypatch.setattr(hk, 'is_listening', assistant.is_listening)
    monkeypatch.setattr(hk, 'cancel_processing', lambda: None)
    monkeypatch.setattr(hk, 'stop_speech', lambda: None)
    assistant.set_listening(False)
    hk.trigger()
    assert assistant.is_listening() is True
    hk.trigger()
    assert assistant.is_listening() is False
