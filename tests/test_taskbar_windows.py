import importlib
import types


def test_list_taskbar_windows(monkeypatch):
    wt = importlib.import_module('modules.window_tools')

    mock_gw1 = types.SimpleNamespace(getAllTitles=lambda: ['One', '', 'Two'])
    monkeypatch.setattr(wt, 'gw', mock_gw1)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)

    assert wt.list_taskbar_windows() == ['One', 'Two']


def test_close_taskbar_item(monkeypatch):
    wt = importlib.import_module('modules.window_tools')

    events = {}

    class MockWin:
        def __init__(self, title):
            self.title = title
        def activate(self):
            events['activated'] = True
        def close(self):
            events['closed'] = True

    mock_gw = types.SimpleNamespace(getAllWindows=lambda: [MockWin('One')])
    monkeypatch.setattr(wt, 'gw', mock_gw)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)

    success, msg = wt.close_taskbar_item(0)
    assert success
    assert events.get('closed')
    assert 'One' in msg


def test_close_taskbar_item_invalid_index(monkeypatch):
    wt = importlib.import_module('modules.window_tools')

    mock_gw2 = types.SimpleNamespace(getAllWindows=lambda: [])
    monkeypatch.setattr(wt, 'gw', mock_gw2)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)

    success, msg = wt.close_taskbar_item(5)
    assert not success
    assert 'Invalid window index' in msg
