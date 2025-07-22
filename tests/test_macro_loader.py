import importlib
from pathlib import Path

def test_list_macros(tmp_path, monkeypatch):
    loader = importlib.import_module('modules.macro_loader')
    mdir = tmp_path / 'macros'
    mdir.mkdir()
    (mdir / 'foo.py').write_text('x=1')
    monkeypatch.setattr(loader, 'MACRO_DIR', str(mdir))
    names = loader.list_macros()
    assert names == ['foo']
