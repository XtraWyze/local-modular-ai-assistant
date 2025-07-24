import types
import importlib
import sys


def test_parse_and_execute_focus(monkeypatch):
    wt = types.ModuleType('modules.window_tools')
    calls = {}

    def fake_focus(title):
        calls['title'] = title
        return True, f"focused {title}"

    wt.focus_window = fake_focus
    wt.__all__ = ['focus_window']
    monkeypatch.setitem(sys.modules, 'modules.window_tools', wt)

    stub_assistant = types.ModuleType('assistant')
    stub_assistant.talk_to_llm = lambda t: 'ignored'
    monkeypatch.setitem(sys.modules, 'assistant', stub_assistant)

    orch = importlib.reload(importlib.import_module('orchestrator'))

    result = orch.parse_and_execute('focus spotify')
    assert result == 'focused spotify'
    assert calls['title'] == 'spotify'
