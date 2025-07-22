import importlib
import sys
import types


def import_assistant(monkeypatch, state):
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

    sm = types.ModuleType('state_manager')
    sm.state = state
    sm.actions = {}
    sm.save_state = lambda st=None: None
    sm.load_state = lambda: state
    sm.update_state = lambda **kw: None
    sm.register_action = lambda name, path: None
    sm.get_action = lambda name: None
    sm.add_resume_phrase = lambda p: None
    sm.get_resume_phrases = lambda: []
    sm.load_actions = lambda: {}
    sm.save_actions = lambda act=None: None
    monkeypatch.setitem(sys.modules, 'state_manager', sm)

    assistant = importlib.import_module('assistant')
    importlib.reload(assistant)
    return assistant


def test_conversation_persists(monkeypatch):
    state = {"history": [], "conversation_history": []}
    assistant = import_assistant(monkeypatch, state)
    assistant.talk_to_llm('hello')
    assert len(state['conversation_history']) == 2
    assistant = importlib.reload(assistant)
    assert assistant.conversation_history == state['conversation_history']

