import importlib
import sqlite3


def test_save_and_fetch(tmp_path, monkeypatch):
    lts = importlib.import_module('modules.long_term_storage')
    importlib.reload(lts)
    db_path = tmp_path / 'ltmem.db'
    monkeypatch.setattr(lts, 'DB_FILE', str(db_path))
    lts.initialize()
    assert db_path.exists()

    assert lts.save_entry('hello') is True
    rows = lts.fetch_recent(limit=1)
    assert rows and rows[0][0] == 'hello'
