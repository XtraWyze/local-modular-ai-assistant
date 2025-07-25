import importlib
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import types

def import_assistant(monkeypatch):
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
    assistant = importlib.import_module('assistant')
    importlib.reload(assistant)
    return assistant


def test_split_llm_response_examples(monkeypatch):
    assistant = import_assistant(monkeypatch)
    text, code = assistant.split_llm_response("I'm just an AI, but here's a fun fact...")
    assert text == "I'm just an AI, but here's a fun fact..."
    assert code is None

    text, code = assistant.split_llm_response("run_python('print(2+2)')")
    assert text == ""
    assert code == "run_python('print(2+2)')"

    t, c = assistant.split_llm_response('Sure! run_python("print(\\"hello\\")")')
    assert t == "Sure!"
    assert c == 'run_python("print(\\"hello\\")")'


def test_user_wants_code_detection(monkeypatch):
    assistant = import_assistant(monkeypatch)
    assert not assistant.user_wants_code("What's the weather?")
    assert assistant.user_wants_code("Calculate the sum of 5 and 8.")
    assert assistant.user_wants_code("close notepad")
    assert assistant.user_wants_code("Move the mouse to 100 200")
    assert assistant.user_wants_code("terminate notepad")

