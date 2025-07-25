import importlib
import json
from pathlib import Path
import types


def _setup_requests(monkeypatch):
    class DummyResp:
        content = b'data'

        def raise_for_status(self):
            pass

    mod = types.SimpleNamespace(get=lambda url, timeout=60: DummyResp())
    monkeypatch.setitem(importlib.import_module('modules.launcher_installer').__dict__, 'requests', mod)


def test_register_launcher(tmp_path, monkeypatch):
    li = importlib.import_module('modules.launcher_installer')
    monkeypatch.chdir(tmp_path)
    li.register_launcher('foo', 'https://example.com/foo.exe')
    data = json.loads(Path('learned_launchers.json').read_text())
    assert data['foo'] == 'https://example.com/foo.exe'


def test_install_epic_launcher(tmp_path, monkeypatch):
    li = importlib.import_module('modules.launcher_installer')
    monkeypatch.chdir(tmp_path)
    _setup_requests(monkeypatch)
    monkeypatch.setattr(li, '_install_file', lambda path: 'installed')
    result = li.install_epic_launcher()
    assert result == 'installed'
    assert Path('EpicGamesLauncherInstaller.msi').exists()

