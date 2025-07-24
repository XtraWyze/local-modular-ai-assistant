"""Learning agent capable of creating new skill modules via OpenAI."""

from __future__ import annotations

import importlib
import importlib.util
import os
import re
import sys
from pathlib import Path
from types import ModuleType

from error_logger import log_error

try:
    from tools import OpenAI
except Exception:  # pragma: no cover - wrapper missing
    try:
        from openai import OpenAI  # type: ignore
    except Exception:  # pragma: no cover - library missing
        OpenAI = None  # type: ignore


SKILLS_DIR = Path(__file__).parent / "skills"


class LearningAgent:
    """Generate and load new skill modules using the OpenAI API."""

    def _sanitize_name(self, text: str) -> str:
        """Return a safe module name derived from ``text``."""
        name = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
        name = re.sub(r"_+", "_", name).strip("_")
        return name or "skill"

    def _write_test_stub(self, name: str) -> None:
        tests_dir = SKILLS_DIR / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        test_path = tests_dir / f"test_{name}.py"
        if not test_path.exists():
            test_path.write_text(
                f"from modules.skills import {name}\n\n\n"
                f"def test_run():\n"
                f"    assert isinstance({name}.run({{}}), str)\n",
                encoding="utf-8",
            )

    def _dynamic_import(self, name: str, path: Path) -> ModuleType | None:
        spec = importlib.util.spec_from_file_location(f"modules.skills.{name}", path)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        except Exception as e:  # pragma: no cover - import error
            log_error(f"[learning] Failed to import {name}: {e}")
            return None
        sys.modules[f"modules.skills.{name}"] = mod
        import modules.skills as pkg
        setattr(pkg, name, mod)
        return mod

    def learn_skill(self, description: str) -> str:
        """Generate, save, and import a new skill described by ``description``."""
        name = self._sanitize_name(description)
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        mod_path = SKILLS_DIR / f"{name}.py"
        if mod_path.exists():
            return f"Skill '{name}' already exists."

        if OpenAI is None:
            log_error("OpenAI wrapper not available")
            return "OpenAI is not available to generate code."

        prompt = (
            "Write Python code implementing:\n"
            "def run(params: dict) -> str:\n"
            f"    \"\"\"{description}\"\"\"\n"
            "    # implementation\n"
            "Return only the function body indented."
        )

        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            resp = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=200,
            )
            code = resp.choices[0].text.strip()
        except Exception as e:  # pragma: no cover - network failure
            log_error(f"OpenAI request failed: {e}")
            return f"Error generating skill: {e}"

        module_code = (
            f"def run(params: dict) -> str:\n"
            f"    \"\"\"{description}\"\"\"\n"
            + "\n".join(f"    {line}" for line in code.splitlines())
            + "\n"
        )

        try:
            mod_path.write_text(module_code, encoding="utf-8")
        except Exception as e:  # pragma: no cover - disk failure
            log_error(f"Failed to write skill {name}: {e}")
            return f"Error saving skill: {e}"

        self._write_test_stub(name)
        mod = self._dynamic_import(name, mod_path)
        if not mod:
            return f"Failed to load skill '{name}'."

        return f"Learned new skill {name}\u2014you can now say 'run {name}'."


def get_description() -> str:
    """Return a short summary of this module."""
    return "Teach the assistant new skills using the OpenAI API."
