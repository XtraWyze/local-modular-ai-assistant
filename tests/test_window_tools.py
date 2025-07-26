import importlib
import types
from modules.window_tools import close_taskbar_item, minimize_window, focus_window

def test_invalid_index():
    ok, msg = close_taskbar_item(-1)
    assert not ok
    assert "Invalid window index" in msg


def test_minimize_window_not_found(monkeypatch):
    wt = importlib.import_module('modules.window_tools')
    mock_gw1 = type('GW', (), {
        'getAllTitles': lambda: [],
    })
    monkeypatch.setattr(wt, 'gw', mock_gw1)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    ok, msg = minimize_window('xyz')
    assert not ok
    assert 'No window found' in msg


def test_minimize_window_success(monkeypatch):
    wt = importlib.import_module('modules.window_tools')
    events = {}

    class MockWin:
        def __init__(self, title):
            self.title = title
        def minimize(self):
            events['min'] = True

    mock_gw2 = type('GW', (), {
        'getAllTitles': lambda: ['My App'],
        'getWindowsWithTitle': lambda t: [MockWin(t)],
    })
    monkeypatch.setattr(wt, 'gw', mock_gw2)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    ok, msg = minimize_window('my app')
    assert ok
    assert events.get('min')
    assert 'My App' in msg


def test_move_window_to_monitor(monkeypatch):
    wt = importlib.import_module('modules.window_tools')
    vt = importlib.import_module('modules.vision_tools')

    class MockWin:
        def __init__(self, title):
            self.title = title
        def moveTo(self, x, y):
            self.moved = (x, y)

    mock_gw3 = type('GW', (), {
        'getWindowsWithTitle': lambda t: [MockWin(t)]
    })
    monkeypatch.setattr(wt, 'gw', mock_gw3)
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

    mock_gw4 = type('GW', (), {'getWindowsWithTitle': lambda t: []})
    monkeypatch.setattr(wt, 'gw', mock_gw4)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    monkeypatch.setattr(vt, 'get_monitors', lambda: [])

    ok, msg = wt.move_window_to_monitor('missing', 2)
    assert not ok
    assert 'not found' in msg.lower()


def test_type_in_window(monkeypatch):
    wt = importlib.import_module('modules.window_tools')

    class MockWin:
        def __init__(self, title):
            self.title = title
        def activate(self):
            pass

    mock_gw5 = types.SimpleNamespace(
        getAllTitles=lambda: ['Notepad'],
        getWindowsWithTitle=lambda t: [MockWin(t)]
    )
    typed = []
    mock_pg = types.SimpleNamespace(write=lambda text, interval=0.05: typed.append(text))
    monkeypatch.setattr(wt, 'gw', mock_gw5)
    monkeypatch.setattr(wt, 'pyautogui', mock_pg)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    monkeypatch.setattr(wt, '_PYAUTOGUI_ERROR', None)

    ok, msg = wt.type_in_window('notepad', 'hello')
    assert ok
    assert typed == ['hello']
    assert 'notepad' in msg.lower()


def test_focus_window_not_found(monkeypatch):
    wt = importlib.import_module('modules.window_tools')
    mock_gw6 = types.SimpleNamespace(getAllTitles=lambda: [])
    monkeypatch.setattr(wt, 'gw', mock_gw6)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)

    ok, msg = wt.focus_window('missing')
    assert not ok
    assert 'no window found' in msg.lower()


def test_focus_window_success(monkeypatch):
    wt = importlib.import_module('modules.window_tools')

    class MockWin:
        def __init__(self, title):
            self.title = title
            self.activated = False

        def activate(self):
            self.activated = True

    mock_win = MockWin('Test App')
    mock_gw7 = types.SimpleNamespace(
        getAllTitles=lambda: ['Test App'],
        getWindowsWithTitle=lambda t: [mock_win]
    )
    monkeypatch.setattr(wt, 'gw', mock_gw7)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)

    ok, msg = wt.focus_window('test app')
    assert ok
    assert mock_win.activated
    assert 'activated' in msg.lower()


def test_focus_window_alt_tab(monkeypatch):
    wt = importlib.import_module('modules.window_tools')

    class MockGW:
        def __init__(self):
            self.calls = 0
        def getAllTitles(self):
            return []
        def getActiveWindow(self):
            self.calls += 1
            if self.calls > 1:
                return types.SimpleNamespace(title='Music App')
            return types.SimpleNamespace(title='Other')

    actions = []
    monkeypatch.setattr(wt, 'gw', MockGW())
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    monkeypatch.setattr(wt, '_PYAUTOGUI_ERROR', None)
    monkeypatch.setattr(wt, 'pyautogui', types.SimpleNamespace(hotkey=lambda *k: actions.append(k)))
    monkeypatch.setattr(wt.time, 'sleep', lambda t: None)

    ok, msg = wt.focus_window('music')
    assert ok
    assert ('alt', 'tab') in actions
    assert 'music' in msg.lower()


def test_maximize_window_not_found(monkeypatch):
    wt = importlib.import_module('modules.window_tools')
    mock_gw = types.SimpleNamespace(getAllTitles=lambda: [], getActiveWindow=lambda: None)
    monkeypatch.setattr(wt, 'gw', mock_gw)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    monkeypatch.setattr(wt, '_PYAUTOGUI_ERROR', None)
    monkeypatch.setattr(wt, 'pyautogui', types.SimpleNamespace(hotkey=lambda *a: None, press=lambda *a: None))

    ok, msg = wt.maximize_window('nothing')
    assert not ok
    assert 'no window found' in msg.lower()


def test_maximize_window_success(monkeypatch):
    wt = importlib.import_module('modules.window_tools')

    class MockWin:
        def __init__(self, title):
            self.title = title
            self.maxed = False
        def activate(self):
            pass
        def maximize(self):
            self.maxed = True

    mock_win = MockWin('Chrome')
    mock_gw = types.SimpleNamespace(
        getAllTitles=lambda: ['Chrome'],
        getWindowsWithTitle=lambda t: [mock_win],
        getActiveWindow=lambda: mock_win,
    )
    monkeypatch.setattr(wt, 'gw', mock_gw)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)
    monkeypatch.setattr(wt, '_PYAUTOGUI_ERROR', None)
    monkeypatch.setattr(wt, 'pyautogui', types.SimpleNamespace(hotkey=lambda *a: None, press=lambda *a: None))

    ok, msg = wt.maximize_window('chrome')
    assert ok
    assert mock_win.maxed
    assert 'chrome' in msg.lower()
