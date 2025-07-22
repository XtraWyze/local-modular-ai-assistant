import importlib


def test_run_python_returns_stdout():
    tools = importlib.reload(importlib.import_module('modules.tools'))
    assert tools.run_python('print(5)') == '5'
