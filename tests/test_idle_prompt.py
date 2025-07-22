import importlib
import sys
import types
import time
import builtins
from pathlib import Path


def import_assistant_with_tts(monkeypatch, flag, calls, logs):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    li = types.ModuleType('llm_interface')
    li.generate_response = lambda *a, **kw: 'ok'
    monkeypatch.setitem(sys.modules, 'llm_interface', li)
    monkeypatch.setitem(sys.modules, 'keyboard', types.ModuleType('keyboard'))
    monkeypatch.setitem(sys.modules, 'pyautogui', types.ModuleType('pyautogui'))

    mm = types.ModuleType('memory_manager')
    mm.save_memory = lambda mem=None: None
    mm.load_memory = lambda: {}
    mm.store_memory = lambda *a, **kw: None
    mm.search_memory = lambda q: []
    mm.memory = {}
    monkeypatch.setitem(sys.modules, 'memory_manager', mm)

    cfgval = types.ModuleType('config_validator')
    cfgval.validate_config = lambda cfg: []
    monkeypatch.setitem(sys.modules, 'config_validator', cfgval)

    tts = types.ModuleType('modules.tts_integration')
    tts.speak = lambda text, **kw: calls.append(text)
    tts.is_speaking = lambda: flag['speaking']
    monkeypatch.setitem(sys.modules, 'modules.tts_integration', tts)

    monkeypatch.setitem(sys.modules, 'modules.window_tools', types.ModuleType('modules.window_tools'))
    monkeypatch.setitem(sys.modules, 'modules.vision_tools', types.ModuleType('modules.vision_tools'))

    assistant = importlib.import_module('assistant')
    importlib.reload(assistant)

    monkeypatch.setattr(builtins, 'print', lambda *a, **kw: logs.append(' '.join(map(str, a))))

    return assistant


def test_idle_prompt_waits_for_tts(monkeypatch):
    flag = {'speaking': True}
    calls = []
    logs = []
    assistant = import_assistant_with_tts(monkeypatch, flag, calls, logs)

    assistant._run_next_in_queue()
    assert calls == []

    flag['speaking'] = False
    time.sleep(0.15)

    assert calls == []
    assert any('Waited' in log for log in logs)
