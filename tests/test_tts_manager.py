import importlib
import types
import sys

def test_manager_gtts(monkeypatch):
    mgr = importlib.import_module('modules.tts_manager')
    gtts = types.SimpleNamespace(speak=lambda text, **kw: 'gtts')
    coqui = types.SimpleNamespace(speak=lambda text, **kw: 'coqui', is_speaking=lambda: False, stop_speech=lambda: None)
    monkeypatch.setitem(sys.modules, 'modules.gtts_tts', gtts)
    monkeypatch.setitem(sys.modules, 'modules.tts_integration', coqui)
    monkeypatch.setattr(mgr, 'BACKEND', 'gtts')
    assert mgr.speak('hi') == 'gtts'
