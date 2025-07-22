"""concurrent_tasks.py
Utility functions for running tasks concurrently using threads.
"""

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, Tuple, Any

from error_logger import log_error

DEFAULT_WORKERS = 4

__all__ = ["run_tasks"]


def _parse_task(task: Any) -> Tuple[Callable, Tuple, dict]:
    """Normalize ``task`` into ``(callable, args, kwargs)`` tuple."""
    if callable(task):
        return task, (), {}
    if isinstance(task, tuple) and task:
        func = task[0]
        args = task[1] if len(task) > 1 else ()
        kwargs = task[2] if len(task) > 2 else {}
        if not callable(func):
            raise TypeError("First element of task tuple must be callable")
        return func, args, kwargs
    raise TypeError("Task must be a callable or (callable, args, kwargs) tuple")


def run_tasks(tasks: Iterable[Any], max_workers: int | None = DEFAULT_WORKERS) -> list:
    """Run multiple tasks concurrently and return their results.

    Parameters
    ----------
    tasks : Iterable
        Each item is either a callable or a tuple ``(callable, args, kwargs)``.
    max_workers : int, optional
        Number of worker threads to use.

    Returns
    -------
    list
        Results in the same order as ``tasks``.
    """
    results = []
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for task in tasks:
                func, args, kwargs = _parse_task(task)
                futures.append(executor.submit(func, *args, **kwargs))
            for fut in futures:
                results.append(fut.result())
    except Exception as e:  # pragma: no cover - error path
        log_error(f"[concurrent_tasks] Error running tasks: {e}")
    return results


def get_info():
    return {
        "name": "concurrent_tasks",
        "description": "Run multiple callables concurrently using threads.",
        "functions": ["run_tasks"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Utilities for running a list of functions concurrently with threads."
