import types
import importlib
import sys


def test_parse_and_execute_terminate(monkeypatch):
    stub_tools = types.ModuleType('modules.tools')
    called = {}
    def fake_close(name):
        called['name'] = name
        return f'closed {name}'
    stub_tools.close_app = fake_close
    stub_tools.__all__ = ['close_app']
    monkeypatch.setitem(sys.modules, 'modules.tools', stub_tools)

    calls = {'llm': 0}
    stub_assistant = types.ModuleType('assistant')
    def fake_llm(prompt):
        calls['llm'] += 1
        return 'ignored'
    stub_assistant.talk_to_llm = fake_llm
    monkeypatch.setitem(sys.modules, 'assistant', stub_assistant)

    orch = importlib.reload(importlib.import_module('orchestrator'))

    result = orch.parse_and_execute('terminate rocket league')
    assert result == 'closed rocket league'
    assert called['name'] == 'rocket league'
    assert calls['llm'] == 0

