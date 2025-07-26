import importlib
import json


def test_add_remove_and_last(tmp_path, monkeypatch):
    mod = importlib.import_module('modules.video_model_manager')
    importlib.reload(mod)
    models_file = tmp_path / 'vid.json'
    monkeypatch.setattr(mod, 'MODELS_FILE', str(models_file), raising=False)
    mod.model_paths = []
    mod.last_model = None
    mod.save_models([])

    mod.add_model('a')
    mod.add_model('b')
    mod.set_last_model('b')
    assert mod.model_paths == ['a', 'b']
    assert mod.get_last_model() == 'b'

    mod.remove_model('a')
    assert mod.model_paths == ['b']
    assert mod.get_last_model() == 'b'

    saved = json.loads(models_file.read_text())
    assert saved == {'models': ['b'], 'last': 'b'}


def test_load_bad_file(tmp_path, monkeypatch):
    mod = importlib.import_module('modules.video_model_manager')
    importlib.reload(mod)
    models_file = tmp_path / 'vid.json'
    models_file.write_text('{bad')
    monkeypatch.setattr(mod, 'MODELS_FILE', str(models_file), raising=False)
    mod.model_paths = ['x']
    mod.last_model = 'x'
    models = mod.load_models()
    assert models == []
    assert mod.model_paths == []
    assert mod.get_last_model() is None
