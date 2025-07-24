import json
import threading
import time
import os

try:
    import keyboard
except Exception:  # keyboard module optional
    keyboard = None
try:
    import pyautogui
except Exception:
    pyautogui = None
import inspect
import importlib
import re

from modules.actions import detect_action
from modules.tts_manager import speak, is_speaking, stop_speech
from modules import window_tools, vision_tools
from modules.automation_learning import record_macro, play_macro
from modules.desktop_shortcuts import build_shortcut_map, open_shortcut
from modules.chitchat import is_chitchat, talk_to_llm
import planning_agent
import remote_agent
from state_manager import (
    update_state,
    register_action,
    get_action,
    state as state_dict,
    save_state,
    add_resume_phrase,
    get_resume_phrases,
)

from error_logger import log_error
from memory_manager import save_memory, load_memory, store_memory, search_memory
from modules.long_term_storage import save_entry
import llm_interface
from llm_interface import generate_response
from module_manager import ModuleRegistry
from config_loader import ConfigLoader
from config_validator import validate_config
import scan_registry

config_loader = ConfigLoader()
config = config_loader.config
BUSY_TIMEOUT = config.get("busy_timeout", 60)

# Ensure long term memory DB is ready
try:
    from modules.long_term_storage import initialize as _init_ltm

    _init_ltm()
except Exception as e:  # pragma: no cover - optional dependency
    log_error(f"[assistant] long_term_storage init failed: {e}")

# Validate config after loading
errors = validate_config(config)
if errors:
    print("[CONFIG VALIDATION] Problems found:")
    for err in errors:
        print(" -", err)
    import sys


    sys.exit(1)

scan_registry.initialize()

# Central state of the assistant: "idle" or "processing"
assistant_state = "idle"
pending_commands: list[tuple[str, any]] = []
listening_before_processing = True

# Event used to signal a cancellation request
cancel_event = threading.Event()

# Legacy variables for compatibility
assistant_busy = False  # will mirror assistant_state
last_user_command = ""
last_ai_response = ""

# Directory where recorded macros will be stored
MACRO_DIR = "macros"

# Callback for GUI screen viewer
screen_viewer_callback = lambda: None

def set_screen_viewer_callback(func):
    """Register GUI hook to open the screen viewer window."""
    global screen_viewer_callback
    screen_viewer_callback = func

# Instance of RemoteServer when started via command
remote_srv: remote_agent.RemoteServer | None = None


def set_state(state: str) -> None:
    """Set the assistant's state and mirror the legacy flag."""
    global assistant_state, assistant_busy
    assistant_state = state
    assistant_busy = state == "processing"


def get_state() -> str:
    """Return the current assistant state."""
    return assistant_state


def queue_command(text: str, widget) -> None:
    """Store a command to be processed once the assistant is idle."""
    pending_commands.append((text, widget))


def cancel_processing() -> None:
    """Abort current work and clear the queue."""
    cancel_event.set()
    pending_commands.clear()
    set_state("idle")


def _run_next_in_queue():
    """Process the next queued command or announce readiness only when TTS is idle."""

    def _do_next():
        if pending_commands:
            text, widget = pending_commands.pop(0)
            process_input(text, widget)
        else:
            print("*>")

    if is_speaking():

        def _wait_then_run():
            start = time.time()
            while is_speaking():
                time.sleep(0.05)
            print(
                f"[assistant] Waited {time.time() - start:.2f}s for TTS to finish before idle prompt."
            )
            _do_next()

        threading.Thread(target=_wait_then_run, daemon=True).start()
    else:
        _do_next()


def list_capabilities():
    """Return a description of available modules and examples."""
    registry = ModuleRegistry()
    registry.auto_discover("modules")
    lines = ["I can perform these actions locally:"]
    for mod in registry.modules.values():
        if hasattr(mod, "get_info"):
            info = mod.get_info()
            desc = info.get("description", "")
            funcs = ", ".join(info.get("functions", []))
            lines.append(f"- {info.get('name')}: {desc} (functions: {funcs})")
    lines.append("\nExamples:")
    lines.append("- record <name> : record a new macro")
    lines.append("- play macro <name> : run a saved macro")
    lines.append("- capture region x y w h : OCR part of the screen")
    lines.append("- recall <keyword> : search memory")
    return "\n".join(lines)


