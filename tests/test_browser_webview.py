import importlib


def test_open_url_triggers_callback(monkeypatch):
    ba = importlib.import_module("modules.browser_automation")
    importlib.reload(ba)
    events = []
    class DummyDriver:
        def get(self, url):
            events.append(url)
    monkeypatch.setattr(ba, "_driver", DummyDriver())
    ba.set_webview_callback(lambda url: events.append(f"cb:{url}"))
    ba.open_url("http://example.com")
    assert events == ["http://example.com", "cb:http://example.com"]
