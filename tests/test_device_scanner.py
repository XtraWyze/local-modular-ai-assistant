import importlib
import sys
import types


def test_list_network_devices(monkeypatch):
    mod = importlib.import_module('modules.device_scanner')
    fake_out = "Interface: 192.168.1.1\n  Internet Address      Physical Address\n  192.168.1.2    aa-bb-cc-dd-ee-ff"
    monkeypatch.setattr(mod.subprocess, 'check_output', lambda *a, **k: fake_out)
    ips = mod.list_network_devices()
    assert '192.168.1.2' in ips


def test_list_usb_devices_psutil(monkeypatch):
    fake_part = types.SimpleNamespace(device='/dev/sdb1', opts='rw,removable')
    fake_psutil = types.SimpleNamespace(disk_partitions=lambda all=False: [fake_part])
    monkeypatch.setitem(sys.modules, 'psutil', fake_psutil)
    mod = importlib.reload(importlib.import_module('modules.device_scanner'))
    devices = mod.list_usb_devices()
    assert '/dev/sdb1' in devices


def test_list_usb_devices_lsusb(monkeypatch):
    sys.modules.pop('psutil', None)
    mod = importlib.reload(importlib.import_module('modules.device_scanner'))
    monkeypatch.setattr(mod.subprocess, 'check_output', lambda *a, **k: 'Bus 001 Device 002: ID 1234:abcd Dev')
    devices = mod.list_usb_devices()
    assert any('ID 1234:abcd' in d for d in devices)
