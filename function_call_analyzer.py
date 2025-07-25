"""Utility to detect undefined or external function calls within Python files."""

from __future__ import annotations

import ast
import builtins
import os
from collections import defaultdict
from typing import Iterable, Mapping

from error_logger import log_error


BUILTIN_NAMES = set(dir(builtins))


def _collect_defs(tree: ast.AST) -> set[str]:
    """Return a set of all function names defined in ``tree``."""
    defs: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defs.add(node.name)
    return defs


def _collect_imports(tree: ast.AST) -> set[str]:
    """Return names imported directly in ``tree``."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def _collect_calls(tree: ast.AST) -> set[str]:
    """Return function names that are called in ``tree``."""
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                calls.add(func.id)
            elif isinstance(func, ast.Attribute):
                calls.add(func.attr)
    return calls


def scan_file(path: str) -> tuple[set[str], set[str], set[str]]:
    """Parse ``path`` and return defs, imports and calls."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
    except Exception as exc:  # pragma: no cover - parse errors logged
        log_error(f"Failed to parse {path}: {exc}")
        return set(), set(), set()
    return _collect_defs(tree), _collect_imports(tree), _collect_calls(tree)


def scan_project(root: str) -> Mapping[str, list[str]]:
    """Scan ``root`` recursively for ``.py`` files and report undefined calls."""
    results: dict[str, list[str]] = defaultdict(list)
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if not name.endswith(".py"):
                continue
            full = os.path.join(dirpath, name)
            defs, imports, calls = scan_file(full)
            missing = sorted(
                call
                for call in calls
                if call not in defs and call not in imports and call not in BUILTIN_NAMES
            )
            if missing:
                results[os.path.relpath(full, root)] = missing
    return results


def main(args: Iterable[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Project directory to scan (default: current directory)",
    )
    parsed = parser.parse_args(args)
    results = scan_project(parsed.path)
    if not results:
        print("No missing calls detected.")
        return
    for file, missing in results.items():
        print(f"\n{file}:")
        for name in missing:
            print(f"  {name}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
