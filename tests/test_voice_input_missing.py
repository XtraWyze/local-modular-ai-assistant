import importlib


def test_listen_missing_dependencies():
    vi = importlib.reload(importlib.import_module('modules.voice_input'))
    result = vi.listen(None, 'model', lambda: False)
    assert 'Missing dependency' in result
