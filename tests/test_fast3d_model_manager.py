import importlib
import json


def test_add_remove_and_last(tmp_path, monkeypatch):
    mod = importlib.import_module('modules.fast3d_model_manager')
    importlib.reload(mod)
    models_file = tmp_path / 'f3d.json'
    monkeypatch.setattr(mod, 'MODELS_FILE', str(models_file), raising=False)
    mod.model_paths = []
    mod.last_model = None
    mod.save_models([])

    mod.add_model('x')
    mod.add_model('y')
    mod.set_last_model('y')
    assert mod.model_paths == ['x', 'y']
    assert mod.get_last_model() == 'y'

    mod.remove_model('x')
    assert mod.model_paths == ['y']
    assert mod.get_last_model() == 'y'

    saved = json.loads(models_file.read_text())
    assert saved == {'models': ['y'], 'last': 'y'}


def test_load_bad(tmp_path, monkeypatch):
    mod = importlib.import_module('modules.fast3d_model_manager')
    importlib.reload(mod)
    models_file = tmp_path / 'f3d.json'
    models_file.write_text('{bad')
    monkeypatch.setattr(mod, 'MODELS_FILE', str(models_file), raising=False)
    mod.model_paths = ['z']
    mod.last_model = 'z'
    models = mod.load_models()
    assert models == []
    assert mod.model_paths == []
    assert mod.get_last_model() is None
