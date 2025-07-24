import importlib
import types


def test_play_pause_missing_keyboard(monkeypatch):
    mc = importlib.import_module('modules.media_controls')
    monkeypatch.setattr(mc, 'keyboard', None)
    monkeypatch.setattr(mc, 'pyautogui', None, raising=False)
    monkeypatch.setattr(mc.sys, 'platform', 'linux')
    monkeypatch.setattr(mc, '_IMPORT_ERROR', RuntimeError('missing'))
    out = mc.play_pause()
    assert 'keyboard module missing' in out


def test_play_pause_sends_key(monkeypatch):
    mc = importlib.import_module('modules.media_controls')
    events = []
    fake_kb = types.SimpleNamespace(send=lambda name: events.append(name))
    monkeypatch.setattr(mc, 'keyboard', fake_kb)
    monkeypatch.setattr(mc, '_IMPORT_ERROR', None)
    out = mc.play_pause()
    assert 'Play/Pause pressed' in out
    assert events == ['play/pause media']


def test_play_pause_win32_fallback(monkeypatch):
    mc = importlib.import_module('modules.media_controls')
    monkeypatch.setattr(mc, 'keyboard', None)
    events = []
    monkeypatch.setattr(mc.sys, 'platform', 'win32')
    monkeypatch.setattr(mc, '_IMPORT_ERROR', RuntimeError('missing'))
    monkeypatch.setattr(mc, 'pyautogui', None, raising=False)
    monkeypatch.setattr(mc, '_send_key_win32', lambda vk: events.append(vk))
    out = mc.play_pause()
    assert 'Play/Pause pressed' in out
    assert events == [0xB3]


def test_play_pause_pyautogui_fallback(monkeypatch):
    mc = importlib.import_module('modules.media_controls')
    monkeypatch.setattr(mc, 'keyboard', None)
    monkeypatch.setattr(mc.sys, 'platform', 'linux')
    events = []
    fake_pg = types.SimpleNamespace(press=lambda key: events.append(key))
    monkeypatch.setattr(mc, 'pyautogui', fake_pg, raising=False)
    monkeypatch.setattr(mc, '_IMPORT_ERROR', RuntimeError('missing'))
    out = mc.play_pause()
    assert 'Play/Pause pressed' in out
    assert events == ['playpause']


def test_volume_down(monkeypatch):
    mc = importlib.import_module('modules.media_controls')
    events = []
    fake_kb = types.SimpleNamespace(send=lambda name: events.append(name))
    monkeypatch.setattr(mc, 'keyboard', fake_kb)
    monkeypatch.setattr(mc, '_IMPORT_ERROR', None)
    out = mc.volume_down()
    assert 'Volume down pressed' in out
    assert events == ['volume down']
