import importlib
import types


def test_skill_functions_loaded(tmp_path, monkeypatch):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "greet.py").write_text("def hello(name):\n    return f'hi {name}'\n")

    import skill_loader
    orig = skill_loader.load_skills
    monkeypatch.setattr(skill_loader, "load_skills", lambda directory=None: orig(str(skills_dir)))

    orch = importlib.reload(importlib.import_module("orchestrator"))

    assert "hello" in orch.ALLOWED_FUNCTIONS
    assert orch.ALLOWED_FUNCTIONS["hello"]("bob") == "hi bob"
