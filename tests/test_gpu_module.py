import importlib
import types


def test_is_available_false(monkeypatch):
    # Simulate torch not installed
    monkeypatch.setitem(importlib.sys.modules, 'torch', None)
    gpu = importlib.reload(importlib.import_module('modules.gpu'))
    assert gpu.is_available() is False
    assert gpu.get_device() == 'cpu'
    assert gpu.get_devices() == []


def test_is_available_true(monkeypatch):
    torch_mod = types.SimpleNamespace(
        cuda=types.SimpleNamespace(
            is_available=lambda: True,
            device_count=lambda: 2,
        ),
        autocast=lambda device: ('ctx', device),
    )
    monkeypatch.setitem(importlib.sys.modules, 'torch', torch_mod)
    gpu = importlib.reload(importlib.import_module('modules.gpu'))
    assert gpu.is_available() is True
    assert gpu.get_device() == 'cuda'
    assert gpu.get_devices() == ['cuda:0', 'cuda:1']
    ctx = gpu.autocast('cuda')
    assert ctx == ('ctx', 'cuda')
