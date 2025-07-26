import importlib
import types
import sys


def test_open_alias(monkeypatch):
    awm = types.ModuleType('modules.app_window_manager')
    called = {}

    def mock_open(app):
        called['app'] = app
        return True, f"opened {app}"

    awm.open_application = mock_open
    awm.__all__ = ['open_application']
    monkeypatch.setitem(sys.modules, 'modules.app_window_manager', awm)

    stub_assistant = types.ModuleType('assistant')
    stub_assistant.talk_to_llm = lambda t: 'ignored'
    monkeypatch.setitem(sys.modules, 'assistant', stub_assistant)

    orch = importlib.reload(importlib.import_module('orchestrator'))

    result = orch.parse_and_execute('open notepad')
    assert result == 'opened notepad'
    assert called['app'] == 'notepad'


def test_close_alias(monkeypatch):
    awm = types.ModuleType('modules.app_window_manager')
    called = {}

    def mock_close(title):
        called['title'] = title
        return True, f"closed {title}"

    awm.close_window = mock_close
    awm.__all__ = ['close_window']
    monkeypatch.setitem(sys.modules, 'modules.app_window_manager', awm)

    stub_assistant = types.ModuleType('assistant')
    stub_assistant.talk_to_llm = lambda t: 'ignored'
    monkeypatch.setitem(sys.modules, 'assistant', stub_assistant)

    orch = importlib.reload(importlib.import_module('orchestrator'))

    result = orch.parse_and_execute('close chrome window')
    assert result == 'closed chrome'
    assert called['title'] == 'chrome'


def test_resize_alias(monkeypatch):
    import modules.app_window_manager as awm
    import modules.automation_actions as aa
    args = {}

    def mock_resize(title, w, h):
        args['title'] = title
        args['w'] = w
        args['h'] = h
        return f"resized {title} to {w}x{h}"

    monkeypatch.setattr(awm, 'resize_window', mock_resize)
    monkeypatch.setattr(aa, 'resize_window', mock_resize)
    awm.__all__ = ['resize_window']
    aa.__all__ = ['resize_window']
    monkeypatch.setitem(sys.modules, 'modules.app_window_manager', awm)
    monkeypatch.setitem(sys.modules, 'modules.automation_actions', aa)

    stub_assistant = types.ModuleType('assistant')
    stub_assistant.talk_to_llm = lambda t: 'ignored'
    monkeypatch.setitem(sys.modules, 'assistant', stub_assistant)

    orch = importlib.reload(importlib.import_module('orchestrator'))
    orch.TOOLS.resize_window = mock_resize
    orch._rebuild_allowed()

    result = orch.parse_and_execute('resize notepad to 800 600')
    assert result == 'resized notepad to 800x600'
    assert args['title'] == 'notepad'
    assert args['w'] == 800
    assert args['h'] == 600