def list_module_descriptions() -> str:
    """Discover modules and return their descriptions."""
    registry = ModuleRegistry()
    registry.auto_discover("modules")
    lines = []
    for name, mod in registry.modules.items():
        desc = ""
        if hasattr(mod, "get_description"):
            try:
                desc = mod.get_description()
            except Exception as e:  # pragma: no cover - log but continue
                log_error(f"[help] {name}.get_description failed: {e}")
        if not desc and hasattr(mod, "get_info"):
            try:
                desc = mod.get_info().get("description", "")
            except Exception as e:  # pragma: no cover - log but continue
                log_error(f"[help] {name}.get_info failed: {e}")
        if desc:
            lines.append(f"- {name}: {desc}")
    lines.sort()
    return "\n".join(lines)


def get_capabilities_summary() -> str:
    """Return a short, human-readable summary of features from ``README.md``."""
    try:
        capture = False
        bullet_lines = []
        with open("README.md", "r", encoding="utf-8") as f:
            for line in f:
                text = line.strip()
                if text == "## ✨ Features":
                    capture = True
                    continue
                if capture:
                    if text.startswith("## ") or text.startswith("---"):
                        break
                    if text:
                        if text.startswith("-"):
                            bullet_lines.append(text[1:].strip().strip("*"))
        if bullet_lines:
            bullets = "\n".join(f"- {b}" for b in bullet_lines)
            return "Here's a quick overview of what I can do:\n" + bullets
    except Exception as e:  # pragma: no cover - file read should succeed
        log_error(f"Capability summary failed: {e}")
    return "See the README for a list of features."


def get_trigger_words_summary() -> str:
    """Return trigger words for each module."""
    try:
        from modules import trigger_words

        trig = trigger_words.get_trigger_words()
        lines = ["Trigger words for quick commands:"]
        for mod, words in sorted(trig.items()):
            lines.append(f"- {mod}: {', '.join(words)}")
        return "\n".join(lines)
    except Exception as e:  # pragma: no cover - optional module errors
        log_error(f"Trigger word summary failed: {e}")
        return "Trigger words unavailable"


