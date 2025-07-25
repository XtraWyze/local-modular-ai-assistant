import pytest

from watchdog import watchdog


def test_watchdog_restarts_until_success(monkeypatch):
    calls = {
        "count": 0
    }

    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("boom")
        return "ok"

    wrapped = watchdog(max_restarts=5, delay=0)(flaky)
    assert wrapped() == "ok"
    assert calls["count"] == 3


def test_watchdog_raises_after_limit(monkeypatch):
    def always_fail():
        raise ValueError("nope")

    wrapped = watchdog(max_restarts=1, delay=0)(always_fail)
    with pytest.raises(ValueError):
        wrapped()
