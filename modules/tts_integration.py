# modules/tts_integration.py

try:
    import json
    import threading
    import time
    import numpy as np
    import sounddevice as sd
    from TTS.api import TTS
except ImportError as e:
    _IMPORT_ERROR = str(e)
else:
    _IMPORT_ERROR = None

from error_logger import log_error
from .utils import chunk_text
from . import gpu

CONFIG_PATH = "config.json"
DEFAULTS = {
    "tts_model": "tts_models/en/vctk/vits",
    "tts_voice": None,
    "tts_volume": 0.8,
    "tts_speed": 1.0,
}

# A curated list of working Coqui models for quick switching. Users may add
# their own model names to ``config.json`` if desired.
AVAILABLE_MODELS = [
    "tts_models/en/jenny/jenny",
    "tts_models/en/vctk/vits",
    "tts_models/en/ljspeech/tacotron2-DDC",
]
MODULE_NAME = "tts_integration"

__all__ = [
    "speak",
    "list_voices",
    "list_models",
    "set_voice",
    "set_model",
    "set_volume",
    "set_speed",
    "is_speaking",
    "stop_speech",
]

def load_config() -> dict:
    """Return configuration dictionary combining defaults and ``config.json``."""
    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Could not load config.json: {e}")
        cfg = {}
    return {**DEFAULTS, **cfg}

config = load_config()
_model = None
_speaking = False

def get_tts_model():
    """Lazy-load and return the configured TTS model."""
    if _IMPORT_ERROR:
        raise ImportError(_IMPORT_ERROR)
    global _model
    if _model is None:
        print(f"[TTS] Loading Coqui model: {config['tts_model']}")
        _model = TTS(
            model_name=config["tts_model"],
            progress_bar=False,
            gpu=gpu.is_available(),
        )
    return _model

def speak(text, voice=None, volume=None, speed=None, async_play=True, on_complete=None):
    """Speak text using Coqui TTS.

    Parameters
    ----------
    text : str
        Text to be spoken.
    voice : str, optional
        Desired speaker voice.
    volume : float, optional
        Playback volume multiplier.
    speed : float, optional
        Playback rate multiplier. Defaults to ``config['tts_speed']`` if ``None``.
    async_play : bool, optional
        When ``True`` the audio is played in a background thread.
    """
    if _IMPORT_ERROR:
        msg = f"[{MODULE_NAME}] Missing dependency: {_IMPORT_ERROR}"
        log_error(msg)
        return msg

    # Enforce a single unified voice profile from config
    voice = config.get("tts_voice") or voice
    volume = volume if volume is not None else config.get("tts_volume", 0.8)
    model = get_tts_model()
    if speed is None:
        speed = config.get("tts_speed", 1.0)
    chunks = chunk_text(text)

    def run():
        try:
            start = time.time()
            wav = []
            sample_rate = None
            total_duration = 0.0
            for part in chunks:
                part_wav = model.tts(part, speaker=voice) if voice else model.tts(part)
                part_wav = np.array(part_wav) * float(volume)
                if sample_rate is None:
                    sample_rate = model.synthesizer.output_sample_rate
                total_duration += len(part_wav) / sample_rate
                wav.extend(part_wav)
            wav = np.array(wav)
            rate = float(speed)
            global _speaking
            _speaking = True
            sd.play(wav, int(sample_rate * rate))
            sd.wait()
            proc_time = time.time() - start
            rtf = proc_time / total_duration if total_duration else 0
            print(f"Processing time: {proc_time:.2f}s")
            print(f"Real-time factor: {rtf:.2f}")
            if len(chunks) > 1:
                print("Text splitted to sentences.")
            if on_complete:
                try:
                    on_complete()
                except Exception as e:
                    log_error(f"[{MODULE_NAME}] on_complete error: {e}")
            _speaking = False
        except Exception as e:
            log_error(f"[{MODULE_NAME}] TTS/playback error: {e}")

    if async_play:
        threading.Thread(target=run, daemon=True).start()
        return "[TTS] Speaking asynchronously."
    else:
        run()
        return "[TTS] Done speaking."

def is_speaking() -> bool:
    """Return True while audio is currently playing."""
    return _speaking

