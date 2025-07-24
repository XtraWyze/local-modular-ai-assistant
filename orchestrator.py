"""LLM orchestration and safe tool execution."""

from __future__ import annotations

import ast
import importlib
import inspect
import os
import pkgutil
import re
import socket
import types
from pathlib import Path

from assistant import talk_to_llm

# Dynamically load all modules under the "modules" package and collect
# functions exported via their ``__all__`` variables.
TOOLS = types.SimpleNamespace()
module_dir = Path(__file__).parent / "modules"
for info in pkgutil.iter_modules([str(module_dir)]):
    mod_name = f"modules.{info.name}"
    try:
        mod = importlib.import_module(mod_name)
    except Exception:
        continue
    for fname in getattr(mod, "__all__", []):
        func = getattr(mod, fname, None)
        if callable(func):
            setattr(TOOLS, fname, func)

# Build allowed function mapping automatically from the TOOLS namespace
ALLOWED_FUNCTIONS = {
    name: getattr(TOOLS, name)
    for name in dir(TOOLS)
    if callable(getattr(TOOLS, name)) and not name.startswith("_")
}

TOOL_LIST = ", ".join(sorted(ALLOWED_FUNCTIONS))

HIGH_RISK_FUNCS = {"run_python", "open_app", "close_app", "copy_file", "move_file"}
# Allow high-risk functions by default unless explicitly disabled
ALLOW_HIGH_RISK = os.environ.get("ALLOW_HIGH_RISK", "1") == "1"

__all__ = ["parse_and_execute", "handle_system_scan"]

PROMPT_HEADER = (
    "Translate the user's request into exactly one Python function call "
    f"using these tools: {TOOL_LIST}. "
    "Output only the call, e.g. open_app('C:\\\\Path\\\\app.exe')."
    "\nOnly use a function if the user is very explicit. For questions, just return an empty string."
)

def _handle_learning(text: str) -> str | None:
    """Handle ``learn <desc>`` commands."""
    if text.lower().startswith("learn "):
        from modules.learning import LearningAgent

        desc = text[6:].strip()
        return LearningAgent().learn_skill(desc)
    return None


def _handle_module_generation(text: str) -> str | None:
    """Handle ``create module <name> <desc>`` commands."""
    m = re.match(r"(?:create|generate) module (\w+)(?:\s+(.*))?", text, re.IGNORECASE)
    if not m:
        return None
    name, desc = m.groups()
    desc = desc or ""
    try:
        from modules import module_generator

        path = module_generator.generate_module_interactive(desc, name=name)
        return path
    except Exception as e:  # pragma: no cover - generation errors
        return f"Error generating module: {e}"


def _handle_run_skill(text: str) -> str | None:
    """Run a module's ``run`` function via ``run <name>``."""
    if not text.lower().startswith("run "):
        return None
    import modules as skills_pkg

    skill_name = text[4:].strip()
    mod = getattr(skills_pkg, skill_name, None)
    if mod:
        try:
            return mod.run({})
        except Exception as e:
            return f"Error running skill '{skill_name}': {e}"
    return f"I don\u2019t know a skill called '{skill_name}'."


def _handle_terminate_alias(text: str) -> str | None:
    """Support ``terminate <app>`` as alias for ``close_app``."""
    term = re.match(r"\b(?:terminate|kill)\s+(.+)", text, re.IGNORECASE)
    if not term:
        return None
    app = term.group(1)
    if "close_app" not in ALLOWED_FUNCTIONS:
        return talk_to_llm(text)
    if "close_app" in HIGH_RISK_FUNCS and not ALLOW_HIGH_RISK:
        return "Error: close_app requires elevated privileges."
    func = ALLOWED_FUNCTIONS["close_app"]
    try:
        return func(app)
    except Exception as e:
        return f"Error running close_app: {e}"


def _handle_minimize_alias(text: str) -> str | None:
    """Support ``minimize <window>`` as alias for ``minimize_window``."""
    m = re.match(r"\bminimize\s+(.+)", text, re.IGNORECASE)
    if not m:
        return None
    target = m.group(1)
    if "minimize_window" not in ALLOWED_FUNCTIONS:
        return talk_to_llm(text)
    func = ALLOWED_FUNCTIONS["minimize_window"]
    try:
        success, msg = func(target)
        return msg
    except Exception as e:
        return f"Error running minimize_window: {e}"


def _execute_tool_call(fn_name: str, args: str, user_text: str) -> str:
    """Validate and execute a tool call returned by the LLM."""
    if fn_name not in ALLOWED_FUNCTIONS:
        return talk_to_llm(user_text)
    if fn_name in HIGH_RISK_FUNCS and not ALLOW_HIGH_RISK:
        return f"Error: {fn_name} requires elevated privileges."

    func = ALLOWED_FUNCTIONS[fn_name]

    sig = inspect.signature(func)
    params = sig.parameters
    if len(params) > 0 and args.strip() in ["", "None"]:
        return talk_to_llm(user_text)

    try:
        parsed_args = ast.literal_eval(f"[{args}]") if args.strip() else []
    except Exception:
        return talk_to_llm(user_text)

    for arg_val, param in zip(parsed_args, params.values()):
        ann = param.annotation
        if ann is not inspect._empty and not isinstance(arg_val, ann):
            return talk_to_llm(user_text)
        if isinstance(arg_val, (int, float)) and not -10000 <= arg_val <= 10000:
            return talk_to_llm(user_text)
        if isinstance(arg_val, str) and len(arg_val) > 1000:
            return talk_to_llm(user_text)

    try:
        return func(*parsed_args)
    except Exception as e:  # pragma: no cover - tool runtime errors
        return f"Error running {fn_name}: {e}"


def _handle_llm_call(text: str) -> str:
    """Ask the LLM for a tool call and execute it."""
    call = talk_to_llm(f"{PROMPT_HEADER}\nUser: {text}\nAssistant:")
    m = re.match(r"(\w+)\((.*)\)", call.strip())
    if not m:
        return talk_to_llm(text)

    fn, args = m.groups()
    return _execute_tool_call(fn, args, text)


def parse_and_execute(user_text: str) -> str:
    """Parse ``user_text`` and execute an appropriate tool or fallback."""

    for handler in (
        _handle_learning,
        _handle_module_generation,
        _handle_run_skill,
        _handle_terminate_alias,
        _handle_minimize_alias,
    ):
        result = handler(user_text)
        if result is not None:
            return result

    return _handle_llm_call(user_text)


def handle_system_scan() -> dict:
    """Collect and return basic system metrics."""
    import psutil

    cpu_percent = psutil.cpu_percent(interval=0.1)

    vm = psutil.virtual_memory()
    memory = {
        "total": vm.total,
        "available": vm.available,
        "percent": vm.percent,
    }

    disks = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except Exception:
            continue
        disks.append({
            "mountpoint": part.mountpoint,
            "total": usage.total,
            "percent": usage.percent,
        })

    net = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                net.append({"interface": iface, "address": addr.address})

    procs = []
    for proc in psutil.process_iter(attrs=["pid", "name", "memory_percent"]):
        try:
            info = proc.info
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        procs.append(info)

    procs.sort(key=lambda p: p.get("memory_percent", 0), reverse=True)
    top_processes = [
        {
            "pid": p["pid"],
            "name": p.get("name", ""),
            "memory_percent": p.get("memory_percent", 0.0),
        }
        for p in procs[:5]
    ]

    return {
        "cpu": {"percent": cpu_percent},
        "memory": memory,
        "disks": disks,
        "network": net,
        "top_processes": top_processes,
    }
