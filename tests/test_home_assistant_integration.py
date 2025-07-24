import importlib


def test_disabled_by_default():
    mod = importlib.import_module('modules.home_assistant_integration')
    mod.initialize({})
    assert mod.call_service('light', 'turn_on') == 'Home Assistant integration disabled'
    assert mod.get_state('light.kitchen') == 'Home Assistant integration disabled'

