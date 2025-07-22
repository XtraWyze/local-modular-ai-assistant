import importlib

import modules.desktop_shortcuts as ds


def test_open_shortcut_windows(monkeypatch):
    called = []
    monkeypatch.setattr(ds.os, "startfile", lambda t: called.append(("startfile", t)), raising=False)
    monkeypatch.setattr(ds.os.path, "exists", lambda p: True)
    result = ds.open_shortcut("open calc", {"calc": "/tmp/calc.exe"}, fuzzy=False)
    assert called == [("startfile", "/tmp/calc.exe")]
    assert "Opening Calc." in result


def test_open_shortcut_macos(monkeypatch):
    called = []
    monkeypatch.delattr(ds.os, "startfile", raising=False)
    monkeypatch.setattr(ds.sys, "platform", "darwin", raising=False)
    monkeypatch.setattr(ds.os.path, "exists", lambda p: True)
    monkeypatch.setattr(ds.subprocess, "Popen", lambda args: called.append(args))
    result = ds.open_shortcut("open calc", {"calc": "/tmp/calc.app"}, fuzzy=False)
    assert called == [["open", "/tmp/calc.app"]]
    assert "Opening Calc." in result


def test_open_shortcut_linux(monkeypatch):
    called = []
    monkeypatch.delattr(ds.os, "startfile", raising=False)
    monkeypatch.setattr(ds.sys, "platform", "linux", raising=False)
    monkeypatch.setattr(ds.os.path, "exists", lambda p: True)
    monkeypatch.setattr(ds.subprocess, "Popen", lambda args: called.append(args))
    result = ds.open_shortcut("open calc", {"calc": "/tmp/calc.sh"}, fuzzy=False)
    assert called == [["xdg-open", "/tmp/calc.sh"]]
    assert "Opening Calc." in result
