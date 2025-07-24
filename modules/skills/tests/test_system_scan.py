import sys
import types

from modules.skills import system_scan


def test_run(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        'modules.window_tools',
        types.SimpleNamespace(list_open_windows=lambda: ['win1', 'win2'])
    )
    monkeypatch.setitem(
        sys.modules,
        'modules.browser_automation',
        types.SimpleNamespace(count_tabs=lambda: 5)
    )
    monkeypatch.setitem(
        sys.modules,
        'modules.calendar_tools',
        types.SimpleNamespace(get_next_appointment=lambda: '10 AM Meeting')
    )
    monkeypatch.setitem(
        sys.modules,
        'modules.automation_actions',
        types.SimpleNamespace(get_clipboard=lambda: 'copy text')
    )
    monkeypatch.setitem(
        sys.modules,
        'modules.device_scanner',
        types.SimpleNamespace(
            list_network_devices=lambda: ['ip1'],
            list_usb_devices=lambda: ['usb1']
        )
    )
    monkeypatch.setattr(system_scan.os, 'getcwd', lambda: '/tmp')

    summary = system_scan.run({})
    assert 'Open windows: 2' in summary
    assert 'Browser tabs: 5' in summary
    assert 'Working directory: /tmp' in summary
    assert '10 AM Meeting' in summary
    assert 'copy text' in summary
    assert 'Network devices detected: 1' in summary
    assert 'USB devices detected: 1' in summary
