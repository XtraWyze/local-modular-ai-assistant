import importlib
from pathlib import Path

from module_manager import get_module_overview


def test_get_module_overview(tmp_path, monkeypatch):
    pkg = tmp_path / "mods"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "demo.py").write_text(
        "def get_info():\n    return {'name': 'demo', 'functions': ['hello']}\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    info = get_module_overview(str(pkg))
    assert info == {"demo": ["hello"]}
    import sys
    sys.modules.pop("mods", None)
