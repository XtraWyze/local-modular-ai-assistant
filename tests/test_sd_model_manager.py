import importlib
import json


def test_add_remove_and_last(tmp_path, monkeypatch):
    mod = importlib.import_module('modules.sd_model_manager')
    importlib.reload(mod)
    models_file = tmp_path / 'models.json'
    monkeypatch.setattr(mod, 'MODELS_FILE', str(models_file), raising=False)
    mod.model_paths = []
    mod.last_model = None
    mod.save_models([])

    mod.add_model('one')
    mod.add_model('two')
    mod.set_last_model('two')
    assert mod.model_paths == ['one', 'two']
    assert mod.get_last_model() == 'two'

    removed = mod.remove_model('one')
    assert removed is True
    assert mod.model_paths == ['two']
    assert mod.get_last_model() == 'two'

    saved = json.loads(models_file.read_text())
    assert saved == {'models': ['two'], 'last': 'two'}


def test_load_models_corruption(tmp_path, monkeypatch):
    mod = importlib.import_module('modules.sd_model_manager')
    importlib.reload(mod)
    models_file = tmp_path / 'models.json'
    models_file.write_text('{bad')
    monkeypatch.setattr(mod, 'MODELS_FILE', str(models_file), raising=False)
    mod.model_paths = ['x']
    mod.last_model = 'x'
    models = mod.load_models()
    assert models == []
    assert mod.model_paths == []
    assert mod.get_last_model() is None
