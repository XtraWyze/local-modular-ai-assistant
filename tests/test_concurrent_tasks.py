import importlib
import time

ct = importlib.import_module("modules.concurrent_tasks")


def test_run_tasks_returns_results_quickly():
    def delay(val, d):
        time.sleep(d)
        return val

    start = time.time()
    results = ct.run_tasks([
        (delay, (1, 0.2), {}),
        (delay, (2, 0.2), {}),
    ], max_workers=2)
    duration = time.time() - start
    assert results == [1, 2]
    assert duration < 0.35


def test_run_tasks_accepts_plain_callables():
    def hello():
        return "hi"

    assert ct.run_tasks([hello]) == ["hi"]
