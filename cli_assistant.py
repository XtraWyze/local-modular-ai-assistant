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
import keyboard
import pyautogui
import time
import os

def cli_loop():
    print("Local AI Assistant with Memory\nType 'exit' to quit, 'recall <keyword>' to search memory.")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        # --- Centralized sleep/wake logic ---
        if not is_listening():
            if check_wake(user_input):
                print("Assistant: I'm awake!")
            continue
        if check_sleep(user_input):
            print("Assistant: Going to sleep. Say a wake phrase to wake me up.")
            continue

        if user_input.lower() == "exit":
            break

        # 1) Detect generic actions (ENTER, TAB, CLICK)
        action = detect_action(user_input)
        if action == "ENTER":
            keyboard.press_and_release("enter")
            print("[Action] Pressed Enter")
            continue
        elif action == "TAB":
            keyboard.press_and_release("tab")
            print("[Action] Pressed Tab")
            continue
        elif action == "CLICK":
            pyautogui.click()
            print("[Action] Clicked Mouse")
            continue

        # 2) Recall from memory
        if user_input.startswith("recall "):
            query = user_input.replace("recall ", "", 1).strip()
            print("Assistant:", handle_recall(query))
            continue

        # 3) Open files or URLs
        if user_input.lower().startswith("open "):
            path = user_input[5:].strip()
            os.system(f'start {path}')
            continue

        # 4) Typing arbitrary text
        if user_input.lower().startswith("type "):
            text = user_input[5:].strip()
            print(f"[Typing]: {text}")
            time.sleep(1)
            keyboard.write(text)
            continue

        if user_input.lower() in ["how do i use you", "how do i use this", "how to use", "tutorial"]:
            from assistant import get_usage_tutorial
            tutorial = get_usage_tutorial()
            print("Assistant:", tutorial)
            continue

        target = detect_tutorial_target(user_input)
        if target:
            doc = explain_object(target)
            if doc:
                print("Assistant:", doc)
                continue

        if user_input.lower() in [
            "what can you do",
            "what can you do?",
            "what can i do",
            "what can i do?",
            "help",
            "capabilities",
        ]:
            desc = get_capabilities_summary()
            print("Assistant:", desc)
            continue

        # 5) Move mouse
        if user_input.lower().startswith("move mouse to "):
            coords = user_input.replace("move mouse to ", "", 1).split(",")
            if len(coords) == 2:
                try:
                    x, y = int(coords[0]), int(coords[1])
                    pyautogui.moveTo(x, y, duration=1)
                except ValueError:
                    print("[Error] Invalid coordinates")
            continue

        # 6) Simple click
        if user_input.lower() == "click":
            pyautogui.click()
            continue

        # 7) Fallback to orchestrator/LLM
        result = parse_and_execute(user_input)
        print("Assistant:", result)

if __name__ == "__main__":
    cli_loop()
