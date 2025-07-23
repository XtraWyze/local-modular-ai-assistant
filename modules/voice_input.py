# voice_input.py

import time
import threading
import json
from error_logger import log_error
try:
    import speech_recognition as sr
    from vosk import Model, KaldiRecognizer
    import pyaudio
except Exception as e:  # pragma: no cover - optional dependencies
    sr = None
    Model = None
    KaldiRecognizer = None
    pyaudio = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

CONFIG_PATH = "config.json"
try:
    with open(CONFIG_PATH, "r") as f:
        _CFG = json.load(f)
except Exception:
    _CFG = {}

# Configurable parameters
PAUSE_THRESHOLD = _CFG.get("pause_threshold", 2.0)
MAX_SPEECH_LENGTH = _CFG.get("max_speech_length", 30)
AUTO_SLEEP_TIMEOUT = _CFG.get("auto_sleep_timeout", 15)
ENABLE_BEEP = _CFG.get("voice_beep", False)
CANCEL_PHRASES = [p.lower() for p in _CFG.get("cancel_phrases", ["stop assistant"])]
SOFT_MUTE_SECS = 3
STT_BACKEND = _CFG.get("stt_backend", "google")  # "google" or "vosk"

__all__ = [
    "start_voice_listener",
    "listen",
    "start_hotword",
    "stop_hotword",
    "mute_hotword",
    "unmute_hotword",
]

from assistant import (
    check_sleep,
    check_wake,
    is_listening,
    speak,
    process_input,
    set_listening,
    cancel_processing,
)
from modules.tts_manager import is_speaking, stop_speech

# Track last time we heard any speech
last_activity_time = time.time()

# Globals used when the hotword listener is started via start_hotword()
_hotword_thread = None
_hotword_stop = None
_hotword_muted = False
_hotword_muted_until = 0.0

def mute_hotword(duration=SOFT_MUTE_SECS):
    """Temporarily mute wake word detection."""
    global _hotword_muted, _hotword_muted_until
    _hotword_muted = True
    _hotword_muted_until = time.time() + duration

def unmute_hotword():
    """Resume wake word detection."""
    global _hotword_muted, _hotword_muted_until
    _hotword_muted = False
    _hotword_muted_until = 0.0

def _beep():
    """Play a short beep if enabled."""
    if not ENABLE_BEEP:
        return
    try:
        import winsound
        winsound.Beep(1000, 150)
    except Exception:
        # Fallback to console bell
        print("\a", end="", flush=True)

