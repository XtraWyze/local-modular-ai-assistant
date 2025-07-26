from pathlib import Path
import tempfile
import textwrap

from update_dependencies import collect_module_requirements, read_requirements_file, write_requirements_file


def test_collect_module_requirements(tmp_path: Path) -> None:
    mod_dir = tmp_path / "modules"
    mod_dir.mkdir()
    (mod_dir / "sample.py").write_text('REQUIREMENTS = ["foo", "bar"]\n')
    reqs = collect_module_requirements(mod_dir)
    assert reqs == {"foo", "bar"}


def test_write_and_read(tmp_path: Path) -> None:
    req_file = tmp_path / "req.txt"
    write_requirements_file(req_file, ["a", "b"])
    result = read_requirements_file(req_file)
    assert result == ["a", "b"]
