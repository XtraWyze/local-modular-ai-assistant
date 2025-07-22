import importlib
import types


def test_play_pause_missing_keyboard(monkeypatch):
    mc = importlib.import_module('modules.media_controls')
    monkeypatch.setattr(mc, 'keyboard', None)
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


def test_volume_down(monkeypatch):
    mc = importlib.import_module('modules.media_controls')
    events = []
    fake_kb = types.SimpleNamespace(send=lambda name: events.append(name))
    monkeypatch.setattr(mc, 'keyboard', fake_kb)
    monkeypatch.setattr(mc, '_IMPORT_ERROR', None)
    out = mc.volume_down()
    assert 'Volume down pressed' in out
    assert events == ['volume down']
