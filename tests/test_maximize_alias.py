import importlib
import types
import sys


def test_parse_and_execute_maximize(monkeypatch):
    awm = types.ModuleType('modules.app_window_manager')
    calls = {}

    def mock_maximize(title):
        calls['title'] = title
        return True, f"maximized {title}"

    awm.maximize_window = mock_maximize
    awm.__all__ = ['maximize_window']
    monkeypatch.setitem(sys.modules, 'modules.app_window_manager', awm)

    stub_assistant = types.ModuleType('assistant')
    stub_assistant.talk_to_llm = lambda t: 'ignored'
    monkeypatch.setitem(sys.modules, 'assistant', stub_assistant)

    orch = importlib.reload(importlib.import_module('orchestrator'))

    result = orch.parse_and_execute('maximize chrome window')
    assert result == 'maximized chrome'
    assert calls['title'] == 'chrome'
