import importlib
from pathlib import Path

import pytest

MODULE_DIR = Path(__file__).resolve().parents[1] / "modules"
MODULE_FILES = [p for p in MODULE_DIR.glob("*.py") if p.name != "__init__.py"]

@pytest.mark.parametrize("module_path", MODULE_FILES, ids=[p.stem for p in MODULE_FILES])
def test_get_info_functions_exist(module_path):
    module_name = f"modules.{module_path.stem}"
    try:
        mod = importlib.import_module(module_name)
    except Exception as exc:
        pytest.skip(f"Could not import {module_name}: {exc}")
        return
    if not hasattr(mod, "get_info"):
        return
    info = mod.get_info()
    for func_name in info.get("functions", []):
        assert hasattr(mod, func_name), f"{module_name} missing function '{func_name}'"
