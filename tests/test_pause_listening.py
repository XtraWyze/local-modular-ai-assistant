import importlib
import json
import sys
import types
from tests.test_assistant_utils import import_assistant

class DummyWidget:
    def insert(self, *a, **kw):
        pass
    def see(self, *a, **kw):
        pass

def test_process_input_pauses_listening(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    assistant.set_listening(True)
    states = {}

    def fake_llm(prompt):
        states['during'] = assistant.is_listening()
        return 'ok'

    monkeypatch.setattr(assistant, 'talk_to_llm', fake_llm)

    assistant.process_input('hello', DummyWidget())
    assert states.get('during') is False
    assert assistant.is_listening() is False

    assistant.check_wake('next question')
    assert assistant.is_listening() is True


def test_pending_commands_cleared(monkeypatch):
    assistant, _ = import_assistant(monkeypatch)
    assistant.set_listening(True)

    def fake_llm(prompt):
        return 'ok'

    monkeypatch.setattr(assistant, 'talk_to_llm', fake_llm)

    assistant.queue_command('extra', DummyWidget())
    assert assistant.pending_commands
    assistant.process_input('hello', DummyWidget())
    assert assistant.pending_commands == []


def test_learn_resume_phrase(monkeypatch, tmp_path):
    assistant, _ = import_assistant(monkeypatch)
    phrase = 'continue please'
    path = tmp_path / 'state.json'
    cfg_path = tmp_path / 'config.json'
    cfg_path.write_text('{}')
    sm = importlib.import_module('state_manager')
    importlib.reload(sm)
    monkeypatch.setattr(sm, 'STATE_FILE', str(path), raising=False)
    sm._config_loader = sm.ConfigLoader(str(cfg_path))
    sm.load_state()
    sm.add_resume_phrase(phrase)
    assert phrase in sm.get_resume_phrases()
    saved = json.loads(cfg_path.read_text())
    assert phrase in saved['resume_phrases']
