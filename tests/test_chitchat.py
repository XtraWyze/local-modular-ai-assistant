import importlib
import sys
import os
import types
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def import_chitchat(monkeypatch):
    import modules  # ensure package is available
    stub_assistant = types.ModuleType('assistant')
    stub_assistant._call_local_llm = lambda p, h: 'ok'
    stub_assistant._call_cloud_llm = lambda p: 'ok'
    stub_assistant._is_bad_response = lambda r: False
    stub_assistant._is_complex_prompt = lambda p: False
    monkeypatch.setitem(sys.modules, 'assistant', stub_assistant)

    mm = types.ModuleType('memory_manager')
    mm.save_memory = lambda mem=None: None
    mm.load_memory = lambda: {}
    mm.store_memory = lambda *a, **kw: None
    mm.search_memory = lambda q: []
    mm.memory = {}
    monkeypatch.setitem(sys.modules, 'memory_manager', mm)

    sm = types.ModuleType('state_manager')
    sm.state = {"conversation_history": []}
    sm.save_state = lambda st=None: None
    sm.update_state = lambda **kw: None
    sm.register_action = lambda *a, **kw: None
    sm.get_action = lambda name: None
    sm.register_macro_command = lambda *a, **kw: ""
    sm.get_macro_action = lambda text=None: None
    sm.get_resume_phrases = lambda: []
    sm.add_resume_phrase = lambda p: None
    monkeypatch.setitem(sys.modules, 'state_manager', sm)

    lts = types.ModuleType('modules.long_term_storage')
    lts.save_entry = lambda *a, **kw: None
    monkeypatch.setitem(sys.modules, 'modules.long_term_storage', lts)

    return importlib.reload(importlib.import_module('modules.chitchat'))


def test_is_chitchat_matches(monkeypatch):
    ch = import_chitchat(monkeypatch)
    for phrase in ch.CHITCHAT_PHRASES:
        assert ch.is_chitchat(phrase)


def test_talk_to_llm_returns_text(monkeypatch):
    ch = import_chitchat(monkeypatch)
    result = ch.talk_to_llm('hello')
    assert isinstance(result, str) and result
