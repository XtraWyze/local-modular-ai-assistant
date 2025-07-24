import importlib
import types
import sys


def test_parse_and_execute_save_exit(monkeypatch):
    mod = types.ModuleType('modules.save_exit')
    called = {}
    def fake_save_and_exit(title):
        called['title'] = title
        return f"closed {title}"
    mod.save_and_exit = fake_save_and_exit
    mod.__all__ = ['save_and_exit']
    monkeypatch.setitem(sys.modules, 'modules.save_exit', mod)

    stub_assistant = types.ModuleType('assistant')
    stub_assistant.talk_to_llm = lambda t: 'ignored'
    monkeypatch.setitem(sys.modules, 'assistant', stub_assistant)

    orch = importlib.reload(importlib.import_module('orchestrator'))

    result = orch.parse_and_execute('save and exit notepad')
    assert result == 'closed notepad'
    assert called['title'] == 'notepad'
