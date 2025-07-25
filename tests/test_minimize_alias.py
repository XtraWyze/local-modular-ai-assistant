import importlib
import types
import sys


def test_parse_and_execute_minimize(monkeypatch):
    wt = types.ModuleType('modules.window_tools')
    calls = {}

    def mock_minimize(title):
        calls['title'] = title
        return True, f"minimized {title}"

    wt.minimize_window = mock_minimize
    wt.__all__ = ['minimize_window']
    monkeypatch.setitem(sys.modules, 'modules.window_tools', wt)

    stub_assistant = types.ModuleType('assistant')
    stub_assistant.talk_to_llm = lambda t: 'ignored'
    monkeypatch.setitem(sys.modules, 'assistant', stub_assistant)

    orch = importlib.reload(importlib.import_module('orchestrator'))

    result = orch.parse_and_execute('minimize youtube music')
    assert result == 'minimized youtube music'
    assert calls['title'] == 'youtube music'


def test_parse_and_execute_minimize_with_window_word(monkeypatch):
    wt = types.ModuleType('modules.window_tools')
    args = {}

    def mock_minimize(title):
        args['title'] = title
        return True, f'minimized {title}'

    wt.minimize_window = mock_minimize
    wt.__all__ = ['minimize_window']
    monkeypatch.setitem(sys.modules, 'modules.window_tools', wt)

    stub_assistant = types.ModuleType('assistant')
    stub_assistant.talk_to_llm = lambda t: 'ignored'
    monkeypatch.setitem(sys.modules, 'assistant', stub_assistant)

    orch = importlib.reload(importlib.import_module('orchestrator'))

    result = orch.parse_and_execute('minimize the youtube window')
    assert result == 'minimized youtube'
    assert args['title'] == 'youtube'
