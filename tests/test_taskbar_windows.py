import importlib
import types


def test_list_taskbar_windows(monkeypatch):
    wt = importlib.import_module('modules.window_tools')

    fake_gw = types.SimpleNamespace(getAllTitles=lambda: ['One', '', 'Two'])
    monkeypatch.setattr(wt, 'gw', fake_gw)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)

    assert wt.list_taskbar_windows() == ['One', 'Two']


def test_close_taskbar_item(monkeypatch):
    wt = importlib.import_module('modules.window_tools')

    events = {}

    class FakeWin:
        def __init__(self, title):
            self.title = title
        def activate(self):
            events['activated'] = True
        def close(self):
            events['closed'] = True

    fake_gw = types.SimpleNamespace(getAllWindows=lambda: [FakeWin('One')])
    monkeypatch.setattr(wt, 'gw', fake_gw)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)

    success, msg = wt.close_taskbar_item(0)
    assert success
    assert events.get('closed')
    assert 'One' in msg


def test_close_taskbar_item_invalid_index(monkeypatch):
    wt = importlib.import_module('modules.window_tools')

    fake_gw = types.SimpleNamespace(getAllWindows=lambda: [])
    monkeypatch.setattr(wt, 'gw', fake_gw)
    monkeypatch.setattr(wt, '_IMPORT_ERROR', None)

    success, msg = wt.close_taskbar_item(5)
    assert not success
    assert 'Invalid window index' in msg
