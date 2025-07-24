import importlib
import sys
import types

sys.modules.setdefault('keyboard', types.ModuleType('keyboard'))
sys.modules.setdefault('pyautogui', types.ModuleType('pyautogui'))
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

from cli_assistant import process_command


def test_cli_set_volume(monkeypatch):
    sv = importlib.import_module('modules.system_volume')
    calls = []
    monkeypatch.setattr(sv, 'set_volume', lambda v: calls.append(v) or 'ok')
    out = process_command('set volume 80')
    assert calls == [80]
    assert out == 'ok'


def test_cli_volume_up(monkeypatch):
    mc = importlib.import_module('modules.media_controls')
    calls = []
    monkeypatch.setattr(mc, 'volume_up', lambda: calls.append('up') or 'ok')
    out = process_command('volume up')
    assert calls == ['up']
    assert out == 'ok'
