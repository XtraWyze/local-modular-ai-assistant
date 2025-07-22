import json
import re
import android_cli_assistant as aca


def test_remember_and_recall(tmp_path, monkeypatch):
    memfile = tmp_path / "mem.json"
    monkeypatch.setattr(aca, "MEMORY_FILE", str(memfile))
    memory = {}
    assert aca.handle_input("remember the milk", memory) == "I'll remember that."
    assert json.load(open(memfile))["items"] == ["the milk"]
    resp = aca.handle_input("what did you remember", memory)
    assert "the milk" in resp


def test_basic_responses(monkeypatch):
    memory = {}
    assert "Android CLI Assistant" in aca.handle_input("what's your name", memory)
    t = aca.handle_input("what time is it", memory)
    assert re.match(r"\d{2}:\d{2}:\d{2}", t)
    assert "don't understand" in aca.handle_input("foo", memory).lower()


def test_exit(monkeypatch):
    assert aca.handle_input("exit", {}) is None
    assert aca.handle_input("quit", {}) is None
