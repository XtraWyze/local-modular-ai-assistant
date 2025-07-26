import sys
import lan_launcher as ll


def test_launch_client_gui_runs(monkeypatch, tmp_path):
    script = tmp_path / "gui_client.py"
    script.write_text("print('ok')")
    called = {}
    def fake_popen(cmd):
        called['cmd'] = cmd
        class Dummy:
            pass
        return Dummy()
    monkeypatch.setattr(ll.subprocess, 'Popen', fake_popen)
    assert ll.launch_client_gui('1.2.3.4', 1234, str(script))
    assert called['cmd'][0] == sys.executable
    assert str(script) in called['cmd']
    assert '--host' in called['cmd'] and '1.2.3.4' in called['cmd']


def test_launch_client_gui_missing(monkeypatch):
    msgs = []
    monkeypatch.setattr(ll, '_show_error', lambda m: msgs.append(m))
    assert ll.launch_client_gui('0.0.0.0', 1, 'missing.py') is False
    assert msgs and 'not found' in msgs[0]
