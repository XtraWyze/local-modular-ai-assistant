import importlib
import os

import pytest


def test_event_lists():
    dp = importlib.import_module("modules.debug_panel")
    dp.add_transcript("hello")
    dp.add_ocr_result("ocr")
    dp.add_command("cmd")
    dp.add_memory_event("mem")
    assert dp.transcripts[-1] == "hello"
    assert dp.ocr_results[-1] == "ocr"
    assert dp.commands[-1] == "cmd"
    assert dp.memory_events[-1] == "mem"


@pytest.mark.skipif(os.environ.get("DISPLAY") is None, reason="GUI not available")
def test_overlay_refresh(monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "1")
    dp = importlib.import_module("modules.debug_panel")
    dp.transcripts.append("hi")
    overlay = dp.DebugOverlay()
    overlay.refresh()
    text = overlay.text.get("1.0", "end").strip()
    assert "hi" in text
    overlay.destroy()