def process_input(user_input, output_widget):
    """Main entry point for user commands from the GUI.

    The function coordinates wake/sleep logic, tutorial mode detection,
    shortcut handling and finally falls back to the LLM or orchestrator.  All
    responses are written to ``output_widget`` and voiced using :func:`speak`.
    """

    global last_user_command, last_ai_response
    cancel_event.clear()

    text = user_input.strip()
    last_user_command = text

    if assistant_state == "processing":
        speak(
            "I'm still processing your previous request but will follow up as soon as it's complete."
        )
        output_widget.insert("end", f"[Queued] {text}\n")
        output_widget.see("end")
        queue_command(text, output_widget)
        return
    set_state("processing")
    global listening_before_processing
    # Save the current listening state before processing
    was_listening = listening_before_processing

    listening_before_processing = is_listening()
    pending_commands.clear()
    set_listening(False)
    speak("Give me a moment...", speed=1.0)

    try:
        from modules import system_load  # optional module
    except Exception:  # pragma: no cover - module may be missing
        system_load = None
    else:
        if system_load.is_overloaded():
            output_widget.insert(
                "end", "Assistant: System overloaded, waiting...\n"
            )
            output_widget.see("end")
            speak("System is busy, waiting for resources.")
            system_load.wait_for_load()

    result = [None]
    exception_caught = [None]

    def task():
        global remote_srv
        try:
            if cancel_event.is_set():
                return
            # === Sleep/Wake logic ===
            if not was_listening:
                if check_wake(text):
                    speak("I'm awake!")
                    output_widget.insert("end", "Assistant: 🟢 Assistant woke up.\n")
                    output_widget.see("end")
                return
            if was_listening and check_sleep(text):
                speak("Going to sleep. Say 'Hey Assistant' to wake me up.", speed=1.0)
                output_widget.insert("end", "Assistant: 🟡 Assistant is sleeping.\n")
                output_widget.see("end")
                return

            # === Speech speed commands ===
            m = re.search(
                r"set (?:speech|voice) speed to ([0-9]*\.?[0-9]+)", text.lower()
            )
            if m:
                val = float(m.group(1))
                from modules import tts_integration

                ok = tts_integration.set_speed(val)
                msg = (
                    f"Speech speed set to {val}"
                    if ok
                    else "Invalid speed. Use 0.5 to 2.0"
                )
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return
            if "slow down your voice" in text.lower():
                from modules import tts_integration

                val = max(tts_integration.config.get("tts_speed", 1.0) - 0.1, 0.5)
                tts_integration.set_speed(val)
                msg = f"Speech speed set to {val}"
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            # === Volume commands ===
            m = re.search(
                r"set (?:speech |voice )?volume to ([0-9]*\.?[0-9]+)", text.lower()
            )
            if m:
                val = float(m.group(1))
                from modules import tts_integration

                ok = tts_integration.set_volume(val)
                msg = (
                    f"Volume set to {val}"
                    if ok is True
                    else "Invalid volume. Use 0.0 to 1.0"
                )
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return
            if "increase volume" in text.lower():
                from modules import tts_integration

                val = min(tts_integration.config.get("tts_volume", 0.8) + 0.1, 1.0)
                tts_integration.set_volume(val)
                msg = f"Volume set to {val}"
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return
            if "decrease volume" in text.lower() or "lower volume" in text.lower():
                from modules import tts_integration

                val = max(tts_integration.config.get("tts_volume", 0.8) - 0.1, 0.0)
                tts_integration.set_volume(val)
                msg = f"Volume set to {val}"
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            # === Media control commands ===
            txt_l = text.lower()
            if txt_l in ["pause music", "pause the music", "pause song", "pause playback"]:
                from modules import media_controls

                msg = media_controls.play_pause()
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            if txt_l in ["play music", "resume music", "play song", "start music"]:
                from modules import media_controls

                msg = media_controls.play_pause()
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            if txt_l in ["skip song", "skip track", "next song", "next track"]:
                from modules import media_controls

                msg = media_controls.next_track()
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            # === Voice selection ===
            m = re.search(r"(?:use|set|change) ([\w-]+) voice", text.lower())
            if m:
                voice = m.group(1)
                from modules import tts_integration

                ok = tts_integration.set_voice(voice)
                msg = f"Voice set to {voice}" if ok else "Voice not available"
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return
            if text.lower() in [
                "list voices",
                "what voices are available",
                "what voices do you have",
            ]:
                from modules import tts_integration

                voices = tts_integration.list_voices()
                msg = "Available voices: " + ", ".join(voices)
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            # === Scan registry commands ===
            lower = text.lower()
            if lower == "system scan":
                info = scan_registry.system_data.get("summary", "No data")
                output_widget.insert("end", f"Assistant: {info}\n")
                output_widget.see("end")
                speak(str(info))
                last_ai_response = str(info)
                result[0] = str(info)
                return
            if lower == "device scan":
                devices = ", ".join(scan_registry.device_data) or "No devices found"
                msg = f"Devices: {devices}"
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                result[0] = msg
                return
            if lower == "network scan":
                hosts = ", ".join(scan_registry.network_data) or "No hosts found"
                msg = f"Network hosts: {hosts}"
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                result[0] = msg
                return
            if lower == "refresh system scan":
                scan_registry.refresh_system()
                msg = "System scan refreshed."
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                result[0] = msg
                return
            if lower == "refresh device scan":
                scan_registry.refresh_devices()
                msg = "Device scan refreshed."
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                result[0] = msg
                return
            if lower == "refresh network scan":
                scan_registry.refresh_network()
                msg = "Network scan refreshed."
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                result[0] = msg
                return
            if lower == "refresh all scans":
                scan_registry.refresh_all()
                msg = "All scans refreshed."
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                result[0] = msg
                return

            # === Casual conversation ===
            if is_chitchat(text):
                result[0] = talk_to_llm(text)
                return

            # === Capabilities query ===
            if text.lower() in [
                "what can you do",
                "what can you do?",
                "what can i do",
                "what can i do?",
                "help",
                "capabilities",
            ]:
                response = get_capabilities_summary()
                output_widget.insert("end", "Assistant: " + response + "\n")
                output_widget.see("end")
                speak(response)
                last_ai_response = response
                update_state(last_action="list_capabilities")
                return

            # === Trigger words query ===
            if text.lower() in [
                "trigger words",
                "what are the trigger words",
                "list trigger words",
            ]:
                response = get_trigger_words_summary()
                output_widget.insert("end", "Assistant: " + response + "\n")
                output_widget.see("end")
                speak(response)
                last_ai_response = response
                result[0] = response
                update_state(last_action="list_trigger_words")
                return

            # === Usage tutorial ===
            if text.lower() in [
                "how do i use you",
                "how do i use this",
                "how to use",
                "tutorial",
            ]:
                tutorial = get_usage_tutorial()
                output_widget.insert("end", "Assistant: " + tutorial + "\n")
                output_widget.see("end")
                speak(tutorial)
                last_ai_response = tutorial
                update_state(last_action="tutorial", topic="usage")
                return

            # === Tutorial mode ===
            target = detect_tutorial_target(text)
            if target:
                doc = explain_object(target)
                if doc:
                    output_widget.insert("end", "Assistant: " + doc + "\n")
                    output_widget.see("end")
                    speak(doc)
                    last_ai_response = doc
                    update_state(last_action="tutorial", topic=target)
                    return

            # === Shortcut logic ===
            m = re.search(r"\b(?:open|launch)\s+(.+)", text, re.IGNORECASE)
            if m and not text.lower().startswith("plan "):
                global shortcut_map
                if "shortcut_map" not in globals():
                    shortcut_map = build_shortcut_map()
                command_text = f"open {m.group(1).strip().rstrip('.!?')}"
                response = open_shortcut(command_text, shortcut_map)
                output_widget.insert("end", f"Assistant: [Shortcut] {response}\n")
                output_widget.see("end")
                speak(response)
                if "not found" in response.lower() or "could not" in response.lower():
                    log_error(
                        "Shortcut/action not found or did not execute", context=text
                    )
                last_ai_response = response
                return

            # === Screen viewer ===
            if text.lower() in [
                "show me my screen",
                "what's on my screen",
                "whats on my screen",
            ]:
                screen_viewer_callback()
                msg = "Opening screen view"
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            # === Macro recording & playback ===
            if text.lower().startswith("record "):
                name = text[7:].strip()
                last_ai_response = record_macro(name)
                return

            if text.lower().startswith("play macro "):
                name = text[11:].strip()
                last_ai_response = play_macro(name)
                return

            m = re.match(r"(?:learn|add) (?:resume|trigger) phrase (.+)", text, re.IGNORECASE)
            if m:
                phrase = m.group(1).strip().strip("\"'")
                msg = add_resume_phrase(phrase)
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            # === Codex module scaffolding ===
            m = re.match(r"(?:codex create module|scaffold code) (\w+)\s+(.*)", text, re.IGNORECASE)
            if m:
                mod_name, desc = m.groups()
                try:
                    from modules.codex_integration import CodexClient

                    client = CodexClient(engine=config.get("codex_engine", "code-davinci-002"))
                    code = client.generate_code(desc)
                    if code:
                        path = os.path.join("modules", f"{mod_name}.py")
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(code)
                        ModuleRegistry().auto_discover("modules")
                        msg = f"Module '{mod_name}' created"
                    else:
                        msg = "Codex returned no code"
                except Exception as e:
                    msg = f"Codex error: {e}"
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            # === Planning & Remote commands ===
            if text.lower().startswith("plan "):
                task = text[5:].strip()
                plan = planning_agent.create_plan(task)
                for sub in plan:
                    queue_command(sub, output_widget)
                msg = "Queued plan: " + ", ".join(plan)
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            if text.lower() == "start remote server":
                if remote_srv is None:
                    remote_srv = remote_agent.RemoteServer(
                        callback=lambda cmd: queue_command(cmd, output_widget)
                    )
                    remote_srv.start()
                    msg = f"Remote server started on port {remote_srv.port}"
                else:
                    msg = f"Remote server already running on port {remote_srv.port}"
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            if text.lower() == "stop remote server":
                if remote_srv:
                    remote_srv.shutdown()
                    msg = "Remote server stopped"
                    remote_srv = None
                else:
                    msg = "Remote server not running"
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            m = re.match(r"send remote (\S+) (\d+) (.+)", text, re.IGNORECASE)
            if m:
                host, port, cmd = m.groups()
                ok = remote_agent.send_command(host, int(port), cmd)
                msg = "sent" if ok else "failed to send"
                output_widget.insert("end", f"Assistant: {msg}\n")
                output_widget.see("end")
                speak(msg)
                last_ai_response = msg
                return

            if text.lower() == "exit":
                # Let GUI handle quitting
                result[0] = "QUIT"
                return

            output_widget.insert("end", f"You: {text}\n")
            output_widget.see("end")

            # === Synonym action logic ===
            if cancel_event.is_set():
                return
            action = detect_action(text)
            if action == "ENTER":
                if keyboard:
                    keyboard.press_and_release("enter")
                elif pyautogui:
                    pyautogui.press("enter")
                output_widget.insert("end", "[Action] Pressed Enter\n")
                output_widget.see("end")
                speak("Pressed enter")
                last_ai_response = "Pressed Enter"
                return
            elif action == "TAB":
                if keyboard:
                    keyboard.press_and_release("tab")
                elif pyautogui:
                    pyautogui.press("tab")
                output_widget.insert("end", "[Action] Pressed Tab\n")
                output_widget.see("end")
                speak("Pressed tab")
                last_ai_response = "Pressed Tab"
                return
            elif action == "CLICK":
                if pyautogui:
                    pyautogui.click()
                    output_widget.insert("end", "[Action] Clicked Mouse\n")
                    output_widget.see("end")
                    speak("Clicked mouse")
                    last_ai_response = "Clicked Mouse"
                else:
                    output_widget.insert("end", "[Error] pyautogui missing\n")
                    output_widget.see("end")
                    speak("pyautogui module not available")
                    last_ai_response = "pyautogui missing"
                return

            # === Window Awareness & Button Actions ===
            if cancel_event.is_set():
                return

            def get_button_image(app, action):
                app = app.lower()
                action = action.lower()
                button_map = {
                    "pandora": {
                        "play": "button_images/pandora_play.png",
                        "pause": "button_images/pandora_pause.png",
                    },
                    "youtube": {
                        "play": "button_images/youtube_play.png",
                        "pause": "button_images/youtube_pause.png",
                    },
                }
                if app in button_map and action in button_map[app]:
                    return button_map[app][action]
                generic_path = f"button_images/{action}.png"
                if os.path.exists(generic_path):
                    return generic_path
                return None

            if (
                "hit play" in text.lower() or "press play" in text.lower()
            ) and "on" in text.lower():
                parts = text.lower().split("on")
                action = "play"
                app = parts[1].strip()
                found, msg = window_tools.focus_window(app)
                if not found:
                    result[0] = msg
                    return
                image_path = get_button_image(app, action)
                if image_path and os.path.exists(image_path):
                    found, msg = window_tools.click_ui_element(image_path)
                    if not found:
                        speak(
                            f"I couldn't find the {action} button in {app}. Would you like to teach me?"
                        )
                        output_widget.insert(
                            "end", f"Assistant: {msg} - Awaiting user input to teach.\n"
                        )
                        output_widget.see("end")
                        user_input_teach = input(
                            "Type 'yes' to capture new button template: "
                        )
                        if user_input_teach.lower().strip() == "yes":
                            new_img = window_tools.learn_new_button(app, action, speak)
                            button_map.setdefault(app.lower(), {})[
                                action.lower()
                            ] = new_img
                            result[0] = (
                                f"Learned and saved new {action} button for {app}."
                            )
                        else:
                            result[0] = f"Skipped teaching new button for {app}."
                    else:
                        result[0] = msg
                    return
                else:
                    speak(
                        f"I don't have a template for {action} in {app}. Would you like to teach me?"
                    )
                    user_input_teach = input(
                        "Type 'yes' to capture new button template: "
                    )
                    if user_input_teach.lower().strip() == "yes":
                        new_img = window_tools.learn_new_button(app, action, speak)
                        button_map.setdefault(app.lower(), {})[action.lower()] = new_img
                        result[0] = f"Learned and saved new {action} button for {app}."
                    else:
                        result[0] = f"Skipped teaching new button for {app}."
                return

            if (
                "pause" in text.lower() or "hit pause" in text.lower()
            ) and "on" in text.lower():
                parts = text.lower().split("on")
                action = "pause"
                app = parts[1].strip()
                found, msg = window_tools.focus_window(app)
                if not found:
                    result[0] = msg
                    return
                image_path = get_button_image(app, action)
                if image_path and os.path.exists(image_path):
                    found, msg = window_tools.click_ui_element(image_path)
                    if not found:
                        speak(
                            f"I couldn't find the {action} button in {app}. Would you like to teach me?"
                        )
                        user_input_teach = input(
                            "Type 'yes' to capture new button template: "
                        )
                        if user_input_teach.lower().strip() == "yes":
                            new_img = window_tools.learn_new_button(app, action, speak)
                            button_map.setdefault(app.lower(), {})[
                                action.lower()
                            ] = new_img
                            result[0] = (
                                f"Learned and saved new {action} button for {app}."
                            )
                        else:
                            result[0] = f"Skipped teaching new button for {app}."
                    else:
                        result[0] = msg
                    return
                else:
                    speak(
                        f"I don't have a template for {action} in {app}. Would you like to teach me?"
                    )
                    user_input_teach = input(
                        "Type 'yes' to capture new button template: "
                    )
                    if user_input_teach.lower().strip() == "yes":
                        new_img = window_tools.learn_new_button(app, action, speak)
                        button_map.setdefault(app.lower(), {})[action.lower()] = new_img
                        result[0] = f"Learned and saved new {action} button for {app}."
                    else:
                        result[0] = f"Skipped teaching new button for {app}."
                return

            # === Vision commands ===
            if cancel_event.is_set():
                return
            try:
                if text.lower().startswith("capture region"):
                    _, x, y, w, h = text.split()
                    region = (int(x), int(y), int(w), int(h))
                    ocr_text = vision_tools.ocr_region(region)
                    output_widget.insert("end", f"Assistant: 🧠 OCR: {ocr_text}\n")
                    output_widget.see("end")
                    speak(ocr_text)
                    last_ai_response = ocr_text
                    return
                if text.lower().startswith("click image"):
                    target = text.replace("click image", "", 1).strip()
                    result_img = vision_tools.find_and_click(target)
                    output_widget.insert("end", f"Assistant: 🖱️ {result_img}\n")
                    output_widget.see("end")
                    speak(result_img)
                    if (
                        "not found" in result_img.lower()
                        or "error" in result_img.lower()
                    ):
                        log_error("Vision action failed", context=text)
                    last_ai_response = result_img
                    return
            except Exception as e:
                output_widget.insert("end", f"Assistant: [VISION ERROR]: {e}\n")
                output_widget.see("end")
                log_error(f"Vision command failed: {e}", context=text)
                last_ai_response = f"Vision error: {e}"
                return

            # === Fallback to orchestrator or LLM ===
            if cancel_event.is_set():
                return
            try:
                if user_wants_code(text):
                    from orchestrator import parse_and_execute

                    response = parse_and_execute(text)
                else:
                    response = talk_to_llm(text)
            except Exception as e:
                log_error(f"parse_and_execute failed: {e}", context=text)
                response = talk_to_llm(text)
            result[0] = response

        except Exception as e:
            exception_caught[0] = e

    t = threading.Thread(target=task)
    t.start()
    t.join(BUSY_TIMEOUT)

    if t.is_alive():
        cancel_event.set()
        speak(
            "Sorry, I got a bit lost trying to answer that. Can you ask again?",
        )
        output_widget.insert(
            "end", "Assistant: ⚠️ Timed out or overload! Command was: " + text + "\n"
        )
        output_widget.see("end")
        log_error("Assistant timed out or overloaded.", context=text)
    elif exception_caught[0]:
        speak("Sorry, I encountered an error. Please try again.")
        output_widget.insert("end", f"Assistant: [ERROR]: {exception_caught[0]}\n")
        output_widget.see("end")
        log_error(str(exception_caught[0]), context=text)
    else:
        last_ai_response = result[0]
        if result[0]:
            output_widget.insert("end", f"Assistant: {result[0]}\n\n")
            output_widget.see("end")
            speak(result[0], on_complete=lambda: print("*>"))
        else:
            msg = "Sorry, I could not process that."
            output_widget.insert("end", f"Assistant: {msg}\n\n")
            output_widget.see("end")
            last_ai_response = msg
            print("*>")

    update_state(last_command=last_user_command, last_response=last_ai_response)
    set_state("idle")
    set_listening(False)
    _run_next_in_queue()

    # If quit requested, let GUI handle quitting
    if result[0] == "QUIT":
        return "QUIT"


