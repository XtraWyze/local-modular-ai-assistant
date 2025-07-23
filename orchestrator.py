import importlib
import pkgutil
import types
import re
import ast
import inspect
import os
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

def parse_and_execute(user_text: str, via_voice: bool = False) -> str:
    """Parse the LLM response and safely execute a whitelisted function.

    Parameters
    ----------
    user_text:
        Raw text from the user.
    via_voice:
        ``True`` if the text originated from speech input.  Currently the
        parameter is informational but is accepted for API compatibility.
    """
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
