import importlib
import types
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


def test_type_in_window_not_found(monkeypatch):
    wt = importlib.import_module('modules.window_tools')
    fake_gw = type('GW', (), {"getAllTitles": lambda: []})
    monkeypatch.setattr(wt, 'gw', fake_gw)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    monkeypatch.setattr(wt, '_PYAUTOGUI_ERROR', None)
    ok, msg = wt.type_in_window('foo', 'bar')
    assert not ok
    assert 'No window found' in msg


def test_type_in_window_success(monkeypatch):
    wt = importlib.import_module('modules.window_tools')

    events = {}

    class FakeWin:
        def __init__(self, title):
            self.title = title
            self.left = 10
            self.top = 20

        def activate(self):
            events['activated'] = True

    fake_gw = type('GW', (), {
        'getAllTitles': lambda: ['Demo'],
        'getWindowsWithTitle': lambda t: [FakeWin(t)],
    })

    class FakePA:
        def click(self, x, y):
            events['click'] = (x, y)

        def write(self, text, interval=0):
            events['text'] = text

    monkeypatch.setattr(wt, 'gw', fake_gw)
    monkeypatch.setattr(wt, 'pyautogui', FakePA())
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    monkeypatch.setattr(wt, '_PYAUTOGUI_ERROR', None)
    monkeypatch.setattr(wt, 'time', types.SimpleNamespace(sleep=lambda s: None))

    ok, msg = wt.type_in_window('demo', 'hello')
    assert ok
    assert events['click'] == (110, 120)
    assert events['text'] == 'hello'
    assert 'Typed into' in msg
