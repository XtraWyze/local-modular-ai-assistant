import os
from pathlib import Path

from function_call_analyzer import scan_project


def test_scan_project(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()

    file_a = project / "a.py"
    file_a.write_text(
        """\n"""
        """def foo():\n"""
        """    bar()\n"""
        """\n"""
        """def bar():\n"""
        """    pass\n"""
        """\n"""
        """baz()\n"""
    )

    file_b = project / "b.py"
    file_b.write_text(
        """\n"""
        """from a import foo\n"""
        """\n"""
        """def qux():\n"""
        """    foo()\n"""
        """"""
    )

    result = scan_project(str(project))
    assert sorted(result[file_a.relative_to(project).as_posix()]) == ["baz"]
    assert file_b.relative_to(project).as_posix() not in result