# --- Sleep/Wake phrases from config ---

WAKE_PHRASES = config.get("wake_phrases", ["hey assistant"])
SLEEP_PHRASES = config.get("sleep_phrases", ["ok that's all"])
RESUME_PHRASES = config.get("resume_phrases", ["next question", "next answer"])
_listening = False


def check_wake(text):
    """Return True if a wake or resume phrase is detected and assistant was asleep."""
    global _listening
    if _listening:
        return False

    text_l = text.lower()
    user_phrases = get_resume_phrases()
    all_phrases = WAKE_PHRASES + RESUME_PHRASES + user_phrases
    for phrase in all_phrases:
        if phrase in text_l:
            _listening = True
            if phrase not in WAKE_PHRASES + RESUME_PHRASES:
                add_resume_phrase(phrase)
            return True

    if text_l.startswith("next "):
        add_resume_phrase(text_l.strip())
        _listening = True
        return True

    return False


def check_sleep(text):
    """Return True if a sleep phrase is detected and assistant was awake; also puts assistant to sleep."""
    global _listening
    if _listening and any(sleep in text.lower() for sleep in SLEEP_PHRASES):
        _listening = False
        return True
    return False


def is_listening():
    """Returns whether assistant is awake/listening."""
    return _listening


def set_listening(val: bool):
    global _listening
    _listening = bool(val)



