
import build_apk


def test_ensure_spec_runs_init(monkeypatch, tmp_path):
    cmds = []
    monkeypatch.setattr(build_apk, "SPEC_FILE", tmp_path / "buildozer.spec")
    monkeypatch.setattr(build_apk.subprocess, "check_call", lambda c: cmds.append(c))
    build_apk.ensure_spec()
    assert ["buildozer", "init"] in cmds


def test_build_apk_invokes_build(monkeypatch):
    cmds = []
    monkeypatch.setattr(build_apk, "ensure_spec", lambda: None)
    monkeypatch.setattr(build_apk.subprocess, "check_call", lambda c: cmds.append(c))
    build_apk.build_apk()
    assert build_apk.BUILD_COMMAND in cmds
