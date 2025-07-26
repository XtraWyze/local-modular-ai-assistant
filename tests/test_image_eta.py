import importlib
import os
import sys
import pytest


def import_gui():
    os.environ["PYTEST_CURRENT_TEST"] = "1"
    if "gui_assistant" in sys.modules:
        del sys.modules["gui_assistant"]
    return importlib.import_module("gui_assistant")


@pytest.mark.skipif(os.environ.get("DISPLAY") is None, reason="GUI not available")
def test_eta_default(monkeypatch):
    ga = import_gui()
    assert ga.estimate_image_eta() == 10.0


@pytest.mark.skipif(os.environ.get("DISPLAY") is None, reason="GUI not available")
def test_eta_records(monkeypatch):
    ga = import_gui()
    ga._eta_history.clear()
    ga.record_image_duration(5)
    ga.record_image_duration(7)
    assert abs(ga.estimate_image_eta() - 6.0) < 0.01
