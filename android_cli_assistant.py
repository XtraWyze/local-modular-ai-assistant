import json
import os
from datetime import datetime

MEMORY_FILE = "android_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_memory(memory: dict) -> None:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f)

def handle_input(user_input: str, memory: dict):
    command = user_input.strip().lower()
    if command in {"exit", "quit"}:
        return None
    if command == "what time is it":
        return datetime.now().strftime("%H:%M:%S")
    if command in {"what's your name", "what is your name"}:
        return "I'm your Android CLI Assistant."
    if command.startswith("remember "):
        item = user_input[len("remember "):].strip()
        memory.setdefault("items", []).append(item)
        save_memory(memory)
        return "I'll remember that."
    if command == "what did you remember":
        items = memory.get("items", [])
        if not items:
            return "I don't have anything remembered."
        listing = "\n".join(f"{i+1}. {itm}" for i, itm in enumerate(items))
        return listing
    return "Sorry, I don't understand."

def cli_loop():
    memory = load_memory()
    print("Android CLI Assistant. Type 'exit' or 'quit' to stop.")
    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        response = handle_input(user_input, memory)
        if response is None:
            break
        print("Assistant:", response)

if __name__ == "__main__":
    cli_loop()
