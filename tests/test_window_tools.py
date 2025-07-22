import importlib
from modules.window_tools import close_taskbar_item

def test_invalid_index():
    ok, msg = close_taskbar_item(-1)
    assert not ok
    assert "Invalid window index" in msg
