import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cleanup


def test_cleanup_removes_files(tmp_path, monkeypatch):
    # create dummy structures
    pycache = tmp_path / "mod" / "__pycache__"
    pycache.mkdir(parents=True)
    (pycache / "x.pyc").write_text("x")
    log_file = tmp_path / "test.log"
    db_file = tmp_path / "test.db"
    state_file = tmp_path / "assistant_state.json"
    log_file.write_text("log")
    db_file.write_text("data")
    state_file.write_text("state")

    # avoid writing to real log
    monkeypatch.setattr(cleanup, "log_error", lambda *a, **kw: None)

    cleanup.cleanup(tmp_path)

    assert not pycache.exists()
    assert not log_file.exists()
    assert not db_file.exists()
    assert not state_file.exists()
