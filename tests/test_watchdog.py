import importlib
import sys
import types


def test_watchdog_restarts_and_logs(monkeypatch):
    logs = []

    def mock_log(msg, context=None, level='ERROR'):
        logs.append(msg)

    monkeypatch.setitem(sys.modules, 'error_logger', types.ModuleType('error_logger'))
    sys.modules['error_logger'].log_error = mock_log

    wd = importlib.import_module('watchdog')
    importlib.reload(wd)

    attempts = {'n': 0}

    @wd.watchdog(delay=0)
    def flaky():
        attempts['n'] += 1
        if attempts['n'] < 2:
            raise RuntimeError('boom')
        return 'ok'

    result = flaky()

    assert result == 'ok'
    assert attempts['n'] == 2
    assert any('boom' in m for m in logs)


def test_watchdog_announces(monkeypatch):
    spoken = []

    def mock_speak(text):
        spoken.append(text)

    wd = importlib.import_module('watchdog')
    importlib.reload(wd)

    @wd.watchdog(delay=0, phrase='restart', speak_func=mock_speak)
    def fail_once():
        if not spoken:
            raise ValueError('fail')
        return 'done'

    assert fail_once() == 'done'
    assert 'restart' in spoken[0]
