# modules/vosk_integration.py

try:
    import vosk
    import sounddevice as sd
    import queue
    import json
    import os
except ImportError as e:
    _IMPORT_ERROR = str(e)
else:
    _IMPORT_ERROR = None

from error_logger import log_error

MODULE_NAME = "vosk_integration"

__all__ = ["recognize_from_mic"]

def load_config(path: str = "config.json") -> dict:
    """Return dictionary from ``path`` or empty dict on failure."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Config load error: {e}")
        return {}

def load_vosk_model(model_path: str | None = None):
    """Load a Vosk model from ``model_path`` or config."""
    if _IMPORT_ERROR:
        raise ImportError(_IMPORT_ERROR)
    config = load_config()
    if model_path is None:
        model_path = config.get("vosk_model_path")
    if not model_path or not os.path.exists(model_path):
        raise FileNotFoundError(f"Vosk model not found at {model_path}")
    return vosk.Model(model_path)

def recognize_from_mic(
    model=None, duration: int = 5, samplerate: int = 16000
) -> str:
    """Return transcribed text from microphone using Vosk."""
    if _IMPORT_ERROR:
        return f"[{MODULE_NAME} Error] {str(_IMPORT_ERROR)}"
    try:
        if model is None:
            model = load_vosk_model()
        q = queue.Queue()
        result = ""
        def callback(indata, frames, time, status):
            q.put(bytes(indata))
        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16', channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(model, samplerate)
            print(f"Listening ({duration} sec)...")
            sd.sleep(duration * 1000)
            while not q.empty():
                data = q.get()
                if rec.AcceptWaveform(data):
                    part = json.loads(rec.Result())
                    result += part.get("text", "") + " "
            final = json.loads(rec.FinalResult())
            result += final.get("text", "")
        return result.strip()
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Recognition error: {e}")
        return f"[{MODULE_NAME} Error] {str(e)}"

def get_info():
    return {
        "name": MODULE_NAME,
        "description": "Offline speech recognition using Vosk and sounddevice.",
        "functions": ["recognize_from_mic"]
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Simple Vosk-based offline speech recognition helper functions."

def register(registry=None):
    """Register this module with ``ModuleRegistry``."""
    from module_manager import ModuleRegistry

    registry = registry or ModuleRegistry()
    registry.register(
        MODULE_NAME,
        {
            "recognize_from_mic": recognize_from_mic,
            "get_info": get_info,
        },
    )

# Optionally auto-register
# register()