# --- Response classification helpers ---
try:
    from modules import tools as _tools

    _tool_funcs = getattr(_tools, "__all__", [])
    try:  # optional audio tools
        from modules import audio_tools as _a_tools

        _tool_funcs += list(getattr(_a_tools, "__all__", []))
    except Exception:  # pragma: no cover - optional module
        pass
except Exception:  # pragma: no cover - import failure
    _tool_funcs = ["run_python"]

_CALL_RE = re.compile(
    rf"(?P<call>(?:{'|'.join(map(re.escape, _tool_funcs))})\s*\(.*\))"
)


def split_llm_response(resp: str) -> tuple[str, str | None]:
    """Return (text, code) if ``resp`` contains a tool/function call."""
    m = _CALL_RE.search(resp)
    if not m:
        return resp.strip(), None
    return resp[: m.start()].strip(), m.group("call").strip()


def is_code_response(resp: str) -> bool:
    """Return True if ``resp`` includes a tool or code call."""
    _, code = split_llm_response(resp)
    return code is not None


_CODE_INTENT = [
    "run",
    "execute",
    "calculate",
    "compute",
    "script",
    "code",
    "open",
    "close",
    "terminate",
    "click",
    "type",
    "move",
    "drag",
]


def user_wants_code(text: str) -> bool:
    """Return True if ``text`` looks like a request to run code/tools."""
    lower = text.lower()
    return any(re.search(r"\b" + re.escape(k) + r"\b", lower) for k in _CODE_INTENT)


