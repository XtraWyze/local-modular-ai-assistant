For the current project roadmap and PR checklist, see the end of README.md.


# AGENTS.md

## 🧠 Overview

This AI assistant is designed as a **modular, local-first system** that supports natural interaction, automation, learning, and multi-agent cooperation. It runs entirely offline, supports live screen interaction, voice input/output, and persistent memory.

Agents communicate using a shared memory structure (JSON) and follow a synchronized protocol where each module is aware of system state and user context.

---

## 🔊 Voice Agent

- **Role:** Listens for voice commands, hotwords, and dictation.
- **Technologies:** `speech_recognition`, Google Speech, Vosk (offline), hotword detection (future: Porcupine).
- **Outputs:** Parsed command strings to shared memory.
- **Input Triggers:** Hotword (“Hey Assistant”), voice input, or keyboard override.

---

## 🗣️ TTS Agent

- **Role:** Speaks assistant responses.
- **Technologies:** `gTTS` (online), `Coqui TTS` (offline fallback).
- **Configurable:** Voice selection, rate control, interruption via hotkey or phrase.
- **Integration:** Responds to all LLM or action confirmations.

---

## 💬 LLM Agent

- **Role:** Processes user intent, generates responses, writes/reads memory.
- **Technologies:** 
  - Local: `llama.cpp`, `gguf` LLM models
- **Capabilities:**
  - Responds to queries
  - Summarizes, codes, explains
  - Talks to other agents via shared state
- **Fallback:** Cloud access removed; all prompts run locally.

---

## 🧩 Automation Agent

- **Role:** Controls the screen and GUI.
- **Technologies:** `pyautogui`, `opencv-python`, `pytesseract`
- **Functions:**
  - Clicks, typing, scrolling
  - Screen capture (static + live)
  - Image-based targeting
- **Examples:**
  - “Click the red button”
  - “Take a screenshot of top-left corner”

---

## 📝 Memory Manager

- **Role:** Tracks system and user state.
- **Files:**
  - `assistant_state.json` – session state, active mode, last command
  - `learned_actions.json` – user-defined workflows/macros
  - `learned_macros.yaml` – voice command to macro mappings
- **Responsibilities:**
  - Profile saving/loading
  - Multi-agent memory sync
  - Conversation history

---

## 🧠 Learned Actions Agent

- **Role:** Manages user-taught workflows or macros.
- **Files:** `learned_actions.json`, `learned_macros.yaml`
- **Structure:** Name, triggers, steps, description
- **Example:**

```json
{
  "name": "take_note",
  "trigger": ["note this", "write it down"],
  "steps": ["gui.open_notepad()", "gui.type(current_input)"]
}
Training: User can create actions by saying “Learn this sequence” (future).

📺 GUI Agent (Tkinter Interface)
Role: Provides live visual interface for input/output, memory view, live log.

Technologies: tkinter, PIL, optional image streaming

Panels:

Current command

Memory state viewer

Screen capture live view

Command builder (future)

🧠 Shared Memory and State Files
File	Purpose
assistant_state.json	Tracks last command, active agents, voice mode, profiles
learned_actions.json	User-defined macros/triggers
conversation_log.txt	(Optional) Past assistant interactions

🔄 Communication Protocol
Agents read and write to shared files. Optionally, a publish/subscribe pattern (via threading, watchdog, or simple event loop) may be used in future versions to react in real-time to changes in memory or command input.

## 🧠 Planning Agent

- **Role:** Break a complex user request into smaller steps for other agents.
- **Usage:** Call `create_plan(text)` to get a list of subtasks, then
  `assign_tasks(plan, dispatcher)` to route each step.

## 🛰️ Remote Agent

- **Role:** Send or receive commands between devices over HTTP.
- **Usage:** Start a server with `RemoteServer(callback=func).start()` and
  forward commands using `send_command(host, port, "my command")`.

---

## Future Work

- 🔌 Plugin Loader: Load third-party tools or Python scripts as assistant plugins.

📍 Status Summary
This file serves as a single-source reference for understanding the modular agent system, their roles, and how they interoperate. Update this document as new agents are added or responsibilities change.
