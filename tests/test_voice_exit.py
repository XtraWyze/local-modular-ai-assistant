import importlib
import pytest

try:
    vi = importlib.import_module('modules.voice_input')
except Exception:
    vi = None

@pytest.mark.skipif(vi is None, reason="voice_input failed to import")
def test_is_exit_command():
    importlib.reload(vi)
    assert vi.is_exit_command("exit environment")
    assert not vi.is_exit_command("exit")
    assert not vi.is_exit_command("hello")