def start_voice_listener(output_widget, vosk_model_path, mic_hard_muted_func, stop_event=None):
    """Unified loop for wake-word detection and speech recognition."""
    if _IMPORT_ERROR:
        return f"Missing dependency: {_IMPORT_ERROR}"

    # Hotword detection setup
    model = Model(vosk_model_path)
    rec = KaldiRecognizer(model, 16000)
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8000,
    )
    stream.start_stream()

    # Speech recognition setup
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = PAUSE_THRESHOLD
    mic = sr.Microphone()


    global last_activity_time
    was_listening = False

    try:
        while True:
            if stop_event and stop_event.is_set():
                break
            if mic_hard_muted_func():
                time.sleep(0.5)
                continue

            if is_speaking():
                if not _hotword_muted:
                    mute_hotword()
                    output_widget.insert("end", "Assistant: 🔇 Hotword paused.\n")
                    output_widget.see("end")
            elif _hotword_muted and time.time() > _hotword_muted_until:
                unmute_hotword()
                output_widget.insert("end", "Assistant: 🎤 Hotword resumed.\n")
                output_widget.see("end")

            data = stream.read(4000, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = rec.Result().lower()

                if any(p in result for p in CANCEL_PHRASES):
                    stop_speech()
                    cancel_processing()
                    unmute_hotword()
                    output_widget.insert("end", "Assistant: ⛔ Cancelled.\n")
                    output_widget.see("end")
                    continue

                if not is_listening() and not _hotword_muted and check_wake(result):
                    output_widget.insert("end", "Assistant: 🟢 Wake phrase detected!\n")
                    output_widget.see("end")
                    _beep()
                    mute_hotword()
                    speak("Yes?", on_complete=unmute_hotword)
                    last_activity_time = time.time()
                    continue

            listening = is_listening()

            if listening and not was_listening:
                _beep()
                last_activity_time = time.time()
            elif not listening and was_listening:
                _beep()
            was_listening = listening

            if listening:
                if time.time() - last_activity_time > AUTO_SLEEP_TIMEOUT:
                    speak("Going to sleep due to inactivity.")
                    output_widget.insert("end", "Assistant: 😴 Auto-sleeping after silence.\n")
                    output_widget.see("end")
                    set_listening(False)
                    _beep()
                    continue

                with mic as source:
                    recognizer.adjust_for_ambient_noise(source)
                    try:
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=MAX_SPEECH_LENGTH)
                    except sr.WaitTimeoutError:
                        continue

                try:
                    if STT_BACKEND == "google":
                        text = recognizer.recognize_google(audio)
                    else:
                        from modules.vosk_integration import recognize_from_mic
                        text = recognize_from_mic()
                except Exception as e:
                    log_error(f"[Mic Error] {e}")
                    continue

                last_activity_time = time.time()

                if check_sleep(text):
                    speak("Going to sleep. Say 'Hey Assistant' to wake me up.")
                    output_widget.insert("end", "Assistant: 😴 Going to sleep. Say 'Hey Assistant' to wake up.\n")
                    output_widget.see("end")
                    set_listening(False)
                    _beep()
                    continue

                if any(p in text.lower() for p in CANCEL_PHRASES):
                    stop_speech()
                    cancel_processing()
                    unmute_hotword()
                    output_widget.insert("end", "Assistant: ⛔ Cancelled.\n")
                    output_widget.see("end")
                    continue

                output_widget.insert("end", f"You (voice): {text}\n")
                output_widget.see("end")
                threading.Thread(target=process_input, args=(text, output_widget), daemon=True).start()
            else:
                time.sleep(0.1)
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

# Simple wrappers used by get_info for discovery
def listen(output_widget, vosk_model_path, mic_hard_muted_func):
    """Start the unified voice listener in a background thread."""
    if _IMPORT_ERROR:
        return f"Missing dependency: {_IMPORT_ERROR}"
    threading.Thread(
        target=start_voice_listener,
        args=(output_widget, vosk_model_path, mic_hard_muted_func),
        daemon=True,
    ).start()
    return "Voice listener started"

def start_hotword(output_widget, vosk_model_path, mic_hard_muted_func):
    """Start the unified voice listener in its own thread."""
    global _hotword_thread, _hotword_stop
    if _hotword_thread and _hotword_thread.is_alive():
        return "Hotword listener already running"
    if _IMPORT_ERROR:
        return f"Missing dependency: {_IMPORT_ERROR}"

    _hotword_stop = threading.Event()
    _hotword_thread = threading.Thread(
        target=start_voice_listener,
        args=(output_widget, vosk_model_path, mic_hard_muted_func, _hotword_stop),
        daemon=True,
    )
    _hotword_thread.start()
    return "Hotword listener started"

def stop_hotword():
    """Stop the hotword listener started via :func:`start_hotword`."""
    global _hotword_thread, _hotword_stop

    if _hotword_stop:
        _hotword_stop.set()
    if _hotword_thread:
        _hotword_thread.join()
        _hotword_thread = None
        _hotword_stop = None

    return "Hotword listener stopped"

def get_info():
    return {
        "name": "voice_input",
        "description": "Handles all voice input, hotword detection, and microphone streaming.",
        "functions": [
            "listen",
            "start_voice_listener",
            "start_hotword",
            "stop_hotword",
            "mute_hotword",
            "unmute_hotword",
        ]
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Provides wake-word detection and streaming microphone input for commands."
