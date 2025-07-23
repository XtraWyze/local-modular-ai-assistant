import importlib
import importlib.util
import sys
import types
from pathlib import Path


def test_store_memory_keeps_arrays(monkeypatch):
    # Stub numpy with minimal ndarray type
    class DummyNDArray(list):
        pass
    np_stub = types.ModuleType("numpy")
    np_stub.ndarray = DummyNDArray
    np_stub.array = lambda x: DummyNDArray(x)

    # Stub SentenceTransformer before importing memory_manager
    class DummyModel:
        def encode(self, texts):
            return [np_stub.array([1.0, 2.0, 3.0])] * len(texts)

    st_stub = types.ModuleType("sentence_transformers")
    st_stub.SentenceTransformer = lambda *args, **kwargs: DummyModel()

    monkeypatch.setitem(sys.modules, "numpy", np_stub)
    monkeypatch.setitem(sys.modules, "sentence_transformers", st_stub)

    mm = importlib.import_module("memory_manager")
    importlib.reload(mm)

    monkeypatch.setattr(mm, "save_memory", lambda mem=mm.memory: None)
    monkeypatch.setattr(mm, "get_model", lambda: DummyModel())
    mm._model = None
    mm.memory = {"texts": [], "vectors": []}

    mm.store_memory("hello world")

    assert len(mm.memory["vectors"]) == 1
    assert isinstance(mm.memory["vectors"][0], mm.np.ndarray)


def test_memory_prunes_to_limit(monkeypatch):
    class DummyNDArray(list):
        pass
    np_stub = types.ModuleType("numpy")
    np_stub.ndarray = DummyNDArray
    np_stub.array = lambda x: DummyNDArray(x)

    class DummyModel:
        def encode(self, texts):
            return [np_stub.array([1.0, 2.0, 3.0])] * len(texts)

    st_stub = types.ModuleType("sentence_transformers")
    st_stub.SentenceTransformer = lambda *args, **kwargs: DummyModel()

    monkeypatch.setitem(sys.modules, "numpy", np_stub)
    monkeypatch.setitem(sys.modules, "sentence_transformers", st_stub)

    mm = importlib.import_module("memory_manager")
    importlib.reload(mm)

    monkeypatch.setattr(mm, "save_memory", lambda mem=mm.memory: None)
    monkeypatch.setattr(mm, "get_model", lambda: DummyModel())
    mm._model = None
    mm.memory = {"texts": [], "vectors": []}
    mm.MEMORY_MAX = 2
    mm.AUTO_MEMORY_INCREASE = False

    mm.store_memory("a")
    mm.store_memory("b")
    mm.store_memory("c")

    assert len(mm.memory["texts"]) == 2
    assert mm.memory["texts"] == ["b", "c"]


def test_load_memory_handles_corruption(tmp_path, monkeypatch):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not json}")

    monkeypatch.setattr("memory_manager.MEMORY_FILE", str(bad_file))
    monkeypatch.setattr("memory_manager.log_error", lambda *a, **k: None)
    mm = importlib.import_module("memory_manager")
    importlib.reload(mm)

    assert mm.memory == {"texts": [], "vectors": []}


def test_auto_memory_increase(monkeypatch):
    class DummyNDArray(list):
        pass

    np_stub = types.ModuleType("numpy")
    np_stub.ndarray = DummyNDArray
    np_stub.array = lambda x: DummyNDArray(x)

    class DummyModel:
        def encode(self, texts):
            return [np_stub.array([1.0, 2.0, 3.0])] * len(texts)

    st_stub = types.ModuleType("sentence_transformers")
    st_stub.SentenceTransformer = lambda *args, **kwargs: DummyModel()

    monkeypatch.setitem(sys.modules, "numpy", np_stub)
    monkeypatch.setitem(sys.modules, "sentence_transformers", st_stub)

    import os
    import sys as _sys
    _sys.path.insert(0, os.getcwd())
    mm = importlib.import_module("memory_manager")
    importlib.reload(mm)

    monkeypatch.setattr(mm, "save_memory", lambda mem=mm.memory: None)
    monkeypatch.setattr(mm, "get_model", lambda: DummyModel())
    mm._model = None
    mm.memory = {"texts": [], "vectors": []}
    mm.MEMORY_MAX = 2
    mm.AUTO_MEMORY_INCREASE = True

    mm.store_memory("a")
    mm.store_memory("b")
    mm.store_memory("c")

    assert mm.MEMORY_MAX > 2
    assert len(mm.memory["texts"]) == 3


def test_import_outside_project(monkeypatch, tmp_path):
    """Ensure ``memory_manager`` imports even when the project root isn't on ``sys.path``."""
    project_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(project_root)
    new_path = [p for p in sys.path if p not in ("", str(project_root))]
    monkeypatch.setattr(sys, "path", new_path, raising=False)
    sys.modules.pop("modules", None)
    sys.modules.pop("modules.utils", None)

    spec = importlib.util.spec_from_file_location(
        "memory_manager", project_root / "memory_manager.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    assert "modules.utils" in sys.modules
    assert str(project_root) in sys.path
