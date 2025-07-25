import importlib
import sys

import types


def test_crash_handler_announces_and_logs(monkeypatch):
    spoken = {}
    logged = []

    def mock_speak(text, **_):
        spoken['text'] = text

    def mock_log(msg, context=None, level='ERROR'):
        logged.append((msg, context, level))

    monkeypatch.setitem(sys.modules, 'error_logger', types.ModuleType('error_logger'))
    sys.modules['error_logger'].log_error = mock_log

    crash_handler = importlib.import_module('crash_handler')
    importlib.reload(crash_handler)
    crash_handler.setup_crash_handler(mock_speak, lambda: spoken.setdefault('ready', True))

    exc = RuntimeError('boom')
    sys.excepthook(type(exc), exc, exc.__traceback__)

    assert 'Crash prevented' in spoken.get('text', '')
    assert spoken.get('ready') is True
    assert any('Unhandled exception' in m for m, _, _ in logged)