def stop_speech():
    """Immediately stop any ongoing playback."""
    if _IMPORT_ERROR:
        return
    try:
        sd.stop()
    except Exception as e:  # pragma: no cover - stop may fail if not playing
        log_error(f"[{MODULE_NAME}] stop error: {e}")
    finally:
        global _speaking
        _speaking = False

def list_voices():
    """Return a list of available speakers for the current model."""
    if _IMPORT_ERROR:
        msg = f"[{MODULE_NAME}] Missing dependency: {_IMPORT_ERROR}"
        log_error(msg)
        return msg
    model = get_tts_model()
    if hasattr(model, "speakers") and model.speakers:
        return model.speakers
    return ["default"]

def list_models():
    """Return a list of recommended model names."""
    return AVAILABLE_MODELS

def set_voice(new_voice):
    """Set and save the preferred voice."""
    config["tts_voice"] = new_voice
    try:
        with open(CONFIG_PATH, "r") as f:
            all_cfg = json.load(f)
        all_cfg["tts_voice"] = new_voice
        with open(CONFIG_PATH, "w") as f:
            json.dump(all_cfg, f, indent=2)
        print(f"[TTS] Voice switched to: {new_voice}")
        return True
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Could not update config.json: {e}")
        return False

def set_model(new_model):
    """Set and save the TTS model name."""
    config["tts_model"] = new_model
    try:
        with open(CONFIG_PATH, "r") as f:
            all_cfg = json.load(f)
        all_cfg["tts_model"] = new_model
        with open(CONFIG_PATH, "w") as f:
            json.dump(all_cfg, f, indent=2)
        # Force model reload on next speak()
        global _model
        _model = None
        print(f"[TTS] Model switched to: {new_model}")
        return True
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Could not update config.json: {e}")
        return False

def set_volume(new_volume):
    """Set and save the preferred volume (0.0 - 1.0)."""
    try:
        vol = float(new_volume)
        assert 0.0 <= vol <= 1.0
    except Exception:
        msg = "[TTS] Volume must be a number between 0.0 and 1.0"
        log_error(msg)
        return msg
    config["tts_volume"] = vol
    try:
        with open(CONFIG_PATH, "r") as f:
            all_cfg = json.load(f)
        all_cfg["tts_volume"] = vol
        with open(CONFIG_PATH, "w") as f:
            json.dump(all_cfg, f, indent=2)
        print(f"[TTS] Volume set to: {vol}")
        return True
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Could not update config.json: {e}")
        return False

def set_speed(new_speed):
    """Set and save the preferred speech speed (0.5 - 2.0)."""
    try:
        val = float(new_speed)
        assert 0.5 <= val <= 2.0
    except Exception:
        msg = "[TTS] Speed must be a number between 0.5 and 2.0"
        log_error(msg)
        return False
    config["tts_speed"] = val
    try:
        with open(CONFIG_PATH, "r") as f:
            all_cfg = json.load(f)
        all_cfg["tts_speed"] = val
        with open(CONFIG_PATH, "w") as f:
            json.dump(all_cfg, f, indent=2)
        print(f"[TTS] Speed set to: {val}")
        return True
    except Exception as e:
        log_error(f"[{MODULE_NAME}] Could not update config.json: {e}")
        return False

def get_info():
    """Plugin info for registry."""
    return {
        "name": MODULE_NAME,
        "description": "Offline text-to-speech using Coqui TTS and sounddevice.",
        "functions": [
            "speak",
            "list_voices",
            "list_models",
            "set_voice",
            "set_model",
            "set_volume",
            "set_speed",
            "is_speaking",
            "stop_speech",
        ]
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Provides offline text-to-speech playback using Coqui TTS."

def register():
    """Register with assistant plugin system."""
    from module_manager import ModuleRegistry
    ModuleRegistry.register(MODULE_NAME, {
        "speak": speak,
        "list_voices": list_voices,
        "list_models": list_models,
        "set_voice": set_voice,
        "set_model": set_model,
        "set_volume": set_volume,
        "set_speed": set_speed,
        "is_speaking": is_speaking,
        "stop_speech": stop_speech,
        "get_info": get_info
    })

# Optionally enable auto-registration if your loader supports it:
# register()

if __name__ == "__main__":
    print("[TTS] Available models:", list_models())
    print("[TTS] Available voices:", list_voices())
    print("[TTS] Speaking test message offline with Coqui.")
    speak("Hello! This is your assistant speaking using Coqui TTS.", async_play=False)
