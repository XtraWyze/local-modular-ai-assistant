import json
from typing import List, Optional

from modules.utils import resource_path

MODULE_NAME = "llm_model_manager"
MODELS_FILE = resource_path("llm_models.json")

model_paths: List[str] = []
last_model: Optional[str] = None

__all__ = [
    "load_models",
    "save_models",
    "add_model",
    "remove_model",
    "get_last_model",
    "set_last_model",
    "get_info",
    "get_description",
]


def load_models() -> List[str]:
    """Load saved LLM model paths and last selection from ``MODELS_FILE``."""
    global model_paths, last_model
    try:
        with open(MODELS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            model_paths = [str(p) for p in data if isinstance(p, str)]
            last_model = model_paths[0] if model_paths else None
        elif isinstance(data, dict):
            model_paths = [str(p) for p in data.get("models", []) if isinstance(p, str)]
            lm = data.get("last")
            last_model = str(lm) if isinstance(lm, str) else None
        else:
            model_paths, last_model = [], None
    except Exception:
        model_paths, last_model = [], None
    return model_paths


def save_models(models: List[str] | None = None, last: str | None = None) -> None:
    """Persist ``models`` and ``last`` to ``MODELS_FILE``."""
    global model_paths, last_model
    if models is not None:
        model_paths = models
    if last is not None:
        last_model = last
    with open(MODELS_FILE, "w", encoding="utf-8") as f:
        json.dump({"models": model_paths, "last": last_model}, f, indent=2)


def add_model(path: str) -> None:
    """Add ``path`` to saved models."""
    if not path:
        return
    if path not in model_paths:
        model_paths.append(path)
    save_models(model_paths, last_model)


def remove_model(path: str) -> bool:
    """Remove ``path`` from saved models."""
    if path in model_paths:
        model_paths.remove(path)
        if path == last_model:
            set_last_model(model_paths[0] if model_paths else None)
        save_models(model_paths, last_model)
        return True
    return False


def get_last_model() -> Optional[str]:
    """Return the last selected model path."""
    return last_model


def set_last_model(path: str | None) -> None:
    """Persist ``path`` as the last selected model."""
    global last_model
    last_model = path
    save_models(model_paths, last_model)


def get_info() -> dict:
    """Return module metadata for discovery."""
    return {
        "name": MODULE_NAME,
        "description": get_description(),
        "functions": [
            "load_models",
            "save_models",
            "add_model",
            "remove_model",
            "get_last_model",
            "set_last_model",
        ],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Manage saved LLM model paths."


# Initialize on import
load_models()
