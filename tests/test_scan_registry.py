import importlib
import sys
import types


def test_refresh_functions(tmp_path, monkeypatch):
    sr = importlib.import_module('scan_registry')
    monkeypatch.setattr(sr, 'SYSTEM_FILE', str(tmp_path / 'sys.json'), raising=False)
    monkeypatch.setattr(sr, 'DEVICE_FILE', str(tmp_path / 'dev.json'), raising=False)
    monkeypatch.setattr(sr, 'NETWORK_FILE', str(tmp_path / 'net.json'), raising=False)

    sys.modules['modules.system_scan'] = types.SimpleNamespace(run=lambda params: 'summary')
    orch = importlib.import_module('orchestrator')
    monkeypatch.setattr(orch, 'handle_system_scan', lambda: {'cpu': 1})
    sys.modules['modules.device_scanner'] = types.SimpleNamespace(
        list_usb_devices=lambda: ['usb'],
        list_network_devices=lambda: ['1.2.3.4']
    )

    sr.refresh_all()
    assert sr.system_data['summary'] == 'summary'
    assert sr.device_data == ['usb']
    assert sr.network_data == ['1.2.3.4']

    # Files should be created
    assert (tmp_path / 'sys.json').exists()
    assert (tmp_path / 'dev.json').exists()
    assert (tmp_path / 'net.json').exists()
