import importlib
import json


def test_add_remove_and_last(tmp_path, monkeypatch):
    mod = importlib.import_module('modules.llm_model_manager')
    importlib.reload(mod)
    models_file = tmp_path / 'llm.json'
    monkeypatch.setattr(mod, 'MODELS_FILE', str(models_file), raising=False)
    mod.model_paths = []
    mod.last_model = None
    mod.save_models([])

    mod.add_model('m1')
    mod.add_model('m2')
    mod.set_last_model('m2')
    assert mod.model_paths == ['m1', 'm2']
    assert mod.get_last_model() == 'm2'

    removed = mod.remove_model('m1')
    assert removed is True
    assert mod.model_paths == ['m2']
    assert mod.get_last_model() == 'm2'

    saved = json.loads(models_file.read_text())
    assert saved == {'models': ['m2'], 'last': 'm2'}


def test_load_bad_file(tmp_path, monkeypatch):
    mod = importlib.import_module('modules.llm_model_manager')
    importlib.reload(mod)
    models_file = tmp_path / 'llm.json'
    models_file.write_text('{bad')
    monkeypatch.setattr(mod, 'MODELS_FILE', str(models_file), raising=False)
    mod.model_paths = ['x']
    mod.last_model = 'x'
    models = mod.load_models()
    assert models == []
    assert mod.model_paths == []
    assert mod.get_last_model() is None
