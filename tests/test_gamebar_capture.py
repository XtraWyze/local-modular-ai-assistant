import importlib
import types


def test_open_capture_keyboard(monkeypatch):
    gb = importlib.import_module('modules.gamebar_capture')
    events = []
    mock_kb = types.SimpleNamespace(send=lambda combo: events.append(combo))
    monkeypatch.setattr(gb, 'keyboard', mock_kb)
    monkeypatch.setattr(gb, 'pyautogui', None, raising=False)
    monkeypatch.setattr(gb.sys, 'platform', 'win32')
    monkeypatch.setattr(gb, '_IMPORT_ERROR', None)
    out = gb.open_capture()
    assert events == ['win+g']
    assert 'opened' in out.lower()


def test_toggle_recording_pyautogui(monkeypatch):
    gb = importlib.import_module('modules.gamebar_capture')
    events = []
    mock_pg = types.SimpleNamespace(hotkey=lambda *keys: events.append('+'.join(keys)))
    monkeypatch.setattr(gb, 'keyboard', None)
    monkeypatch.setattr(gb, 'pyautogui', mock_pg, raising=False)
    monkeypatch.setattr(gb.sys, 'platform', 'win32')
    monkeypatch.setattr(gb, '_IMPORT_ERROR', RuntimeError('missing'))
    out = gb.toggle_recording()
    assert events == ['win+alt+r']
    assert 'toggled' in out.lower()


def test_capture_last_30s_non_windows(monkeypatch):
    gb = importlib.import_module('modules.gamebar_capture')
    monkeypatch.setattr(gb.sys, 'platform', 'linux')
    out = gb.capture_last_30s()
    assert 'windows' in out.lower()


def test_screenshot_no_backend(monkeypatch):
    gb = importlib.import_module('modules.gamebar_capture')
    monkeypatch.setattr(gb, 'keyboard', None)
    monkeypatch.setattr(gb, 'pyautogui', None, raising=False)
    monkeypatch.setattr(gb.sys, 'platform', 'win32')
    monkeypatch.setattr(gb, '_IMPORT_ERROR', RuntimeError('missing'))
    out = gb.capture_screenshot()
    assert 'keyboard module missing' in out
