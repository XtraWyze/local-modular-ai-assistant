from pathlib import Path
import importlib

from plugin_loader import PluginRegistry


def test_plugin_registry_loads_functions(tmp_path, capsys, monkeypatch):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "__init__.py").write_text("")
    (skills_dir / "skill_a.py").write_text("def greet():\n    return 'hi'\n")
    (skills_dir / "empty.py").write_text("value = 1\n")
    monkeypatch.syspath_prepend(str(tmp_path))

    registry = PluginRegistry(skills_dir)
    funcs = registry.get_functions()
    assert funcs["greet"]() == "hi"
    assert "empty" not in registry.modules

    out = capsys.readouterr().out
    assert "skill_a" in out and "greet" in out

