import importlib
import sys
import types
from pathlib import Path

def test_open_memory_window_runs(monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    # Stub tkinter before importing config_gui
    tk_stub = types.ModuleType('tkinter')
    mb_stub = types.ModuleType('messagebox')
    mb_stub.showinfo = lambda *a, **k: None
    class DummyWidget:
        def pack(self, *a, **k):
            pass
        def grid(self, *a, **k):
            pass
        def title(self, *a, **k):
            pass
    tk_stub.Toplevel = lambda: DummyWidget()
    tk_stub.Label = lambda *a, **k: DummyWidget()
    class DummyText(DummyWidget):
        def __init__(self, *a, **k):
            self.content = ''
        def insert(self, idx, text):
            self.content = text
        def get(self, *a):
            return self.content
    tk_stub.Text = lambda *a, **k: DummyText()
    class DummyEntry(DummyWidget):
        def __init__(self, *a, **k):
            self.var = types.SimpleNamespace(get=lambda: '1')
    tk_stub.Entry = lambda *a, **k: DummyEntry()
    tk_stub.StringVar = lambda value='': types.SimpleNamespace(get=lambda: value, set=lambda v: None)
    class DummyButton(DummyWidget):
        pass
    tk_stub.Button = lambda *a, **k: DummyButton()
    tk_stub.END = 'end'
    tk_stub.messagebox = mb_stub
    monkeypatch.setitem(sys.modules, 'tkinter', tk_stub)
    monkeypatch.setitem(sys.modules, 'tkinter.messagebox', mb_stub)

    mm_stub = types.ModuleType('memory_manager')
    mm_stub.load_memory = lambda: {'texts': [], 'vectors': []}
    mm_stub.memory = {'texts': [], 'vectors': []}
    mm_stub.MEMORY_MAX = 5
    mm_stub.get_model = lambda: types.SimpleNamespace(encode=lambda t: [[0]])
    mm_stub.save_memory = lambda mem=None: None
    mm_stub.prune_memory = lambda max_entries=5: None
    monkeypatch.setitem(sys.modules, 'memory_manager', mm_stub)

    cg = importlib.import_module('config_gui')
    importlib.reload(cg)
    win = cg.open_memory_window()
    assert win is not None
