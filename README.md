# Local Modular AI Assistant

![tests](https://github.com/owner/repo/actions/workflows/tests.yml/badge.svg)

A privacy-first, voice-enabled local AI assistant with modular automation, customizable memory, and full offline/online LLM support.

---

## ✨ Features

- **Offline voice interaction (fully local and private)**
- **Hotword detection, hard/soft mute, and wake/sleep phrases**
- **Priority 'Stop Assistant' hotword to cancel speech**
- **Alt+/ hotkey toggles voice listening on or off**
- **Unified voice profile for all TTS output**
- **Live config editing:** Change `config.json` and see it reload instantly (no restart needed)
- **Powerful memory search and recall**
- **Conversation history for more contextual responses**
- **Safe automation: tools, actions, and GUI scripting**
- **Record and play macros on the fly for custom workflows**
- **Vision/ocr tools:** Screen capture and image recognition by voice or command
- **Plugin system:** Easy extension with your own Python modules
- **LLM auto-loads module list for accurate tool usage**
- **User-friendly GUI with mic overlay and system tray**
- **Speech learning tab to practice recognition**
- **Lightweight CLI mode for keyboard power-users**
- **Full local/offline LLM via LocalAI or text-generation-webui**
- **Ask "What can you do?" to hear all available modules**
- **TTS speed, volume, and voice adjustable via config or voice command**
- **Fast onboarding: all config, shortcuts, and memory are editable text**
- **Memory viewer/editor:** adjust stored history and `memory_max` from the GUI
- **Config editor tab:** tweak and save `config.json` without leaving the app
- **Automatic .exe scanning builds a registry of installed applications**
- **Startup system/device/network scans populate registries and can be refreshed by voice**
- **Close or terminate apps by window title or process name (e.g. "terminate Rocket League")**
- **List open windows via the taskbar (e.g. "what windows are open?")**
- **Control music playback with media keys (play/pause, skip) using keyboard, Windows API, or pyautogui fallbacks**
- **Tutorial mode:** ask "what does `function_name` do?" to hear documentation
- **Emulation mode:** set `emulate_actions` to true to practice commands safely
- **Crash prevention:** unexpected errors are logged and the assistant says "Crash prevented" before resuming

Adjust voice playback on the fly with phrases like "set speech speed to 1.2", "increase volume", or "use jenny voice." The GUI sliders and menu mirror these settings.

---

## 🚀 Getting Started

### 1. **Installation**

**Requirements:**
- Python 3.10+ (64-bit recommended)
- [Coqui TTS](https://github.com/coqui-ai/TTS)
- [LocalAI](https://github.com/go-skynet/LocalAI) or [text-generation-webui](https://github.com/oobabooga/text-generation-webui) for local LLMs
- [Vosk](https://alphacephei.com/vosk/) speech model (see config for path)
- `sounddevice` (audio playback and microphone input)
- `watchdog` (for live config reload, highly recommended)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for vision tools
  (on Windows set `TESSERACT_CMD` if not installed in the default location)
- `pygetwindow` (or `wmctrl` on Linux) for listing open windows and focusing
  them
- `pycaw` and `comtypes` for adjusting system volume on Windows
- [Git](https://git-scm.com/) (required for `install_llm_backends.py` and the Windows batch file)

**Install Python dependencies:**
```bash
pip install -r requirements.txt
# Or run the cross‑platform helper:
python install_requirements.py
# Windows: run install_requirements.bat for a quick install
# or run setup_venv.py (Windows: setup_venv.bat) to create the `venv/` folder
# and install everything automatically
# Optional: fetch local LLM backends
python install_llm_backends.py --all
# Windows users can run install_llm_backends.bat
# Remove caches and temporary files
python cleanup.py
Optional: Download/prepare your LLM and speech models, and place them in the project directory as needed.

### Required Downloads
Offline use requires a few additional assets:

1. **Vosk speech model** – grab `vosk-model-small-en-us-0.15` from
   <https://alphacephei.com/vosk/models> and extract it to the path specified by
   `vosk_model_path` in `config.json`.
2. **Coqui TTS voice** – run
   `tts --model tts_models/en/jenny/jenny --download` or download another voice
   from the [Coqui TTS](https://github.com/coqui-ai/TTS) project. Update
   `tts_model` in `config.json` with the chosen voice.
3. **LLM backends** – clone LocalAI and text-generation-webui by running
   `python install_llm_backends.py --all` (or the `.bat` file on Windows).
   Follow each backend’s README to place your LLM weights in its `models/`
   directory.
4. **LLM weights** – download a compatible GGUF or GPTQ model (for example,
   [Llama 3 on Hugging Face](https://huggingface.co/)). Put the files under the
   selected backend’s `models/` folder and update `llm_model` accordingly.
5. **Tesseract OCR** – install from
   <https://github.com/tesseract-ocr/tesseract>. On Windows, set the
   `TESSERACT_CMD` environment variable if it’s not in your PATH.

2. Configuration
Edit config.json to customize:

Wake/sleep phrases

TTS and LLM model choices

Plugins and memory settings

Mic overlay appearance/colors

Logging, startup messages, and tips
Busy timeout for commands

Sample config.json:

{
  "tts_model": "tts_models/en/jenny/jenny",
  "tts_voice": null,
  "tts_volume": 0.85,
  "tts_speed": 1.0,
  "use_voice": true,

  "prefer_local_llm": "auto",
  "llm_backend": "localai",
  "llm_model": "llama3",
  "emulate_actions": false,

  "vosk_model_path": "vosk-model-small-en-us-0.15",

  "memory_max": 5000,
  "auto_memory_increase": true,
  "conversation_history_limit": 6,
  "enable_plugins": true,

  "wake_phrases": ["hey assistant", "wake up", "hello assistant"],
  "sleep_phrases": ["go to sleep", "stop listening", "ok that's all"],
  "cancel_phrases": ["stop assistant"],
  "resume_phrases": ["next question", "next answer"],

  "mic_overlay": true,
  "mic_overlay_colors": {
    "listening": "green",
    "sleeping": "red",
    "muted": "gray"
  },

  "startup_message": "Welcome to your local AI assistant!",
  "tips": [
    "Try: capture region 100 200 300 300",
    "Say 'go to sleep' to pause listening.",
    "Click the mic icon to fully mute/unmute."
  ],

  "hotword": "hey assistant",
  "enable_hotword": true,
  "log_level": "info",
  "enable_advanced_logging": false,
  "busy_timeout": 60,
  "min_good_response_words": 3,
  "min_good_response_chars": 10
}

Key options:
- `prefer_local_llm`: always `true` (cloud access removed).
- `min_good_response_words` / `min_good_response_chars`: treat a local
  response as poor quality if shorter than these thresholds.

3. Running the Assistant
GUI Mode:
python gui_assistant.py
Windows users can run **start_gui_assistant.bat** to automatically activate the
virtual environment and launch the GUI.
CLI Mode:
python cli_assistant.py
Windows users can run **start_cli_assistant.bat** for the CLI version.
Android (Pydroid 3):
 1. Install the Pydroid 3 app from Google Play.
 2. Copy this project onto your device.
 3. Run `python install_requirements.py` in the Pydroid terminal.
4. Start the assistant with `python android_cli_assistant.py`.

To package the assistant as a standalone APK, install dependencies from
`android_requirements.txt` (Windows users can run
`install_android_requirements.bat`) and run `python build_apk.py` (see
`BUILD_ANDROID.md`).

4. How to Use
Type or speak your command/question.

Try:

capture region 100 200 300 300

press enter

type hello world

move mouse to 100 200

recall wifi password
record my_demo, play macro my_demo

Or just chat!

Mic Status & Mute Controls (GUI)
🟢 Green: Listening

🔴 Red: Sleeping (only listening for wake phrase)

⚫ Gray: Fully muted (no listening)

Click the mic icon to mute/unmute.

Sleep & Wake Phrases
To sleep: say any of "go to sleep", "stop listening", "ok that's all"

To wake: say any of "hey assistant", "wake up", "hello assistant"

Trigger Word Quick Reference
These keywords activate different modules even if mentioned casually:
- **actions:** enter, tab, click
- **automation_actions:** drag, resize, clipboard
- **browser_automation:** open browser, search
- **device_scanner:** scan devices, list usb
- **voice_input:** listen, mute, unmute
- **tts_integration:** volume, speed, voice
- **media_controls:** play, pause, skip
Ask "what are the trigger words" to hear this list any time.

Memory Recall
Search assistant’s memory:
recall <keyword>

What Can You Do?
Ask "what can you do?" any time to list all loaded modules with short descriptions.

Tutorial Mode
Ask questions like "what does `online_fallback` do?" and the assistant will read
the relevant docstring aloud.
You can also say "how do I use you" or just "tutorial" for a quick walkthrough of the basic commands.

5. Extending & Plugins
Add new tools or actions in `modules/tools.py` or `modules/actions.py`, or create additional Python files in the `modules/` directory.

Use the generator script to scaffold new modules quickly.

Enable/disable plugins in config.json (enable_plugins).

Load plugin packages with `modules.plugin_loader` to dynamically add new
modules at runtime. Launch `python config_gui.py` for a quick settings editor.
Use the **Edit Memory** button there or in the main GUI to view conversation
history and adjust the `memory_max` limit.

Place custom macro scripts in the `macros/` folder. Load them at runtime with `modules.macro_loader` or record new ones with the GUI recorder.
You can now record a macro and automatically generate a runnable Python script using `modules.automation_learning.record_macro_script`.
An example macro `sample_open_notepad.json` is included. Run it with `play macro sample_open_notepad`.
Use `modules.voice_annotations.record_annotation` to add voice notes to a macro.
Preview steps with `modules.overlay_preview.preview_macro` before saving.
Call `modules.macro_suggestions.suggest_macros()` to see recommended macros.

### Planning and Remote Agents
Use the **planning agent** to break a request into subtasks:
```python
from planning_agent import create_plan, assign_tasks
plan = create_plan("open browser and search cats then save results")
assign_tasks(plan, print)  # replace print with your dispatcher
```
You can say `plan <task>` in the assistant to queue the generated subtasks automatically.

Run a **remote agent** server to send commands between machines:
```python
from remote_agent import RemoteServer, send_command
srv = RemoteServer(callback=print)
srv.start()
send_command("localhost", srv.port, "hello")
```
You can also start and control the remote server via voice commands:
`"start remote server"`, `"stop remote server"`, and
`"send remote <host> <port> <command>"`.

Or start the lightweight Flask REST API:
```bash
python -m modules.web_api
```
Then POST JSON `{"command": "your text"}` to `/command`.

### Allowed Plugin APIs
The `ModuleRegistry` can optionally verify imports when loading modules. If this
feature is enabled, any module that tries to import a banned package will fail
to load. This means modules requiring `os` or `subprocess` will be rejected if
those packages are on the banned list. Stick to safe libraries like `math`,
`random`, or the helper modules in `modules/`.

### High-Risk Functions
Certain automation functions can modify your system or execute code. They are
now **enabled by default**. Set the `ALLOW_HIGH_RISK=0` environment variable if
you want to disable `open_app`, `close_app`, `run_python`, `copy_file`, and
`move_file`.

Example:
```bash
ALLOW_HIGH_RISK=0 python assistant.py
```

6. Live Config Editing
Edit and save config.json while the assistant is running.

The assistant will auto-reload your changes and report in the GUI (requires watchdog).

7. Packaging (EXE/Standalone)
Create a standalone binary with PyInstaller. Windows users can optionally build
an installer with Inno Setup.

**Prerequisites**
- Python 3.10 or newer
- `pyinstaller` installed in a clean virtual environment
- *(Windows only)* [Inno Setup](https://jrsoftware.org/isinfo.php) if you want an installer

**Windows Example**
1. Activate your virtual environment and install dependencies:
   ```cmd
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
   Or simply run `build_exe.bat` from the project root. It will create the
   `venv/` folder if needed, install dependencies, and run PyInstaller with the
   settings below.
2. Run PyInstaller from the project root (see `BUILD_WINDOWS.md`):
   ```cmd
   pyinstaller gui_assistant.py ^
     --onefile --noconfirm ^
     --add-data "modules;modules" ^
     --add-data "vosk-model-small-en-us-0.15;vosk-model-small-en-us-0.15" ^
     --add-data "config.json;." ^
     --add-data "assistant_memory.db;." ^
     --icon icon.ico
   ```
   The executable appears in `dist\gui_assistant.exe`.
3. (Optional) Compile `installer.iss` with Inno Setup to create an installer. The
   example script in `BUILD_WINDOWS.md` copies the PyInstaller output to
   `Program Files` and adds a desktop shortcut.

**macOS/Linux Notes**
- Use the same PyInstaller command (without `^` line breaks). Adjust `--add-data`
  paths as needed for your platform.
- macOS builds may require code signing or Gatekeeper approval before running.
- On Linux ensure any voice or clipboard dependencies (like `xclip`) are
  installed.

## 🤝 How to Contribute

We welcome contributions to make the Local Modular AI Assistant even better! Here’s how you can help:

### 1. **Reporting Bugs or Suggesting Features**
- [ ] Open an issue on GitHub (or send an email if not hosted yet) describing the bug or suggestion clearly.
- [ ] Include steps to reproduce, screenshots, and log snippets if reporting a bug.

### 2. **Adding a New Module or Plugin**
- Fork or clone the repository.
- Create a new Python file in the `modules/` directory.
- Use the module template in `examples/my_module.py` (or see `generate_module.py`) for reference.
- Be sure to include a `get_info()` function for discovery and testing.
 - Add your module to your local project and test it with `examples/test_full_run.py`.
- (Optional) Add a test script in `/tests`.

### 3. **Submitting Code**
- Make your changes in a new branch.
- Run `pytest` locally and ensure all tests pass.
- Run `flake8` to check for style issues.
- (Optional) Generate a coverage report with `coverage run -m pytest && coverage html`.
- Update `requirements.txt` and `README.md` if you add new dependencies or features.
- Ensure the GitHub Actions tests badge is green before merging.
- Create a pull request (PR) with a clear summary of your changes.

### 4. **Coding Style**
- Write clean, well-documented code (docstrings are appreciated!).
- Catch exceptions and log errors using `log_error`.
- Follow the structure of existing modules for consistency.

### 5. **Getting Help**
- If you have questions about the codebase, open an issue or email the maintainer.
- For major changes or proposals, start a discussion first!

-### 6. **Contact**
- Project maintainer: [xtrawyxe@gmail.com]
- Or open an issue on GitHub

---

*Thank you for helping make this project awesome!*



🛡️ Safety & Privacy
Assistant only listens/runs actions when awake/unmuted.

All memory and automation runs locally (no data leaves your machine).

No actions or code can be triggered by accident while muted/sleeping.

🛠️ Support, Customization, and Contact
For troubleshooting, see log output and this README.

For customization or help, [contact the project author].

Enjoy your private, modular, and truly local AI assistant!

## 📝 Big Dream AI Assistant: Next Steps Task List

1. **Live Automation Learning**
   - Implement "Learn New Automation" mode:
     - Add a command or GUI button to start recording user actions (mouse,
       keyboard, and screen capture).
     - Provide a timeline editor so the user can tweak, reorder, or delete
       recorded steps before saving.
     - Convert the final workflow into a new plugin or module script that can be
       reused.
     - Let users name, tag, and search their learned automations so they are
       easy to trigger later.
    - Enable "Show Me" mode so the assistant can learn by watching the user
      perform a demonstration in real time.
    - Offer a way to share or import automation scripts with others in the
      community.
    - Allow voice annotations during recording so the assistant can narrate
      each step in the final automation.
    - Provide a preview mode with screenshot overlays so users can verify
      each recorded action before saving.
    - Detect repeated routines and suggest converting them into macros
      automatically.

2. **Unified Voice & Feedback Loop**
   - Refactor TTS to queue, interrupt, or mute speech as needed.
   - Add GUI visual feedback for "Listening", "Speaking", "Busy", and "Idle" states.
   - Enable hotword detection to interrupt TTS or trigger actions even if speaking.

3. **Task Orchestration & Context Management**
   - Improve the orchestrator to:
     - Queue, stack, or defer tasks.
     - Report "I'm busy, wait a moment…" if interrupted.
     - Allow "main quest/side quest" (priorities, task switching).
     - Persist conversational context and task history.

4. **Module Self-Description & Discoverability**
   - Make all modules self-describing:
     - Add `get_description()` or similar to each module.
     - Expose a "What can you do?" intent/command that lists all current skills.
     - Enable the assistant to vocalize or display its skills to the user on demand.

5. **Memory & Knowledge Recall**
   - Upgrade memory manager to:
     - Support semantic/embedding-based search.
     - Store/retrieve reminders, preferences, and "user facts".
     - Allow conversational recall: "Remind me about…", "What did I say last week?"
     - Persist memory across sessions.

6. **Vision/Audio Awareness Integration**
   - Promote OCR/image-to-text as a first-class command: "Read this screen".
   - Add real-time screen/audio event triggers to automations.
   - Allow live vision/audio hooks in learned automations.

7. **UX & Error Handling**
   - Hot-reload modules with no restart required.
   - Fail gracefully if hardware (mic, cam) is missing.
   - Show user-friendly error messages (in GUI and TTS).

8. **Documentation & Tests**
   - Ensure docs/readme always match current feature set.
   - Update/expand tests for every new feature and error case.
   - Document every module and its self-description interface.

### ✅ PR Checklist / User Stories (for Issues/PRs or Codex)
* As a user, I want to teach the assistant new automations by demonstration, so I can automate my unique workflows easily.
* As a user, I want the assistant to give visual and voice feedback about its current status (listening, speaking, busy, idle), so I always know what it's doing.
* As a user, I want to interrupt or queue voice output (TTS) and interact with the assistant even if it's talking, so conversations feel natural.
* As a user, I want to ask "What can you do?" and get a current, accurate list of all assistant capabilities, with descriptions, so I know what's possible.
* As a user, I want my reminders, preferences, and facts about me to be remembered, searchable, and used to personalize responses, so my experience gets better over time.
* As a user, I want to trigger automations by screen/audio events (like "when this window appears, do X"), so my assistant is proactive and context-aware.
* As a user, I want the assistant to never crash or hang if hardware is missing or an error occurs, so it's always reliable.
* As a developer, I want all modules to have self-description strings and help methods, so adding new features is seamless and discoverable.
* As a developer, I want the docs and README to auto-update or prompt for updates when modules change, so docs never go stale.
* As a developer, I want logs if hardware is missing or an error occurs.
