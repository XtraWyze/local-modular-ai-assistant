import importlib
import sys
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


def test_get_usage_tutorial(monkeypatch):
    assistant = import_assistant(monkeypatch)
    tutorial = assistant.get_usage_tutorial()
    assert isinstance(tutorial, str)
    assert len(tutorial) > 0
