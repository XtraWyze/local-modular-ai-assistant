import importlib


def test_speak_missing_dependencies():
    tts = importlib.reload(importlib.import_module('modules.tts_integration'))
    result = tts.speak('hi', async_play=False)
    assert 'Missing dependency' in result
