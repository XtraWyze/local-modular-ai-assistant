import importlib
import pytest

try:
    import PIL
except Exception:
    PIL = None


@pytest.mark.skipif(PIL is None, reason="Pillow not available")
def test_make_icon_image():
    gui_assistant = importlib.import_module('gui_assistant')
    img = gui_assistant.make_icon_image()
    assert img.size == (64, 64)
