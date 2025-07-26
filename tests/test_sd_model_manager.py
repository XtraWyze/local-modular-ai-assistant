import importlib
import json


def test_add_and_remove_models(tmp_path, monkeypatch):
    mod = importlib.import_module('modules.sd_model_manager')
    importlib.reload(mod)
    models_file = tmp_path / 'models.json'
    monkeypatch.setattr(mod, 'MODELS_FILE', str(models_file), raising=False)
    mod.model_paths = []
    mod.save_models([])

    mod.add_model('one')
    mod.add_model('two')
    assert mod.model_paths == ['one', 'two']

    removed = mod.remove_model('one')
    assert removed is True
    assert mod.model_paths == ['two']
    saved = json.loads(models_file.read_text())
    assert saved == ['two']


def test_load_models_corruption(tmp_path, monkeypatch):
    mod = importlib.import_module('modules.sd_model_manager')
    importlib.reload(mod)
    models_file = tmp_path / 'models.json'
    models_file.write_text('{bad')
    monkeypatch.setattr(mod, 'MODELS_FILE', str(models_file), raising=False)
    mod.model_paths = ['x']
    models = mod.load_models()
    assert models == []
    assert mod.model_paths == []
