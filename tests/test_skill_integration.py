import importlib
from skills.skill_loader import SkillRegistry


def test_orchestrator_loads_skills(tmp_path, monkeypatch):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "__init__.py").write_text("")
    (skills_dir / "hello.py").write_text("""__all__=['say']\n
def say():\n    return 'ok'\n""")
    monkeypatch.syspath_prepend(str(tmp_path))

    import orchestrator
    orchestrator.SKILL_REGISTRY = SkillRegistry(skills_dir)
    orchestrator._refresh_skills()
    assert orchestrator.ALLOWED_FUNCTIONS['say']() == 'ok'



