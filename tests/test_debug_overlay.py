import importlib
import os
import pytest


def test_event_lists():
    do = importlib.import_module('debug_overlay')
    do.add_transcript('hi')
    do.add_ocr_text('ocr')
    do.add_command('cmd')
    do.add_memory_recall('mem')
    assert do._transcripts[-1] == 'hi'
    assert do._ocr_texts[-1] == 'ocr'
    assert do._commands[-1] == 'cmd'
    assert do._memory[-1] == 'mem'


@pytest.mark.skipif(os.environ.get('DISPLAY') is None, reason='GUI not available')
def test_overlay_toggle(monkeypatch):
    monkeypatch.setenv('PYTEST_CURRENT_TEST', '1')
    do = importlib.import_module('debug_overlay')
    overlay = do.DebugOverlay()
    overlay.toggle()
    overlay.refresh()
    text = overlay.txt_trans.get('1.0', 'end').strip()
    assert 'Transcription' in text
    overlay.toggle()
    overlay.destroy()

