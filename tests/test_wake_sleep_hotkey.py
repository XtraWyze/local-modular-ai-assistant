import importlib
import types
from tests.test_assistant_utils import import_assistant


def test_start_hotkeys_missing_keyboard(monkeypatch):
    mod = importlib.import_module('modules.wake_sleep_hotkey')
    monkeypatch.setattr(mod, 'keyboard', None)
    monkeypatch.setattr(mod, '_IMPORT_ERROR', RuntimeError('missing'))
    out = mod.start_hotkeys()
    assert 'keyboard module missing' in out


def test_start_hotkeys(monkeypatch):
    mod = importlib.import_module('modules.wake_sleep_hotkey')
    events = []
    mock_kb = types.SimpleNamespace(
        add_hotkey=lambda k, cb: events.append(k),
        remove_hotkey=lambda k: events.remove(k) if k in events else None,
    )
    monkeypatch.setattr(mod, 'keyboard', mock_kb)
    monkeypatch.setattr(mod, '_IMPORT_ERROR', None)
    out = mod.start_hotkeys()
    assert mod.WAKE_HOTKEY in out and mod.SLEEP_HOTKEY in out
    assert events == [mod.WAKE_HOTKEY, mod.SLEEP_HOTKEY]

    # update hotkeys
    msg = mod.set_hotkeys('alt+w', 'alt+s')
    assert 'alt+w' in msg and 'alt+s' in msg
    assert events == ['alt+w', 'alt+s']


def test_trigger_actions(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    mod = importlib.import_module('modules.wake_sleep_hotkey')

    monkeypatch.setattr(mod, 'set_listening', assistant.set_listening)
    monkeypatch.setattr(mod, 'is_listening', assistant.is_listening)
    monkeypatch.setattr(mod, 'cancel_processing', lambda: None)
    monkeypatch.setattr(mod, 'stop_speech', lambda: None)

    assistant.set_listening(False)
    mod.trigger_wake()
    assert assistant.is_listening() is True

    mod.trigger_sleep()
    assert assistant.is_listening() is False
