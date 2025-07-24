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


def test_move_window_to_monitor(monkeypatch):
    wt = importlib.import_module('modules.window_tools')
    vt = importlib.import_module('modules.vision_tools')

    class FakeWin:
        def __init__(self, title):
            self.title = title
        def moveTo(self, x, y):
            self.moved = (x, y)

    fake_gw = type('GW', (), {
        'getWindowsWithTitle': lambda t: [FakeWin(t)]
    })
    monkeypatch.setattr(wt, 'gw', fake_gw)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    monitors = [
        type('M', (), {'x': 0, 'y': 0})(),
        type('M', (), {'x': 100, 'y': 0})(),
    ]
    monkeypatch.setattr(vt, 'get_monitors', lambda: monitors)

    ok, msg = wt.move_window_to_monitor('test', 1)
    assert ok
    assert 'monitor 1' in msg


def test_move_window_to_monitor_invalid(monkeypatch):
    wt = importlib.import_module('modules.window_tools')
    vt = importlib.import_module('modules.vision_tools')

    fake_gw = type('GW', (), {'getWindowsWithTitle': lambda t: []})
    monkeypatch.setattr(wt, 'gw', fake_gw)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    monkeypatch.setattr(vt, 'get_monitors', lambda: [])

    ok, msg = wt.move_window_to_monitor('missing', 2)
    assert not ok
    assert 'not found' in msg.lower()
