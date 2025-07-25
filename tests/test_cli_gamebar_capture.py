import importlib
import sys
import types

sys.modules.setdefault('keyboard', types.ModuleType('keyboard'))
sys.modules.setdefault('pyautogui', types.ModuleType('pyautogui'))

from cli_assistant import process_command


def test_cli_start_recording(monkeypatch):
    gb = importlib.import_module('modules.gamebar_capture')
    calls = []
    monkeypatch.setattr(gb, 'toggle_recording', lambda: calls.append('rec') or 'ok')
    out = process_command('start recording')
    assert calls == ['rec']
    assert out == 'ok'


def test_cli_open_game_bar(monkeypatch):
    gb = importlib.import_module('modules.gamebar_capture')
    calls = []
    monkeypatch.setattr(gb, 'open_capture', lambda: calls.append('open') or 'ok')
    out = process_command('open game bar')
    assert calls == ['open']
    assert out == 'ok'


def test_cli_take_screenshot(monkeypatch):
    gb = importlib.import_module('modules.gamebar_capture')
    calls = []
    monkeypatch.setattr(gb, 'capture_screenshot', lambda: calls.append('shot') or 'ok')
    out = process_command('take screenshot')
    assert calls == ['shot']
    assert out == 'ok'


def test_cli_last_30s(monkeypatch):
    gb = importlib.import_module('modules.gamebar_capture')
    calls = []
    monkeypatch.setattr(gb, 'capture_last_30s', lambda: calls.append('30s') or 'ok')
    out = process_command('record last 30 seconds')
    assert calls == ['30s']
    assert out == 'ok'
