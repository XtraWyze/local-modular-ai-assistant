import importlib
import types
import sys

sys_modules = {
    'keyboard': types.ModuleType('keyboard'),
    'pyautogui': types.ModuleType('pyautogui'),
}
sys.modules.update(sys_modules)

import cli_assistant as cli


def test_cli_macro_learning(monkeypatch, tmp_path):
    cm = importlib.import_module('modules.command_macros')
    importlib.reload(cm)
    monkeypatch.setattr(cm, 'FILE_PATH', str(tmp_path / 'cmd.json'), raising=False)
    monkeypatch.setitem(sys.modules, 'modules.command_macros', cm)

    monkeypatch.setattr(cli, 'parse_and_execute', lambda c: f'ran {c}')

    out = cli.handle_cli_input('learn this macro demo')
    assert 'Recording' in out
    cli.handle_cli_input('open 1')
    cli.handle_cli_input('type 2')
    out = cli.handle_cli_input('stop macro')
    assert 'Saved macro' in out
    executed = []
    monkeypatch.setattr(cli, 'parse_and_execute', lambda c: executed.append(c) or 'ok')
    out = cli.handle_cli_input('run macro demo')
    assert 'Ran macro' in out
    assert executed == ['open 1', 'type 2']
