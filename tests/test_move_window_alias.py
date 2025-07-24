import types
import importlib
import sys

def test_parse_and_execute_move_window(monkeypatch):
    wt = types.ModuleType('modules.window_tools')
    calls = {}
    def fake_move(title, idx):
        calls['title'] = title
        calls['idx'] = idx
        return True, 'done'
    wt.move_window_to_monitor = fake_move
    wt.__all__ = ['move_window_to_monitor']
    monkeypatch.setitem(sys.modules, 'modules.window_tools', wt)

    stub_assistant = types.ModuleType('assistant')
    stub_assistant.talk_to_llm = lambda text: 'ignored'
    monkeypatch.setitem(sys.modules, 'assistant', stub_assistant)

    orch = importlib.reload(importlib.import_module('orchestrator'))

    result = orch.parse_and_execute('move spotify to monitor 1')
    assert result == 'done'
    assert calls == {'title': 'spotify', 'idx': 1}
