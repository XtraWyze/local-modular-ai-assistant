import importlib
from pathlib import Path


def test_initialize(tmp_path, monkeypatch):
    init_mod = importlib.import_module('initialize_skills_folder')
    monkeypatch.chdir(tmp_path)
    init_mod.initialize_skills_folder('skills')
    skills = Path('skills')
    assert skills.exists()
    assert (skills / '__init__.py').exists()
    assert (skills / 'example_skill.py').exists()

