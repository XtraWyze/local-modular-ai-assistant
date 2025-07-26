import importlib
import types
import sys


def test_parse_and_execute_maximize(monkeypatch):
    wt = types.ModuleType('modules.window_tools')
    calls = {}

    def mock_maximize(title):
        calls['title'] = title
        return True, f"maximized {title}"

    wt.maximize_window = mock_maximize
    wt.__all__ = ['maximize_window']
    monkeypatch.setitem(sys.modules, 'modules.window_tools', wt)

    stub_assistant = types.ModuleType('assistant')
    stub_assistant.talk_to_llm = lambda t: 'ignored'
    monkeypatch.setitem(sys.modules, 'assistant', stub_assistant)

    orch = importlib.reload(importlib.import_module('orchestrator'))

    result = orch.parse_and_execute('maximize chrome window')
    assert result == 'maximized chrome'
    assert calls['title'] == 'chrome'
