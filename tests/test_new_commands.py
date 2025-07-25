import importlib
import types
import sys
from tests.test_assistant_utils import import_assistant

sys.modules.setdefault('comtypes', types.SimpleNamespace(CLSCTX_ALL=None))
pycaw_stub = types.ModuleType('pycaw')
pycaw_stub.pycaw = types.SimpleNamespace(
    IAudioEndpointVolume=None,
    MMDeviceEnumerator=None,
    EDataFlow=None,
    ERole=None,
)
sys.modules.setdefault('pycaw', pycaw_stub)
sys.modules.setdefault('pycaw.pycaw', pycaw_stub.pycaw)

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
    mock_kb = types.SimpleNamespace(write=lambda t: typed.append(t))
    monkeypatch.setattr(assistant, 'keyboard', mock_kb, raising=False)
    assistant.set_listening(True)
    assistant.process_input('type hello world', DummyWidget())
    assert typed == ['hello world']


def test_process_input_move_mouse(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    monkeypatch.setattr(assistant, 'speak', lambda *a, **kw: None)
    moved = []
    mock_pg = types.SimpleNamespace(
        moveTo=lambda x, y, duration=1: moved.append((x, y)),
        write=lambda *a, **k: None,
        press=lambda *a, **k: None,
        click=lambda *a, **k: None,
    )
    monkeypatch.setattr(assistant, 'pyautogui', mock_pg, raising=False)
    assistant.set_listening(True)
    assistant.process_input('move mouse to 10 20', DummyWidget())
    assert moved == [(10, 20)]


def test_process_input_move_window(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    monkeypatch.setattr(assistant, 'speak', lambda *a, **kw: None)
    wt = importlib.import_module('modules.window_tools')
    calls = []
    monkeypatch.setattr(wt, 'move_window_to_monitor', lambda t, m: calls.append((t, m)) or (True, 'ok'))
    assistant.set_listening(True)
    assistant.process_input('move chrome to monitor 2', DummyWidget())
    assert calls == [('chrome', 2)]


def test_process_input_set_system_volume(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    monkeypatch.setattr(assistant, 'speak', lambda *a, **kw: None)
    sv = importlib.import_module('modules.system_volume')
    calls = []
    monkeypatch.setattr(sv, 'set_volume', lambda v: calls.append(v) or 'ok')
    assistant.set_listening(True)
    assistant.process_input('set system volume to 30', DummyWidget())
    assert calls == [30]


def test_process_input_increase_system_volume(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    monkeypatch.setattr(assistant, 'speak', lambda *a, **kw: None)
    mc = importlib.import_module('modules.media_controls')
    calls = []
    monkeypatch.setattr(mc, 'volume_up', lambda: calls.append('up') or 'ok')
    assistant.set_listening(True)
    assistant.process_input('increase system volume', DummyWidget())
    assert calls == ['up']
