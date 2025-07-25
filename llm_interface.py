import json
from urllib import request
from config_loader import ConfigLoader
from memory_manager import search_memory
from error_logger import log_error
from module_manager import get_module_overview

# Load config once at import
_config_loader = ConfigLoader()
config = _config_loader.config

SYSTEM_PROMPT = (
    "You are a modular, local-first AI assistant capable of voice interaction, "
    "desktop automation, memory recall, plugin usage, and learning new tools. "
    "You use local memory to recall past events and can control the system through modules."
)


def _module_prompt() -> str:
    """Return a short description of available modules for the system prompt."""
    overview = get_module_overview()
    if not overview:
        return ""
    parts = [f"{name}: {', '.join(funcs)}" for name, funcs in sorted(overview.items()) if funcs]
    if not parts:
        return ""
    return "Available modules -> " + "; ".join(parts)


def _get_url():
    """Return endpoint URL based on configuration."""
    url = config.get("llm_url")
    if url:
        return url
    backend = config.get("llm_backend", "localai")
    if backend == "webui":
        return "http://localhost:5000/v1/chat/completions"
    return "http://localhost:11434/v1/chat/completions"


def generate_response(prompt: str, history=None, system_prompt: str | None = None):
    """Send ``prompt`` and optional ``history`` to the local LLM backend."""
    history = history or []
    system_prompt = system_prompt or SYSTEM_PROMPT

    # Inject relevant memory into the system prompt
    memory_hits = search_memory(prompt)
    if memory_hits:
        mem_text = "\n".join(memory_hits)
        system_prompt = f"{system_prompt}\nRelevant past events:\n{mem_text}"

    mod_text = _module_prompt()
    if mod_text:
        system_prompt = f"{system_prompt}\n{mod_text}"

    messages = [{"role": "system", "content": system_prompt}] + history
    messages.append({"role": "user", "content": prompt})
    data = {
        "model": config.get("llm_model", "llama3"),
        "messages": messages,
        "temperature": 0.7,
    }


    url = _get_url()
    try:
        req = request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with request.urlopen(req, timeout=60) as resp:
            resp_data = json.load(resp)
        if isinstance(resp_data, dict) and "error" in resp_data:
            err = resp_data["error"]
            log_error(f"LLM backend error: {err}")
            return f"[LLM Error] {err}"
        try:
            return resp_data["choices"][0]["message"]["content"]
        except Exception as exc:
            log_error(f"LLM response missing fields: {resp_data} ({exc})")
            return "[LLM Error] Invalid response"
    except Exception as exc:  # pragma: no cover - network failure
        log_error(f"LLM request failed: {exc}")
        return f"[LLM Error] {exc}"
