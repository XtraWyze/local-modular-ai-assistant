"""Planning agent.

This module breaks a user's high level request into smaller subtasks.
It can then delegate those subtasks to other agents using a dispatcher
callback. The planning logic is intentionally simple so it can run
without heavy dependencies.
"""

from typing import List, Callable


def create_plan(task: str) -> List[str]:
    """Return ``task`` as a single-item plan."""
    text = task.strip().lower()
    return [text] if text else []


def assign_tasks(plan: List[str], dispatch_func: Callable[[str], None]) -> None:
    """Send each item of ``plan`` to ``dispatch_func`` in order."""
    for sub in plan:
        dispatch_func(sub)
