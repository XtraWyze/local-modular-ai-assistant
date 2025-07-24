import importlib
import pkgutil
import types
import re
import ast
import inspect
import os
import socket
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

PROMPT_HEADER = (
    "Translate the user's request into exactly one Python function call "
    f"using these tools: {TOOL_LIST}. "
    "Output only the call, e.g. open_app('C:\\\\Path\\\\app.exe')."
    "\nOnly use a function if the user is very explicit. For questions, just return an empty string."
)

def parse_and_execute(user_text: str) -> str:
    """Parse the LLM response and safely execute a whitelisted function."""

    if user_text.lower().startswith("learn "):
        from modules.learning import LearningAgent

        desc = user_text[6:].strip()
        return LearningAgent().learn_skill(desc)

    m = re.match(r"(?:create|generate) module (\w+)(?:\s+(.*))?", user_text, re.IGNORECASE)
    if m:
        name, desc = m.groups()
        desc = desc or ""
        try:
            from modules import module_generator

            path = module_generator.generate_module_interactive(desc, name=name)
            return path
        except Exception as e:
            return f"Error generating module: {e}"

    if user_text.lower().startswith("run "):
        import modules as skills_pkg

        skill_name = user_text[4:].strip()
        mod = getattr(skills_pkg, skill_name, None)
        if mod:
            try:
                return mod.run({})
            except Exception as e:
                return f"Error running skill '{skill_name}': {e}"
        return f"I don\u2019t know a skill called '{skill_name}'."

    # Quick manual handling for common phrases like "terminate <app>"
    term = re.match(r"\b(?:terminate|kill)\s+(.+)", user_text, re.IGNORECASE)
    if term:
        app = term.group(1)
        if "close_app" not in ALLOWED_FUNCTIONS:
            return talk_to_llm(user_text)
        if "close_app" in HIGH_RISK_FUNCS and not ALLOW_HIGH_RISK:
            return "Error: close_app requires elevated privileges."
        func = ALLOWED_FUNCTIONS["close_app"]
        try:
            return func(app)
        except Exception as e:
            return f"Error running close_app: {e}"

    call = talk_to_llm(f"{PROMPT_HEADER}\nUser: {user_text}\nAssistant:")
    m = re.match(r"(\w+)\((.*)\)", call.strip())
    if not m:
        return talk_to_llm(user_text)

    fn, args = m.groups()
    if fn not in ALLOWED_FUNCTIONS:
        return talk_to_llm(user_text)

    if fn in HIGH_RISK_FUNCS and not ALLOW_HIGH_RISK:
        return f"Error: {fn} requires elevated privileges."

    func = ALLOWED_FUNCTIONS[fn]

    sig = inspect.signature(func)
    params = sig.parameters
    if len(params) > 0 and args.strip() in ["", "None"]:
        # Missing required arguments - fall back to natural language response
        return talk_to_llm(user_text)

    try:
        parsed_args = ast.literal_eval(f"[{args}]") if args.strip() else []
    except Exception:
        # LLM produced bad arguments - fall back to natural language
        return talk_to_llm(user_text)

    # Type and basic range validation
    for arg_val, param in zip(parsed_args, params.values()):
        ann = param.annotation
        if ann is not inspect._empty and not isinstance(arg_val, ann):
            # Invalid type supplied
            return talk_to_llm(user_text)
        if isinstance(arg_val, (int, float)) and not -10000 <= arg_val <= 10000:
            # Out-of-range numeric value
            return talk_to_llm(user_text)
        if isinstance(arg_val, str) and len(arg_val) > 1000:
            # Excessively long string
            return talk_to_llm(user_text)

    try:
        result = func(*parsed_args)
        return result
    except Exception as e:
        return f"Error running {fn}: {e}"


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
