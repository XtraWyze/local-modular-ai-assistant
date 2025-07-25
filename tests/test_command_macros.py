import importlib
from pathlib import Path


def test_record_and_run(tmp_path, monkeypatch):
    cm = importlib.import_module('modules.command_macros')
    importlib.reload(cm)
    monkeypatch.setattr(cm, 'FILE_PATH', str(tmp_path / 'cmd.json'), raising=False)

    assert cm.start_recording('demo').startswith('Recording')
    cm.record_command('open notepad')
    cm.record_command('type hello')
    assert cm.stop_recording() == "Saved macro 'demo'"
    assert Path(cm.FILE_PATH).exists()
    assert cm.list_macros() == ['demo']

    executed = []
    cm.run_macro('demo', lambda c: executed.append(c))
    assert executed == ['open notepad', 'type hello']
