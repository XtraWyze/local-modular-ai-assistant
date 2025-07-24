import importlib
import sys
import types


def _make_psutil(cpu_percent=10.0, mem_percent=10.0):
    psutil = types.SimpleNamespace()
    psutil.cpu_percent = lambda interval=None: cpu_percent
    mem = types.SimpleNamespace(percent=mem_percent)
    psutil.virtual_memory = lambda: mem
    return psutil


def test_is_overloaded_true(monkeypatch):
    ps = _make_psutil(cpu_percent=95.0, mem_percent=50.0)
    monkeypatch.setitem(sys.modules, 'psutil', ps)
    mod = importlib.reload(importlib.import_module('modules.system_load'))
    assert mod.is_overloaded()


def test_wait_for_load_timeout(monkeypatch):
    ps = _make_psutil(cpu_percent=95.0, mem_percent=95.0)
    monkeypatch.setitem(sys.modules, 'psutil', ps)
    mod = importlib.reload(importlib.import_module('modules.system_load'))
    assert not mod.wait_for_load(timeout=0.1, check_interval=0.05)
