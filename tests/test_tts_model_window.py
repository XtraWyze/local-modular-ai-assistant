import importlib
import sys
import types
from pathlib import Path


def test_open_tts_model_window(monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    # stub tkinter
    tk_stub = types.ModuleType("tkinter")
    mb_stub = types.ModuleType("messagebox")
    mb_stub.showinfo = lambda *a, **k: None
    class DummyWidget:
        def pack(self, *a, **k):
            pass
        def grid(self, *a, **k):
            pass
        def title(self, *a, **k):
            pass
    class DummyOption(DummyWidget):
        pass
    tk_stub.Toplevel = lambda: DummyWidget()
    tk_stub.Label = lambda *a, **k: DummyWidget()
    tk_stub.Button = lambda *a, **k: DummyWidget()
    tk_stub.OptionMenu = lambda *a, **k: DummyOption()
    tk_stub.StringVar = lambda value="": types.SimpleNamespace(get=lambda: value, set=lambda v: None)
    tk_stub.END = "end"
    tk_stub.messagebox = mb_stub
    tk_stub.ttk = types.SimpleNamespace(OptionMenu=lambda *a, **k: DummyOption())
    monkeypatch.setitem(sys.modules, "tkinter", tk_stub)
    monkeypatch.setitem(sys.modules, "tkinter.messagebox", mb_stub)

    # stub tts_integration
    tts_stub = types.ModuleType("tts_integration")
    tts_stub.list_models = lambda: ["m1", "m2"]
    tts_stub.set_model = lambda m: None
    tts_stub.config = {"tts_model": "m1"}
    monkeypatch.setitem(sys.modules, "modules.tts_integration", tts_stub)

    cg = importlib.import_module("config_gui")
    importlib.reload(cg)
    win = cg.open_tts_model_window()
    assert win is not None
