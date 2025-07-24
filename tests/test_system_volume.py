import importlib
import types
import sys

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

def test_set_volume(monkeypatch):
    sv = importlib.import_module('modules.system_volume')
    monkeypatch.setattr(sv.sys, 'platform', 'win32')
    class EP:
        def SetMasterVolumeLevelScalar(self, val, _):
            self.value = val
    ep = EP()
    monkeypatch.setattr(sv, '_get_endpoint', lambda: ep)
    out = sv.set_volume(40)
    assert ep.value == 0.4
    assert '40%' in out
    assert sv.set_volume(150) == 'Volume must be 0-100'


def test_get_volume(monkeypatch):
    sv = importlib.import_module('modules.system_volume')
    monkeypatch.setattr(sv.sys, 'platform', 'win32')
    class EP:
        def GetMasterVolumeLevelScalar(self):
            return 0.7
    monkeypatch.setattr(sv, '_get_endpoint', lambda: EP())
    assert sv.get_volume() == 70
