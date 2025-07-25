import sys
import types

sys.modules.setdefault('keyboard', types.ModuleType('keyboard'))
sys.modules.setdefault('pyautogui', types.ModuleType('pyautogui'))

import cli_assistant as cli


def test_handle_cli_input_queues_plan(monkeypatch, capsys):
    executed = []
    monkeypatch.setattr(cli, "parse_and_execute", lambda text: executed.append(text) or f"ok {text}")
    monkeypatch.setattr(cli, "is_listening", lambda: True)
    monkeypatch.setattr(cli, "check_wake", lambda x: False)
    monkeypatch.setattr(cli, "check_sleep", lambda x: False)

    out = cli.handle_cli_input("open app then close app")
    _ = capsys.readouterr()  # drain prints from queue processing
    assert "Queued tasks" in out
    assert executed == ["open app", "close app"]

