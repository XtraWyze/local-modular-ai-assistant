import os
import json
from error_logger import log_error, log_info
try:
    import numpy as np
except ImportError:  # pragma: no cover - fallback for minimal environments
    class _SimpleNumpy:
        class ndarray(list):
            """Minimal stand-in for ``numpy.ndarray`` when NumPy is unavailable."""
            pass

        @staticmethod
        def array(x):
            return _SimpleNumpy.ndarray(x)

        @staticmethod
        def dot(a, b):
            return sum(x * y for x, y in zip(a, b))

        class linalg:
            @staticmethod
            def norm(x, axis=None):
                if axis is None:
                    return (sum(i * i for i in x)) ** 0.5
                return [(sum(i * i for i in row)) ** 0.5 for row in x]

        @staticmethod
        def argsort(seq):
            return sorted(range(len(seq)), key=lambda i: seq[i])

    np = _SimpleNumpy()
from config_loader import ConfigLoader

# Ensure the 'modules' package can be imported even if the working directory
# isn't the project root. This commonly happens on Windows when launching the
# application via shortcuts or different shells.
try:
    from modules.utils import resource_path
except ModuleNotFoundError:  # pragma: no cover - runtime safeguard
    import sys

    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from modules.utils import resource_path

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - minimal fallback
    class SentenceTransformer:
        """Very small fallback embedding model used when ``sentence-transformers`` is missing."""

        def __init__(self, *_, **__):
            pass

        def encode(self, texts):
            # Basic character-level embedding to keep shapes consistent
            return [[float(ord(c)) for c in t[:10]] for t in texts]

MODEL_NAME = "all-MiniLM-L6-v2"
# Persistent memory is stored in a JSON file.
MEMORY_FILE = resource_path("assistant_memory.json")

_model = None

def get_model():
    """Lazily create and return the embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

# Holds: {"texts": [...], "vectors": [[...], ...]}
memory = {"texts": [], "vectors": []}

# Load configuration for memory limits
_config_loader = ConfigLoader()
MEMORY_MAX = _config_loader.config.get("memory_max", 500)
# Optional auto expansion when memory reaches the limit
AUTO_MEMORY_INCREASE = _config_loader.config.get("auto_memory_increase", True)

def save_memory(mem=memory):
    # Convert all np.ndarray vectors to lists before saving as JSON
    safe_mem = dict(mem)  # shallow copy
    safe_mem["vectors"] = [v.tolist() if isinstance(v, np.ndarray) else v for v in mem["vectors"]]
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(safe_mem, f)

def prune_memory(max_entries=MEMORY_MAX):
    """Truncate memory to the most recent `max_entries` messages."""
    if len(memory["texts"]) <= max_entries:
        return
    excess = len(memory["texts"]) - max_entries
    # Drop oldest items
    memory["texts"] = memory["texts"][excess:]
    memory["vectors"] = memory["vectors"][excess:]

def maybe_expand_memory():
    """Increase ``MEMORY_MAX`` if auto expansion is enabled."""
    global MEMORY_MAX
    if not AUTO_MEMORY_INCREASE:
        return False
    if len(memory["texts"]) <= MEMORY_MAX:
        return False
    new_limit = int(MEMORY_MAX * 1.5)
    if new_limit <= MEMORY_MAX:
        new_limit = MEMORY_MAX + 1
    MEMORY_MAX = new_limit
    log_info(f"[memory_manager] Increased MEMORY_MAX to {MEMORY_MAX}")
    return True

def load_memory():
    global memory
    if os.path.isfile(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                memory = json.load(f)
            # Ensure vectors are np.arrays for computation
            memory["vectors"] = [np.array(v) for v in memory.get("vectors", [])]
            memory.setdefault("texts", [])
        except Exception as e:  # pragma: no cover - corrupted file
            log_error(f"[memory_manager] Failed to load memory: {e}")
            memory = {"texts": [], "vectors": []}
    else:
        memory = {"texts": [], "vectors": []}
    return memory

def store_memory(text, response=None):
    if response:
        pair = f"Q: {text}\nA: {response}"
    else:
        pair = text
    vector = get_model().encode([pair])[0]
    memory["texts"].append(pair)
    # Keep numpy arrays in memory; save_memory will convert to lists when needed
    memory["vectors"].append(vector)
    if len(memory["texts"]) > MEMORY_MAX:
        if not maybe_expand_memory():
            prune_memory(MEMORY_MAX)
    save_memory(memory)

def search_memory(query, top_k=5):
    if not memory["texts"]:
        return []
    q_vec = get_model().encode([query])[0]
    vectors = np.array(memory["vectors"])
    sims = np.dot(vectors, q_vec) / (np.linalg.norm(vectors, axis=1) * np.linalg.norm(q_vec) + 1e-8)
    # Get top K
    idxs = np.argsort(sims)[::-1][:top_k]
    results = [f"{memory['texts'][i]} (score={sims[i]:.2f})" for i in idxs]
    return results

# Auto-load at import
load_memory()
maybe_expand_memory()
prune_memory(MEMORY_MAX)
