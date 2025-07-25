import importlib
import yaml


def test_register_and_get_macro(tmp_path, monkeypatch):
    sm = importlib.import_module('state_manager')
    importlib.reload(sm)

    macro_file = tmp_path / 'macros.yaml'
    monkeypatch.setattr(sm, 'MACRO_MAP_FILE', str(macro_file), raising=False)

    sm.macro_map = {}
    sm.save_macro_map()

    msg = sm.register_macro_command('open notes', 'demo')
    assert 'open notes' in sm.macro_map
    assert 'demo' == sm.get_macro_action('open notes')

    data = yaml.safe_load(macro_file.read_text())
    assert data == {'open notes': 'demo'}

    sm.macro_map = {}
    sm.load_macro_map()
    assert sm.get_macro_action('open notes') == 'demo'
