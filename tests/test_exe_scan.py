import os
import modules.desktop_shortcuts as ds

def test_build_exe_map(tmp_path):
    (tmp_path / "dirA").mkdir()
    exe1 = tmp_path / "dirA" / "AppOne.exe"
    exe1.write_text("x")
    exe2 = tmp_path / "AppTwo.EXE"
    exe2.write_text("y")
    result = ds.build_exe_map([str(tmp_path)])
    assert result["appone"].endswith("AppOne.exe")
    assert result["apptwo"].endswith("AppTwo.EXE")

def test_build_shortcut_map_includes_system(monkeypatch):
    monkeypatch.setattr(ds, "build_exe_map", lambda: {"foo": "/x/foo.exe"})
    monkeypatch.setattr(ds, "get_desktop_path", lambda: "/nonexistent")
    mp = ds.build_shortcut_map(include_system=True)
    assert mp["foo"] == "/x/foo.exe"
