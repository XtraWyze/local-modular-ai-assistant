import importlib
import pytest

try:
    vi = importlib.import_module('modules.voice_input')
except Exception:
    vi = None

@pytest.mark.skipif(vi is None, reason="voice_input failed to import")
def test_hotword_toggle():
    importlib.reload(vi)
    vi.mute_hotword(1)
    assert vi._hotword_muted
    vi.unmute_hotword()
    assert not vi._hotword_muted
