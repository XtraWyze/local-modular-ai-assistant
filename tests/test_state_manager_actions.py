import importlib
import json


def test_remove_and_clear_actions(tmp_path, monkeypatch):
    sm = importlib.import_module("state_manager")
    importlib.reload(sm)

    actions_file = tmp_path / "actions.json"
    monkeypatch.setattr(sm, "ACTIONS_FILE", str(actions_file), raising=False)

    sm.actions = {}
    sm.register_action("one", "a.py")
    sm.register_action("two", "b.py")
    assert "one" in sm.actions and "two" in sm.actions

    removed = sm.remove_action("one")
    assert removed is True
    assert "one" not in sm.actions

    sm.clear_actions()
    assert sm.actions == {}
    saved = json.loads(actions_file.read_text())
    assert saved == {}

