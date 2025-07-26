import importlib


def test_show_cmd_window_non_windows():
    """Ensure showing the console does not raise on non-Windows systems."""
    utils = importlib.import_module("modules.utils")
    utils.show_cmd_window()
