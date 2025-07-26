import importlib
import types


def test_get_open_windows(monkeypatch):
    mod = importlib.import_module('modules.app_window_manager')
    win_obj = types.SimpleNamespace(title='Demo', _hWnd=1)
    mock_gw = types.SimpleNamespace(getAllWindows=lambda: [win_obj], getAllTitles=lambda: ['Demo'])
    monkeypatch.setattr(mod, 'gw', mock_gw)
    monkeypatch.setattr(mod, '_GW_ERROR', None)
    monkeypatch.setattr(mod.os, 'name', 'nt', raising=False)
    monkeypatch.setattr(
        mod,
        'win32process',
        types.SimpleNamespace(GetWindowThreadProcessId=lambda h: (1, 123)),
    )
    proc_mod = types.SimpleNamespace(
        Process=lambda pid: types.SimpleNamespace(name=lambda: 'demo.exe')
    )
    monkeypatch.setattr(mod, 'psutil', proc_mod)

    windows = mod.get_open_windows()
    assert windows == [{'title': 'Demo', 'process': 'demo.exe'}]


def test_close_window(monkeypatch):
    mod = importlib.import_module('modules.app_window_manager')

    class Win:
        def __init__(self):
            self.closed = False
            self.title = 'Test App'
        def activate(self):
            pass
        def close(self):
            self.closed = True

    w = Win()
    mock_gw = types.SimpleNamespace(
        getAllTitles=lambda: ['Test App'],
        getWindowsWithTitle=lambda t: [w],
        getAllWindows=lambda: []
    )
    monkeypatch.setattr(mod, 'gw', mock_gw)
    monkeypatch.setattr(mod, '_GW_ERROR', None)
    monkeypatch.setattr(mod, 'pyautogui', types.SimpleNamespace(hotkey=lambda *a: None))

    ok, msg = mod.close_window('test app')
    assert ok
    assert w.closed
    assert 'closed' in msg.lower()


def test_handle_app_logic(monkeypatch):
    mod = importlib.import_module('modules.app_window_manager')
    stub = lambda title: (True, f'focused {title}')
    monkeypatch.setattr(mod, 'focus_window', stub)
    mod._FUNCTION_MAP['focus_window'] = stub
    mod.APP_WORKFLOWS = {'demo': [{'action': 'focus_window', 'args': ['demo']}]}

    result = mod.handle_app_logic('demo')
    assert 'focused demo' in result
