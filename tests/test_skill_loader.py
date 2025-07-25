from pathlib import Path
import time
from skills.skill_loader import SkillRegistry


def test_load_and_reload(tmp_path, monkeypatch):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "__init__.py").write_text("")
    skill_file = skills_dir / "demo.py"
    skill_file.write_text("""__all__=['greet']\n
def greet():\n    return 'hi'\n""")
    monkeypatch.syspath_prepend(str(tmp_path))

    reg = SkillRegistry(skills_dir)
    funcs = reg.get_functions()
    assert funcs["greet"]() == "hi"

    # Modify skill and reload
    skill_file.write_text("""__all__=['greet']\n
def greet():\n    return 'bye'\n""")
    time.sleep(0.1)
    skill_file.touch()
    reg.reload_modified()
    assert reg.get_functions()["greet"]() == "bye"

