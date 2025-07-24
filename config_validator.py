"""Configuration validation using jsonschema."""

try:
    from jsonschema import Draft7Validator  # type: ignore
except Exception:  # jsonschema may be missing
    Draft7Validator = None  # type: ignore


CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "tts_model": {"type": "string"},
        "tts_voice": {"type": ["string", "null"]},
        "tts_volume": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "tts_speed": {"type": "number", "minimum": 0.5, "maximum": 2.0},
        "use_voice": {"type": "boolean"},
        "prefer_local_llm": {
            "oneOf": [
                {"type": "boolean"},
                {"type": "string", "enum": ["auto"]},
            ]
        },
        "llm_backend": {"type": "string"},
        "llm_model": {"type": "string"},
        "vosk_model_path": {"type": "string"},
        "memory_max": {"type": "number"},
        "auto_memory_increase": {"type": "boolean"},
        "enable_plugins": {"type": "boolean"},
        "wake_phrases": {"type": "array", "items": {"type": "string"}},
        "sleep_phrases": {"type": "array", "items": {"type": "string"}},
        "cancel_phrases": {"type": "array", "items": {"type": "string"}},
        "resume_phrases": {"type": "array", "items": {"type": "string"}},
        "mic_overlay": {"type": "boolean"},
        "mic_overlay_colors": {
            "type": "object",
            "properties": {
                "listening": {"type": "string"},
                "sleeping": {"type": "string"},
                "muted": {"type": "string"},
            },
            "required": ["listening", "sleeping", "muted"],
        },
        "startup_message": {"type": "string"},
        "tips": {"type": "array", "items": {"type": "string"}},
        "hotword": {"type": "string"},
        "enable_hotword": {"type": "boolean"},
        "pause_threshold": {"type": "number"},
        "max_speech_length": {"type": "number"},
        "auto_sleep_timeout": {"type": "number"},
        "voice_beep": {"type": "boolean"},
        "log_level": {"type": "string"},
        "enable_advanced_logging": {"type": "boolean"},
        "busy_timeout": {"type": "number"},
        "home_assistant_url": {"type": "string"},
        "home_assistant_token": {"type": "string"},
        "enable_home_assistant": {"type": "boolean"},
        "min_good_response_words": {"type": "number"},
        "min_good_response_chars": {"type": "number"},
    },
    "required": ["tts_model", "vosk_model_path"],
}


def validate_config(config):
    """Validate configuration dictionary against :data:`CONFIG_SCHEMA`."""
    if Draft7Validator is None:
        # jsonschema not installed; skip validation
        return []
    validator = Draft7Validator(CONFIG_SCHEMA)
    errors = []
    for err in sorted(validator.iter_errors(config), key=lambda e: e.path):
        errors.append(err.message)
    return errors

