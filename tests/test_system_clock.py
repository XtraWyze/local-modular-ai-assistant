import importlib


def test_get_system_time_returns_string():
    clock = importlib.import_module('modules.system_clock')
    result = clock.get_system_time()
    assert isinstance(result, str) and len(result) > 0
