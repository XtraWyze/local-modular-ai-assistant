import importlib


def test_load_url_html(monkeypatch):
    mod = importlib.import_module("modules.web_activity")
    importlib.reload(mod)
    mod._HISTORY.clear()
    events = []

    class DummyFrame:
        def load_website(self, url):
            events.append(url)

    monkeypatch.setattr(mod.webbrowser, "open", lambda url: events.append(f"open:{url}"))

    mod.load_url("http://example.com", DummyFrame())

    assert events == ["http://example.com"]
    assert mod.get_history() == ["http://example.com"]


def test_load_url_fallback(monkeypatch):
    mod = importlib.import_module("modules.web_activity")
    importlib.reload(mod)
    mod._HISTORY.clear()
    events = []
    monkeypatch.setattr(mod.webbrowser, "open", lambda url: events.append(url))

    mod.load_url("http://example.com", None)

    assert events == ["http://example.com"]
    assert mod.get_history() == ["http://example.com"]