# --- Memory ---
assistant_memory = load_memory()
# Track chat history for LLM context, persisted via state_manager
conversation_history = state_dict.setdefault("conversation_history", [])
save_state()

# --- LLM interaction ---


def _call_local_llm(prompt: str, history):
    """Return a response from the local LLM or an error string."""
    try:
        return generate_response(prompt, history=history)
    except Exception as exc:  # pragma: no cover - network failure
        return f"[Local Error] {exc}"




def _call_google_llm(prompt: str) -> str:
    """Query the Google Gemini API."""
    try:
        import requests

        key = config.get("google_api_key")
        model = config.get("google_model", "gemini-pro")
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={key}"
        )
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "[Cloud Error] Invalid response"
    except Exception as exc:  # pragma: no cover - network failure
        return f"[Cloud Error] {exc}"


def _call_cloud_llm(prompt: str) -> str:
    """Return a response from the configured cloud provider (Google)."""
    return _call_google_llm(prompt)


def _is_complex_prompt(prompt: str) -> bool:
    """Heuristic check for prompt complexity."""
    words = re.findall(r"\w+", prompt)
    if len(words) > 12:
        return True
    keywords = ["explain", "detailed", "analysis", "summarize", "write", "code"]
    return any(k in prompt.lower() for k in keywords)


