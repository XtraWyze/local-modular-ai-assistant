from assistant import (
    handle_recall,
    check_wake,
    check_sleep,
    is_listening,
    detect_tutorial_target,
    explain_object,
    get_capabilities_summary,
)
from orchestrator import parse_and_execute
from modules.actions import detect_action
from modules import command_macros
import re
import planning_agent
import keyboard
import pyautogui
import time
import os


# Queue of pending CLI commands processed sequentially
pending_commands: list[str] = []

def queue_command(text: str) -> None:
    """Add a command to the pending queue."""
    pending_commands.append(text)

def _run_next_in_queue() -> None:
    """Process queued commands in FIFO order."""
    while pending_commands:
        cmd = pending_commands.pop(0)
        result = parse_and_execute(cmd)
        print("Assistant:", result)


def process_command(user_input: str):
    """Return a response for basic CLI commands or ``None``."""
    cmd = user_input.strip().lower()
    if cmd.startswith("set volume "):
        try:
            value = int(cmd.split("set volume ", 1)[1])
        except ValueError:
            return "[Error] Invalid volume"
        from modules import system_volume

        return system_volume.set_volume(value)

    if cmd.startswith("set speech volume "):
        try:
            value = float(cmd.split("set speech volume ", 1)[1])
        except ValueError:
            return "[Error] Invalid volume"
        from modules import tts_integration
        if value > 1:
            value = value / 100.0
        result = tts_integration.set_volume(value)
        return "Speech volume set" if result is True else result

    if cmd in {"volume up", "increase volume"}:
        from modules import media_controls

        return media_controls.volume_up()

    if cmd in {"speech volume up", "increase speech volume"}:
        from modules import tts_integration

        val = min(tts_integration.config.get("tts_volume", 0.8) + 0.1, 1.0)
        tts_integration.set_volume(val)
        return f"Speech volume set to {val}"

    if cmd in {"volume down", "decrease volume"}:
        from modules import media_controls

        return media_controls.volume_down()

    if cmd in {"speech volume down", "decrease speech volume"}:
        from modules import tts_integration

        val = max(tts_integration.config.get("tts_volume", 0.8) - 0.1, 0.0)
        tts_integration.set_volume(val)
        return f"Speech volume set to {val}"

    if cmd in {"start recording", "stop recording", "toggle recording"}:
        from modules import gamebar_capture

        return gamebar_capture.toggle_recording()

    if cmd in {"open game bar", "open capture"}:
        from modules import gamebar_capture

        return gamebar_capture.open_capture()

    if cmd in {"take screenshot", "capture screenshot"}:
        from modules import gamebar_capture

        return gamebar_capture.capture_screenshot()

    if cmd in {"record last 30 seconds", "capture last 30 seconds"}:
        from modules import gamebar_capture

        return gamebar_capture.capture_last_30s()

    return None


def handle_cli_input(user_input: str) -> str | None:
    """Process ``user_input`` and return a response string."""
    user_input = user_input.strip()
    if not user_input:
        return ""

    # Record command if a macro is being learned
    if command_macros.is_recording() and user_input.lower() not in {"stop macro"}:
        command_macros.record_command(user_input)

    m = re.match(r"learn this macro (\w+)", user_input, re.IGNORECASE)
    if m:
        return command_macros.start_recording(m.group(1))

    if user_input.lower() == "stop macro":
        return command_macros.stop_recording()

    if user_input.lower() == "list macros":
        names = command_macros.list_macros()
        return ", ".join(names) if names else "No macros saved"

    m = re.match(r"run macro (\w+)", user_input, re.IGNORECASE)
    if m:
        return command_macros.run_macro(m.group(1), parse_and_execute)

    m = re.match(r"edit macro (\w+) (.+)", user_input, re.IGNORECASE)
    if m:
        cmds = [c.strip() for c in m.group(2).split(';') if c.strip()]
        return command_macros.edit_macro(m.group(1), cmds)

    # Basic volume and media commands
    resp = process_command(user_input)
    if resp is not None:
        return resp

    # Sleep/Wake management
    if not is_listening():
        if check_wake(user_input):
            return "I'm awake!"
        return None
    if check_sleep(user_input):
        return "Going to sleep. Say a wake phrase to wake me up."

    if user_input.lower() == "exit":
        return None

    # Queue multi-step instructions
    if user_input.lower().startswith("plan "):
        task = user_input[5:].strip()
        tasks = planning_agent.create_plan(task)
        for t in tasks:
            queue_command(t)
        queued = ", ".join(tasks)
        _run_next_in_queue()
        return f"Queued plan: {queued}"

    plan = planning_agent.create_plan(user_input)
    if len(plan) > 1:
        for t in plan:
            queue_command(t)
        queued = ", ".join(plan)
        _run_next_in_queue()
        return f"Queued tasks: {queued}"

    # Generic actions
    action = detect_action(user_input)
    if action == "ENTER":
        keyboard.press_and_release("enter")
        return "[Action] Pressed Enter"
    elif action == "TAB":
        keyboard.press_and_release("tab")
        return "[Action] Pressed Tab"
    elif action == "CLICK":
        pyautogui.click()
        return "[Action] Clicked Mouse"

    if user_input.startswith("recall "):
        query = user_input.replace("recall ", "", 1).strip()
        return handle_recall(query)

    if user_input.lower().startswith("open "):
        path = user_input[5:].strip()
        os.system(f"start {path}")
        return ""

    if user_input.lower().startswith("type "):
        text = user_input[5:].strip()
        time.sleep(1)
        keyboard.write(text)
        return ""

    if user_input.lower() in ["how do i use you", "how do i use this", "how to use", "tutorial"]:
        from assistant import get_usage_tutorial
        return get_usage_tutorial()

    target = detect_tutorial_target(user_input)
    if target:
        doc = explain_object(target)
        if doc:
            return doc

    if user_input.lower() in [
        "what can you do",
        "what can you do?",
        "what can i do",
        "what can i do?",
        "help",
        "capabilities",
    ]:
        return get_capabilities_summary()

    if user_input.lower().startswith("move mouse to "):
        coords = user_input.replace("move mouse to ", "", 1).split(",")
        if len(coords) == 2:
            try:
                x, y = int(coords[0]), int(coords[1])
                pyautogui.moveTo(x, y, duration=1)
            except ValueError:
                return "[Error] Invalid coordinates"
        return ""

    if user_input.lower() == "click":
        pyautogui.click()
        return ""

    # Fallback to orchestrator/LLM
    return parse_and_execute(user_input)

def cli_loop():
    print(
        "Local AI Assistant with Memory\n"
        "Type 'exit' to quit, 'recall <keyword>' to search memory.\n"
        "Try window commands like 'open notepad', 'close chrome window', or 'resize spotify to 800 600'."
    )
    while True:
        user_input = input("You: ")
        result = handle_cli_input(user_input)
        if user_input.strip().lower() == "exit":
            break
        if result:
            print("Assistant:", result)

if __name__ == "__main__":
    cli_loop()
