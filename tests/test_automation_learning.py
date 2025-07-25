import importlib
import types
import json
from pathlib import Path


def test_record_and_play_macro(tmp_path, monkeypatch):
    # Stub pyautogui functions
    mod = importlib.import_module('modules.automation_learning')
    events = [{'x': 1}]
    mock_pa = types.SimpleNamespace(record=lambda: events, play=lambda e: None)
    monkeypatch.setattr(mod, 'pyautogui', mock_pa)
    monkeypatch.setattr(mod, '_IMPORT_ERROR', None)

    macro_dir = tmp_path / 'macros'
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(mod, 'MACRO_DIR', str(macro_dir))

    path = mod.record_macro('demo')
    assert Path(path).exists()
    assert json.load(open(path)) == events

    result = mod.play_macro('demo')
    assert 'Played macro' in result


def test_record_macro_script(tmp_path, monkeypatch):
    mod = importlib.import_module('modules.automation_learning')
    events = [{'x': 2}]
    mock_pa = types.SimpleNamespace(record=lambda: events, play=lambda e: None)
    monkeypatch.setattr(mod, 'pyautogui', mock_pa)
    monkeypatch.setattr(mod, '_IMPORT_ERROR', None)

    macro_dir = tmp_path / 'macros'
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(mod, 'MACRO_DIR', str(macro_dir))

    path = mod.record_macro_script('demo2')
    assert Path(path).exists()
    assert (macro_dir / 'demo2.json').exists()
    text = Path(path).read_text()
    assert 'pyautogui.play' in text


def test_record_macro_no_record_attr(tmp_path, monkeypatch):
    """Ensure fallback recorder works when pyautogui lacks record()."""
    mod = importlib.import_module('modules.automation_learning')
    mock_pa = types.SimpleNamespace()
    monkeypatch.setattr(mod, 'pyautogui', mock_pa)
    monkeypatch.setattr(mod, '_IMPORT_ERROR', None)
    # Replace fallback recorder with stub
    monkeypatch.setattr(mod, 'record_events', lambda: [{'z': 3}])
    monkeypatch.setattr(mod, 'play_events', lambda ev: None)

    macro_dir = tmp_path / 'macros'
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(mod, 'MACRO_DIR', str(macro_dir))

    path = mod.record_macro('demo3')
    assert Path(path).exists()
    assert json.load(open(path)) == [{'z': 3}]
    result = mod.play_macro('demo3')
    assert 'Played macro' in result
