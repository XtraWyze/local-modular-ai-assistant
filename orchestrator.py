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
from skills.skill_loader import registry as SKILL_REGISTRY

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

# Load skill plugins and register their public callables
for fname, func in SKILL_REGISTRY.get_functions().items():
    setattr(TOOLS, fname, func)

# Build allowed function mapping automatically from the TOOLS namespace
ALLOWED_FUNCTIONS = {
    name: getattr(TOOLS, name)
    for name in dir(TOOLS)
    if callable(getattr(TOOLS, name)) and not name.startswith("_")
}

TOOL_LIST = ", ".join(sorted(ALLOWED_FUNCTIONS))


def _rebuild_allowed() -> None:
    """Rebuild the allowed function map from ``TOOLS``."""
    global ALLOWED_FUNCTIONS, TOOL_LIST
    ALLOWED_FUNCTIONS = {
        name: getattr(TOOLS, name)
        for name in dir(TOOLS)
        if callable(getattr(TOOLS, name)) and not name.startswith("_")
    }
    TOOL_LIST = ", ".join(sorted(ALLOWED_FUNCTIONS))


def _refresh_skills() -> None:
    """Reload skill plugins and update allowed functions."""
    SKILL_REGISTRY.reload_modified()
    for fname, func in SKILL_REGISTRY.get_functions().items():
        setattr(TOOLS, fname, func)
    _rebuild_allowed()

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


def _extract_window_target(text: str, action: str) -> str | None:
    """Return the window title following ``action`` if present."""
    pattern = rf"\b{action}\s+(?:the\s+)?(?:window\s+|app(?:lication)?\s+)?(.+)"
    m = re.match(pattern, text, re.IGNORECASE)
    if not m:
        return None
    title = m.group(1).strip()
    title = re.sub(r"\s+(?:window|app(?:lication)?)$", "", title, flags=re.IGNORECASE)
    return title


def _handle_minimize_alias(text: str) -> str | None:
    """Support ``minimize <window>`` as alias for ``minimize_window``."""
    target = _extract_window_target(text, "minimize")
    if not target:
        return None
    if "minimize_window" not in ALLOWED_FUNCTIONS:
        return talk_to_llm(text)
    func = ALLOWED_FUNCTIONS["minimize_window"]
    try:
        success, msg = func(target)
        return msg
    except Exception as e:
        return f"Error running minimize_window: {e}"


def _handle_focus_alias(text: str) -> str | None:
    """Support ``focus <window>`` as alias for ``focus_window``."""
    target = _extract_window_target(text, "focus")
    if not target:
        return None
    if "focus_window" not in ALLOWED_FUNCTIONS:
        return talk_to_llm(text)
    func = ALLOWED_FUNCTIONS["focus_window"]
    try:
        success, msg = func(target)
        return msg
    except Exception as e:
        return f"Error running focus_window: {e}"


def _handle_maximize_alias(text: str) -> str | None:
    """Support ``maximize <window>`` as alias for ``maximize_window``."""
    target = _extract_window_target(text, "maximize")
    if not target:
        return None
    if "maximize_window" not in ALLOWED_FUNCTIONS:
        return talk_to_llm(text)
    func = ALLOWED_FUNCTIONS["maximize_window"]
    try:
        success, msg = func(target)
        return msg
    except Exception as e:
        return f"Error running maximize_window: {e}"


def _handle_move_window_alias(text: str) -> str | None:
    """Support ``move <title> to monitor N`` commands."""
    m = re.match(r"move\s+(.+?)\s+(?:to|onto)\s+(?:monitor|screen)\s+(\d+)", text, re.IGNORECASE)
    if not m:
        return None
    title, idx = m.groups()
    if "move_window_to_monitor" not in ALLOWED_FUNCTIONS:
        return talk_to_llm(text)
    func = ALLOWED_FUNCTIONS["move_window_to_monitor"]
    try:
        success, msg = func(title, int(idx))
        return msg
    except Exception as e:
        return f"Error running move_window_to_monitor: {e}"


def _handle_save_exit_alias(text: str) -> str | None:
    """Support ``save and exit <window>`` commands."""
    m = re.match(r"save and exit\s+(.+)", text, re.IGNORECASE)
    if not m:
        return None
    target = m.group(1)
    if "save_and_exit" not in ALLOWED_FUNCTIONS:
        return talk_to_llm(text)
    func = ALLOWED_FUNCTIONS["save_and_exit"]
    try:
        return func(target)
    except Exception as e:
        return f"Error running save_and_exit: {e}"


def _handle_open_alias(text: str) -> str | None:
    """Support ``open <app>`` as alias for ``open_application``."""
    m = re.match(r"(?:open|launch|start)\s+(.+)", text, re.IGNORECASE)
    if not m:
        return None
    app = m.group(1).strip()
    if "open_application" not in ALLOWED_FUNCTIONS:
        return None
    func = ALLOWED_FUNCTIONS["open_application"]
    try:
        ok, msg = func(app)
        return msg
    except Exception as e:
        return f"Error running open_application: {e}"


def _handle_close_alias(text: str) -> str | None:
    """Support ``close <window>`` as alias for ``close_window``."""
    target = _extract_window_target(text, "close")
    if not target:
        return None
    if "close_window" not in ALLOWED_FUNCTIONS:
        return None
    func = ALLOWED_FUNCTIONS["close_window"]
    try:
        ok, msg = func(target)
        return msg
    except Exception as e:
        return f"Error running close_window: {e}"


def _handle_resize_alias(text: str) -> str | None:
    """Support ``resize <window> to WxH`` commands."""
    m = re.match(r"resize\s+(.+?)\s+(?:to\s*)?(\d+)\s*[x, ]\s*(\d+)", text, re.IGNORECASE)
    if not m:
        return None
    title, w, h = m.groups()
    if "resize_window" not in ALLOWED_FUNCTIONS:
        return talk_to_llm(text)
    func = ALLOWED_FUNCTIONS["resize_window"]
    try:
        return func(title.strip(), int(w), int(h))
    except Exception as e:
        return f"Error running resize_window: {e}"


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


def _extract_tool_call(text: str) -> tuple[str, str] | None:
    """Return ``(fn_name, args)`` from the first function call in ``text``."""
    match = re.search(r"([a-zA-Z_][\w]*)\s*\(", text)
    if not match:
        return None
    fn = match.group(1)
    idx = match.end()
    depth = 1
    start = idx
    while idx < len(text):
        ch = text[idx]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return fn, text[start:idx].strip()
        idx += 1
    return None


def _handle_llm_call(text: str) -> str:
    """Ask the LLM for a tool call and execute it."""
    call = talk_to_llm(f"{PROMPT_HEADER}\nUser: {text}\nAssistant:")
    parsed = _extract_tool_call(call.strip())
    if not parsed:
        return talk_to_llm(text)

    fn, args = parsed
    return _execute_tool_call(fn, args, text)


def parse_and_execute(user_text: str) -> str:
    """Parse ``user_text`` and execute an appropriate tool or fallback."""

    _refresh_skills()

    for handler in (
        _handle_learning,
        _handle_module_generation,
        _handle_run_skill,
        _handle_terminate_alias,
        _handle_open_alias,
        _handle_close_alias,
        _handle_minimize_alias,
        _handle_maximize_alias,
        _handle_focus_alias,
        _handle_resize_alias,
        _handle_move_window_alias,
        _handle_save_exit_alias,
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
