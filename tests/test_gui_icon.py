import importlib
import os
import sys
import pytest

try:
    import PIL
except Exception:
    PIL = None


@pytest.mark.skipif(PIL is None or not os.environ.get("DISPLAY"), reason="GUI not available")
def test_make_icon_image(monkeypatch):
    """Ensure icon generation works without a display."""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "1")
    if "gui_assistant" in sys.modules:
        del sys.modules["gui_assistant"]
    gui_assistant = importlib.import_module("gui_assistant")
    img = gui_assistant.make_icon_image()
    assert img.size == (64, 64)
