import importlib


def test_hide_cmd_window_non_windows():
    """Ensure hiding the console does not raise on non-Windows systems."""
    utils = importlib.import_module("modules.utils")
    utils.hide_cmd_window()