def _is_bad_response(resp: str) -> bool:
    """Return True if ``resp`` is empty or too short."""
    if not isinstance(resp, str) or not resp.strip():
        return True
    if resp.startswith("[Local Error]") or resp.startswith("[Cloud Error]"):
        return True
    words = resp.strip().split()
    min_words = config.get("min_good_response_words", 3)
    min_chars = config.get("min_good_response_chars", 10)
    return len(words) < min_words or len(resp.strip()) < min_chars




def online_fallback(prompt):
    """Query the cloud model and fall back to the local LLM on failure."""
    result = _call_cloud_llm(prompt)
    if result.startswith("[Cloud Error]"):
        history = conversation_history[-config.get("conversation_history_limit", 6) :]
        return _call_local_llm(prompt, history)
    return result


def handle_recall(query):
    """Search conversation memory for ``query`` and format the results."""
    vector_results = search_memory(query)
    saved_results = []
    for key, value in assistant_memory.items():
        if query.lower() in str(key).lower() or query.lower() in str(value).lower():
            saved_results.append(f"{key}: {value}")
    if not vector_results and not saved_results:
        return "No memories found for that query."
    output = []
    if vector_results:
        output.append("[Vector Memory]")
        output.extend(f"- {r}" for r in vector_results)
    if saved_results:
        output.append("\n[Saved Memory]")
        output.extend(f"- {r}" for r in saved_results)
    return "\n".join(output)


