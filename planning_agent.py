"""Planning agent.

This module breaks a user's high level request into smaller subtasks.
It can then delegate those subtasks to other agents using a dispatcher
callback. The planning logic is intentionally simple so it can run
without heavy dependencies.
"""

import re
from typing import List, Callable

KEYWORDS = ["then", "and", "after", "before", "next"]


def create_plan(task: str) -> List[str]:
    """Return a list of subtasks extracted from ``task``."""
    lower = task.lower()
    for kw in KEYWORDS:
        lower = lower.replace(f" {kw} ", "|")
    parts = re.split(r"[.!?\n|]", lower)
    return [p.strip() for p in parts if p.strip()]


def assign_tasks(plan: List[str], dispatch_func: Callable[[str], None]) -> None:
    """Send each item of ``plan`` to ``dispatch_func`` in order."""
    for sub in plan:
        dispatch_func(sub)
