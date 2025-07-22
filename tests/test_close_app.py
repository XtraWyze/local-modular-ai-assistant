import importlib
import types


def test_close_app_closes_window(monkeypatch):
    tools = importlib.import_module('modules.tools')

    events = {}

    class FakeWin:
        def __init__(self, title):
            self.title = title
        def activate(self):
            events['activated'] = True
        def close(self):
            events['closed'] = True

    fake_pa = types.SimpleNamespace(
        getWindowsWithTitle=lambda n: [FakeWin('Doc - Notepad')] if n == 'Notepad' else []
    )
    monkeypatch.setattr(tools, 'pyautogui', fake_pa)
    monkeypatch.setattr(tools, '_IMPORT_ERROR', None)

    out = tools.close_app('Notepad')
    assert 'Closed window' in out
    assert events.get('closed')


def test_close_app_kills_process_when_no_window(monkeypatch):
    tools = importlib.import_module('modules.tools')

    fake_pa = types.SimpleNamespace(getWindowsWithTitle=lambda n: [])
    monkeypatch.setattr(tools, 'pyautogui', fake_pa)
    monkeypatch.setattr(tools, '_IMPORT_ERROR', None)

    called = {}
    def fake_run(cmd, *a, **kw):
        called['cmd'] = cmd
    monkeypatch.setattr(tools.subprocess, 'run', fake_run)

    out = tools.close_app('dummy')
    assert 'Closed process dummy' in out
    assert 'dummy' in called['cmd']

