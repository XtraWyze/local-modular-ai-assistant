import importlib
import types
import sys
from pathlib import Path


def test_sanitize_name():
    learning = importlib.import_module('modules.learning')
    agent = learning.LearningAgent()
    assert agent._sanitize_name('Hello World!') == 'hello_world'


def test_learn_skill_creates_module(tmp_path, monkeypatch):
    class StubCompletions:
        def create(self, **kw):
            return types.SimpleNamespace(choices=[types.SimpleNamespace(text="return 'ok'\n")])

    class StubClient:
        def __init__(self, *a, **kw):
            self.completions = StubCompletions()

    monkeypatch.setitem(sys.modules, 'tools', types.SimpleNamespace(OpenAI=StubClient))
    learning = importlib.reload(importlib.import_module('modules.learning'))
    monkeypatch.setattr(learning, 'SKILLS_DIR', tmp_path / 'skills')
    agent = learning.LearningAgent()
    msg = agent.learn_skill('say ok')
    assert 'run say_ok' in msg
    skills_pkg = importlib.import_module('modules.skills')
    mod = getattr(skills_pkg, 'say_ok')
    assert mod.run({}) == 'ok'
