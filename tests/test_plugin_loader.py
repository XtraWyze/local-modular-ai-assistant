import importlib
from pathlib import Path

def test_load_plugins(tmp_path, monkeypatch):
    loader = importlib.import_module('modules.plugin_loader')
    # create dummy plugin package
    pkg = tmp_path / 'dummy'
    pkg.mkdir()
    (pkg / 'plugin.json').write_text('{"module": "math"}')
    monkeypatch.chdir(tmp_path)
    loaded = loader.load_plugins(str(tmp_path))
    assert 'math' in loaded