def explain_object(name: str) -> str | None:
    """Return the docstring for a function, class, or module.

    The lookup searches loaded modules via :class:`ModuleRegistry` and then this
    module's global namespace.  ``name`` may be ``module.func`` or just a simple
    identifier.  ``None`` is returned if no documentation is found.
    """
    registry = ModuleRegistry()
    registry.auto_discover("modules")
    obj = None
    if "." in name:
        mod_name, attr = name.split(".", 1)
        try:
            mod = registry.modules.get(
                f"modules.{mod_name}"
            ) or importlib.import_module(mod_name)
            obj = getattr(mod, attr, None)
        except Exception:
            obj = None
    else:
        for mod in registry.modules.values():
            if hasattr(mod, name):
                obj = getattr(mod, name)
                break
        if obj is None:
            obj = globals().get(name)
    if obj is None:
        return None
    return inspect.getdoc(obj)


def detect_tutorial_target(text: str) -> str | None:
    """Return a function or module name if ``text`` asks about it."""
    match = re.search(r"`?([a-zA-Z_][\w\.]+)`?", text)
    if match and any(k in text.lower() for k in ["how", "what", "explain"]):
        return match.group(1)
    return None


def get_usage_tutorial() -> str:
    """Return a short usage tutorial extracted from ``README.md``.

    The function reads the "Getting Started" section of the repository
    ``README.md`` file and returns it as plain text.  If any error occurs,
    a fallback message is returned instead.
    """
    try:
        start = "## 🚀 Getting Started"
        end_prefix = "## "
        lines = []
        capture = False
        with open("README.md", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith(start):
                    capture = True
                    continue
                if capture and line.strip().startswith(end_prefix):
                    break
                if capture:
                    lines.append(line.rstrip())
        text = "\n".join(lines).strip()
        return text or "See the README for usage instructions."
    except Exception as e:  # pragma: no cover - file read should succeed
        log_error(f"Tutorial read failed: {e}")
        return "Unable to load tutorial."
