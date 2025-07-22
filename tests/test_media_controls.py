import importlib
import types
import sys


def test_play_pause_non_windows(monkeypatch):
    mc = importlib.import_module('modules.media_controls')
    monkeypatch.setattr(sys, 'platform', 'linux')
    out = mc.play_pause()
    assert 'Windows' in out


def test_play_pause_windows(monkeypatch):
    mc = importlib.import_module('modules.media_controls')
    monkeypatch.setattr(sys, 'platform', 'win32')

    class DummyUser32:
        def __init__(self):
            self.calls = []
        def keybd_event(self, code, a, flag, d):
            self.calls.append((code, flag))

    dummy_user32 = DummyUser32()
    dummy_ctypes = types.SimpleNamespace(windll=types.SimpleNamespace(user32=dummy_user32))
    monkeypatch.setattr(mc, 'ctypes', dummy_ctypes)

    out = mc.play_pause()
    assert 'Play/Pause pressed' in out
    assert (mc.VK_MEDIA_PLAY_PAUSE, 0) in dummy_user32.calls
    assert (mc.VK_MEDIA_PLAY_PAUSE, 0x0002) in dummy_user32.calls

