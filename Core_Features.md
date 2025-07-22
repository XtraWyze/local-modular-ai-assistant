For the current project roadmap and PR checklist, see the end of README.md.

Overview
Local Modular AI Assistant is a cross-platform, privacy-first, extensible AI agent for your desktop.
It features a GUI, conversational voice interface, plugin systems, desktop automation, “live learning” of new skills, and real perception—it can “see” your screen and “hear” system audio to answer questions or trigger automations.
Runs fully offline or connects to online LLMs for expanded abilities.

Core Features
Conversational Voice Recognition

Streaming STT (speech-to-text), hotword detection, auto-sleep, and background listening

Offline and online models (Vosk, Google, etc.)

GUI Interface

Tkinter-based main window with mic button, output, and easy controls

Full Desktop Automation

Automate mouse, keyboard, windows, screenshots, drag & drop, and clipboard

File management, app launching, custom workflows

OCR (screen text recognition) for “see and click” actions

Run Python, shell commands, or external scripts as steps

Modular plugins—add new automation actions in the modules/ folder
Ask "What can you do?" to list available modules and features

User can interrupt/halt automation safely by voice or hotkey

Perception: Visual & Audio Awareness

Screen Vision: Capture screen regions or windows, read on-screen text, identify UI elements or images, answer “What’s on my screen?”

Audio Awareness: Listen to what’s playing on your computer (not just the mic), transcribe, identify sounds or songs, answer “What is that sound?”

Enables accessible, “situation-aware” automations

Memory & Context

Local conversation memory, context tracking, and recall

Supports custom memory modules for deep context or search

Orchestrator

Routes commands to plugins, skills, automation, or LLM as needed

TTS (Text-to-Speech)

Offline (Coqui), online (gTTS), voice selection, speed and volume adjustment
Voice options can be controlled with phrases like "set speech speed to 1.2", "increase volume", or "use jenny voice".

Config Validation, Error Logging

Built-in validation and structured logs for troubleshooting

Live Learning & Teachability
Teach New Automations—Live!

Users can teach the assistant new tasks or macros at runtime via GUI or voice

“Assistant, learn a new routine called ‘Daily Report’.”

[Assistant records actions or listens to your description]

“Assistant, save and remember this.”

Learning by Demonstration

“Watch me do this”—records user’s mouse, keyboard, app steps

“Record” mode in GUI, then save/names the new macro

Voice-Driven Editing

“Edit my ‘Screenshot and Email’ automation to save files to D:\Screenshots”

Chaining & Scheduling

Trigger, combine, or schedule automations by voice/text or calendar

Perception & Awareness Examples
Visual:

“Read the error message in that popup.”

“Find and click the ‘OK’ button.”

“What’s showing on my screen right now?”

Audio:

“What song is playing?”

“Transcribe the audio from this video.”

“Alert me if you hear a Windows error sound.”

Automation:

“Take a screenshot and upload it to Google Drive.”

“Open Excel, create a new sheet, and copy today’s report data.”

“Monitor my downloads folder and notify me when a PDF appears.”

“When I say ‘goodnight’, mute my PC and turn off the display.”

File/Folder Structure
gui_assistant.py — Main GUI launcher

assistant.py — Core assistant and voice logic

orchestrator.py — Command dispatch and plugin routing

modules/ — Plugins, automation actions, skills
automation_learning.py — record/play user macros

vosk-model-small-en-us-0.15/ — Offline STT model

memory_manager.py, state_manager.py — Memory and recall

utils.py — Shared helpers (e.g., resource_path)

tests/ — Automated tests (pytest)

requirements.txt — Dependencies

config.json — Configuration file

How to Run
pip install -r requirements.txt

Ensure vosk-model-small-en-us-0.15/ is present for offline voice

Run with python gui_assistant.py

Packaging
Use PyInstaller for .exe creation; see PyInstaller and Inno Setup scripts in project or ask the assistant/Codex for packaging commands.

Vision
A truly personal AI agent you can teach, automate, and trust—no coding required.

Local, private, hackable, and endlessly extensible.

Upgrade your assistant’s skills by showing, telling, or connecting new modules—no limits.

Achieve real digital “perception”—understanding what’s on your screen and what you hear.

Contribution
Pull requests, feature ideas, and plugin modules are welcome!
See the examples and guides to get started.

