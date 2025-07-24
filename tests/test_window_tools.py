import importlib
from modules.window_tools import close_taskbar_item, minimize_window

def test_invalid_index():
    ok, msg = close_taskbar_item(-1)
    assert not ok
    assert "Invalid window index" in msg


def test_minimize_window_not_found(monkeypatch):
    wt = importlib.import_module('modules.window_tools')
    fake_gw = type('GW', (), {
        'getAllTitles': lambda: [],
    })
    monkeypatch.setattr(wt, 'gw', fake_gw)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    ok, msg = minimize_window('xyz')
    assert not ok
    assert 'No window found' in msg


def test_minimize_window_success(monkeypatch):
    wt = importlib.import_module('modules.window_tools')
    events = {}

    class FakeWin:
        def __init__(self, title):
            self.title = title
        def minimize(self):
            events['min'] = True

    fake_gw = type('GW', (), {
        'getAllTitles': lambda: ['My App'],
        'getWindowsWithTitle': lambda t: [FakeWin(t)],
    })
    monkeypatch.setattr(wt, 'gw', fake_gw)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    ok, msg = minimize_window('my app')
    assert ok
    assert events.get('min')
    assert 'My App' in msg
