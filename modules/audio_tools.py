"""Audio capture utilities for speaker output."""

MODULE_NAME = "audio_tools"

try:
    import sys
    import numpy as _np
    import pyaudio
except Exception as e:
    pyaudio = None
    _IMPORT_ERROR = str(e)
else:
    _IMPORT_ERROR = None

try:
    import sounddevice as _sd
except Exception:
    _sd = None

from error_logger import log_error

__all__ = ["transcribe_speaker", "detect_sound"]


def _record_speaker(duration=5, samplerate=16000):
    """Capture audio from the system speakers for the given duration.

    Returns a tuple of (raw_bytes, sample_rate) or (None, None) on error.
    """
    if _IMPORT_ERROR and _sd is None:
        log_error(f"[{MODULE_NAME}] Missing dependencies: {_IMPORT_ERROR}")
        return None, None

    if _sd is not None:
        try:
            loopback = None
            try:
                if hasattr(_sd, "WasapiSettings"):
                    loopback = _sd.WasapiSettings(loopback=True)
            except Exception:
                loopback = None
            device = None
            try:
                device = _sd.default.device[1]
            except Exception:
                pass
            with _sd.InputStream(
                samplerate=samplerate,
                channels=2,
                dtype="int16",
                blocksize=1024,
                device=device,
                extra_settings=loopback,
            ) as stream:
                data = stream.read(int(duration * samplerate))[0]
                return data.tobytes(), samplerate
        except Exception as e:
            log_error(f"[{MODULE_NAME}] sounddevice capture error: {e}")

    if pyaudio is not None:
        try:
            pa = pyaudio.PyAudio()
            stream = None
            if sys.platform.startswith("win") and hasattr(pyaudio, "paWASAPI"):
                try:
                    host_index = pa.get_host_api_info_by_type(pyaudio.paWASAPI)["index"]
                    device_index = pa.get_host_api_info_by_type(pyaudio.paWASAPI)["defaultOutputDevice"]
                    stream = pa.open(
                        format=pyaudio.paInt16,
                        channels=2,
                        rate=samplerate,
                        frames_per_buffer=1024,
                        input=True,
                        input_device_index=device_index,
                        as_loopback=True,
                    )
                except Exception:
                    stream = None
            if stream is None:
                device_index = pa.get_default_input_device_info()["index"]
                stream = pa.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=samplerate,
                    frames_per_buffer=1024,
                    input=True,
                    input_device_index=device_index,
                )
            frames = []
            for _ in range(int(samplerate / 1024 * duration)):
                frames.append(stream.read(1024))
            stream.stop_stream()
            stream.close()
            pa.terminate()
            return b"".join(frames), samplerate
        except Exception as e:
            log_error(f"[{MODULE_NAME}] pyaudio capture error: {e}")
    return None, None


def detect_sound(threshold=500, duration=2):
    """Return True if speaker audio exceeds threshold during duration."""
    data, rate = _record_speaker(duration, samplerate=16000)
    if data is None:
        return False
    try:
        arr = _np.frombuffer(data, dtype=_np.int16)
        rms = _np.sqrt(_np.mean(arr.astype(_np.float32) ** 2))
        return rms > threshold
    except Exception as e:
        log_error(f"[{MODULE_NAME}] detect_sound error: {e}")
        return False


def transcribe_speaker(duration=5):
    """Record speaker output and transcribe using SpeechRecognition."""
    data, rate = _record_speaker(duration, samplerate=16000)
    if data is None:
        return ""
    try:
        import speech_recognition as sr
    except Exception as e:
        log_error(f"[{MODULE_NAME}] speech_recognition import error: {e}")
        return ""
    recognizer = sr.Recognizer()
    audio = sr.AudioData(data, rate, 2)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        log_error(f"[{MODULE_NAME}] transcription error: {e}")
        return ""


def get_info():
    return {
        "name": MODULE_NAME,
        "description": "Capture speaker output and provide simple sound detection or transcription.",
        "functions": ["transcribe_speaker", "detect_sound"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Capture system audio to detect sounds or transcribe speech."


def register():
    """Register this module with ``ModuleRegistry``."""
    from module_manager import ModuleRegistry

    ModuleRegistry.register(
        MODULE_NAME,
        {
            "transcribe_speaker": transcribe_speaker,
            "detect_sound": detect_sound,
            "get_info": get_info,
        },
    )

# register()
