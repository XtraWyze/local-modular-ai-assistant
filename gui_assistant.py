# ========== IMPORTS ==========
import tkinter as tk
from tkinter import ttk


class ReadOnlyText(tk.Text):
    """Text widget that prevents user edits but allows programmatic inserts."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("state", tk.DISABLED)
        super().__init__(*args, **kwargs)
        # Block user key presses to keep the widget read-only
        self.bind("<Key>", lambda _event: "break")

    def insert(self, index, chars, *tags):
        """Insert text while temporarily enabling the widget."""
        self.config(state=tk.NORMAL)
        super().insert(index, chars, *tags)
        self.config(state=tk.DISABLED)
try:
    from PIL import Image, ImageDraw, ImageTk  # type: ignore
except Exception:  # Pillow is optional
    Image = ImageDraw = ImageTk = None  # type: ignore

import threading
import os
import sys
import json
import time
from error_logger import log_error
from modules import gpu
try:
    from watchdog.observers import Observer
    from config_watcher import ConfigFileChangeHandler
    WATCHDOG_AVAILABLE = True
except Exception:
    Observer = None  # type: ignore
    ConfigFileChangeHandler = None  # type: ignore
    WATCHDOG_AVAILABLE = False
from config_loader import ConfigLoader
from config_validator import validate_config
from config_gui import open_memory_window
from assistant import set_screen_viewer_callback
from assistant import (
    process_input,
    check_wake,
    check_sleep,
    is_listening,
    speak,
    set_listening,
    get_state,
)
# voice_input module lives inside the modules package
from modules.voice_input import start_voice_listener
from modules.tts_integration import is_speaking
import modules.tts_integration as tts_module
from modules import speech_learning
# utils is located within the modules package
from modules.utils import resource_path
from modules import wake_sleep_hotkey
from modules import api_keys
from modules import image_generator
from modules import stable_diffusion_generator as sd_generator
from modules.browser_automation import set_webview_callback
from modules import web_activity
try:
    from tkinterweb import HtmlFrame  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    HtmlFrame = None  # type: ignore
try:
    import pystray
except Exception:  # pystray is optional
    pystray = None

# ========== RESOURCE PATH & CONFIG ==========
VOSK_MODEL_PATH = resource_path("vosk-model-small-en-us-0.15")
config_loader = ConfigLoader()
config = config_loader.config
api_keys.apply_keys_from_config()


# ========== TKINTER GUI SETUP ==========
if os.environ.get("PYTEST_CURRENT_TEST"):
    class DummyTk:
        def __init__(self):
            self.tk = self
            self._last_child_ids = {}
            self._w = "."
            self.children = {}

        def __getattr__(self, _name):
            return lambda *a, **k: None
    root = DummyTk()
else:
    root = tk.Tk()
    root.title("AI Assistant")
    # Default size increased so all controls fit comfortably
    root.geometry("900x650")

# Notebook with main UI and speech training tab
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")
main_tab = ttk.Frame(notebook)
speech_tab = ttk.Frame(notebook)
config_tab = ttk.Frame(notebook)
hotkey_tab = ttk.Frame(notebook)
module_tab = ttk.Frame(notebook)
image_tab = ttk.Frame(notebook)
web_tab = ttk.Frame(notebook)
settings_tab = ttk.Frame(notebook)
notebook.add(main_tab, text="Assistant")
notebook.add(speech_tab, text="Speech Learning")
notebook.add(config_tab, text="Config Editor")
notebook.add(hotkey_tab, text="Hotkeys")
notebook.add(module_tab, text="Module Generator")
notebook.add(image_tab, text="Image Generator")
notebook.add(web_tab, text="Web Activity")
notebook.add(settings_tab, text="Settings")

# ---------- Config Editor Tab ----------
config_text = tk.Text(config_tab, wrap=tk.WORD)
config_text.pack(fill="both", expand=True, padx=10, pady=10)

def load_config_text() -> None:
    """Load ``config.json`` into the editor widget."""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            data = f.read()
    except Exception as exc:  # pragma: no cover - unexpected I/O issues
        data = f"Error loading config: {exc}\n"
    config_text.delete("1.0", tk.END)
    config_text.insert(tk.END, data)

def save_config_text() -> None:
    """Validate and save the config editor contents."""
    raw = config_text.get("1.0", tk.END)
    try:
        cfg = json.loads(raw)
    except Exception as exc:
        output.insert(tk.END, f"[CONFIG ERROR] {exc}\n")
        return
    errors = validate_config(cfg)
    if errors:
        output.insert(tk.END, "[CONFIG VALIDATION ERROR]\n" + "\n".join(errors) + "\n")
        return
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    config_loader.config = cfg
    output.insert(tk.END, "[SYSTEM] Config saved.\n")
    reload_config()

btn_frame = ttk.Frame(config_tab)
btn_frame.pack(pady=(0, 10))
ttk.Button(btn_frame, text="Reload", command=load_config_text).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame, text="Save", command=save_config_text).pack(side=tk.LEFT)
ttk.Button(btn_frame, text="Edit Memory", command=open_memory_window).pack(side=tk.LEFT, padx=5)

load_config_text()
# Apply a modern ttk theme if available
style = ttk.Style()
if "clam" in style.theme_names():
    style.theme_use("clam")

# Close button should minimize to tray
def on_close():
    root.withdraw()

root.protocol("WM_DELETE_WINDOW", on_close)

frame = ttk.Frame(main_tab)
frame.pack(padx=10, pady=10, fill="both", expand=True)

# Main output console (read-only for user)
output = ReadOnlyText(frame, height=20, wrap=tk.WORD)
output.pack(fill="both", expand=True)
output.insert(tk.END, "Assistant: Assistant is sleeping. Say your wake phrase to activate.\n")


# Frame for command entry and action buttons
entry_frame = ttk.Frame(main_tab)
entry_frame.pack(fill="x", padx=10, pady=(0, 10))

# Input box for CLI-style commands
entry = ttk.Entry(entry_frame)
entry.pack(side=tk.LEFT, fill="x", expand=True)
entry.bind("<Return>", lambda event: send())

# New input box for natural language task descriptions
task_frame = ttk.Frame(main_tab)
task_frame.pack(fill="x", padx=10, pady=(0, 10))
task_label = ttk.Label(task_frame, text="Describe a Task:")
task_label.pack(anchor="w")
task_entry = ttk.Entry(task_frame)
task_entry.pack(fill="x")
task_entry.bind("<Return>", lambda event: send_task())
task_entry.bind("<Up>", lambda event: show_prev_task(event))
task_entry.bind("<Down>", lambda event: show_next_task(event))

# Validate on initial load now that the output widget exists
errors = validate_config(config)
if errors:
    output.insert(tk.END, "[CONFIG VALIDATION ERROR]\n" + "\n".join(errors) + "\n")
    print("Config validation failed. Fix and restart the app.")
    sys.exit(1)

# ========== MIC STATUS OVERLAY (UI ONLY) ==========
def create_mic_icon(color):
    """Create a microphone status icon.

    Falls back to a simple square ``PhotoImage`` if Pillow is not available."""
    if Image is None or ImageTk is None:
        img = tk.PhotoImage(width=40, height=40)
        img.put(color, to=(0, 0, 40, 40))
        return img
    img = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((5, 5, 35, 35), fill=color)
    return ImageTk.PhotoImage(img)

mic_active_icon = create_mic_icon("green")
mic_sleep_icon = create_mic_icon("red")
mic_hardmute_icon = create_mic_icon("gray")

mic_button = tk.Label(root, image=mic_active_icon, cursor="hand2")
mic_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
mic_status_label = tk.Label(root, text="Mic: Listening", fg="green", font=("Arial", 10, "bold"))
mic_status_label.place(relx=1.0, rely=0.0, anchor="ne", x=-60, y=20)

mic_hard_muted = False

def update_mic_overlay():
    if mic_hard_muted:
        mic_button.configure(image=mic_hardmute_icon)
        mic_status_label.config(text="Mic: Fully Muted", fg="gray")
    elif is_listening():
        mic_button.configure(image=mic_active_icon)
        mic_status_label.config(text="Mic: Listening", fg="green")
    else:
        mic_button.configure(image=mic_sleep_icon)
        mic_status_label.config(text="Mic: Sleeping", fg="red")
    root.after(400, update_mic_overlay)

def on_mic_click(event=None):
    global mic_hard_muted
    mic_hard_muted = not mic_hard_muted
    if mic_hard_muted:
        speak("Microphone fully muted. I won't listen for anything until you unmute.")
        output.insert(tk.END, "Assistant: 🛑 Assistant fully muted by overlay.\n")
    else:
        speak("Microphone unmuted. I'm listening for your wake phrase.")
        output.insert(tk.END, "Assistant: 🎤 Assistant unmuted by overlay.\n")
    update_mic_overlay()

mic_button.bind("<Button-1>", on_mic_click)
update_mic_overlay()

# ========== ACTIVITY STATUS ==========
status_label = ttk.Label(root, text="Ready", foreground="green", font=("Arial", 10, "bold"))
status_label.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

def update_status_label():
    if is_speaking():
        status_label.config(text="Speaking...", foreground="blue")
    elif get_state() == "processing":
        status_label.config(text="Processing...", foreground="orange")
    else:
        status_label.config(text="Ready", foreground="green")
    root.after(200, update_status_label)

update_status_label()

# ========== SCREEN VIEWER WINDOW ==========

class ScreenViewer(tk.Toplevel):
    """Live screen capture window with simple macro controls."""

    def __init__(self, master=None, fps: int = 3):
        super().__init__(master)
        self.title("Screen View")
        self.fps = max(1, fps)
        self._after_id = None
        self.recording = False
        self.recorded_events: list = []
        self.label = tk.Label(self)
        self.label.pack()
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Record Macro", command=self.start_record).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Stop Recording", command=self.stop_record).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Play Macro", command=self.play_macro).pack(side=tk.LEFT, padx=5)
        self._update_frame()

    def _grab_screen(self):
        try:
            from PIL import ImageGrab, ImageTk  # type: ignore
            img = ImageGrab.grab()
            return ImageTk.PhotoImage(img)
        except Exception:
            try:
                import pyautogui
                img = pyautogui.screenshot()
                return ImageTk.PhotoImage(img)
            except Exception:
                return None

    def _update_frame(self):
        if self.recording:
            return
        photo = self._grab_screen()
        if photo is not None:
            self.label.configure(image=photo)
            self.label.image = photo
        self._after_id = self.after(int(1000 / self.fps), self._update_frame)

    def start_record(self):
        if self.recording:
            return
        self.recording = True
        if self._after_id:
            self.after_cancel(self._after_id)

        from modules.automation_learning import record_events

        def _rec():
            try:
                self.recorded_events = record_events()
            except Exception:
                self.recorded_events = []
            finally:
                self.recording = False
                self._update_frame()

        threading.Thread(target=_rec, daemon=True).start()

    def stop_record(self):
        if not self.recording:
            return
        try:
            import keyboard
            keyboard.press_and_release("esc")
        except Exception:
            pass

    def play_macro(self):
        if self.recording or not self.recorded_events:
            return
        try:
            from modules.automation_learning import play_events
            play_events(self.recorded_events)
        except Exception:
            pass

    def destroy(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        super().destroy()

screen_viewer_window: ScreenViewer | None = None

def open_screen_viewer():
    """Open or focus the ScreenViewer window."""
    global screen_viewer_window
    if screen_viewer_window and screen_viewer_window.winfo_exists():
        screen_viewer_window.focus()
        return screen_viewer_window
    screen_viewer_window = ScreenViewer(master=root)
    return screen_viewer_window

set_screen_viewer_callback(open_screen_viewer)


# ========== SEND BUTTON HANDLER (UI ONLY) ==========
def send():
    user_input = entry.get()
    entry.delete(0, tk.END)
    # Use imported process_input, pass the UI output widget for responses
    threading.Thread(target=process_input, args=(user_input, output), daemon=True).start()

# ===== Task Entry Handlers =====
task_history = []
history_index = 0

def send_task(event=None):
    """Send natural-language task description to the assistant."""
    global history_index
    user_input = task_entry.get()
    task_entry.delete(0, tk.END)
    if not user_input.strip():
        return
    task_history.append(user_input)
    history_index = len(task_history)
    threading.Thread(target=process_input, args=(user_input, output), daemon=True).start()

def show_prev_task(event):
    global history_index
    if task_history and history_index > 0:
        history_index -= 1
        task_entry.delete(0, tk.END)
        task_entry.insert(0, task_history[history_index])

def show_next_task(event):
    global history_index
    if task_history and history_index < len(task_history) - 1:
        history_index += 1
        task_entry.delete(0, tk.END)
        task_entry.insert(0, task_history[history_index])
    else:
        task_entry.delete(0, tk.END)
    # ========== “Reload Config” Button and Handler=================
def reload_config():
    global config
    config = config_loader.reload()
    api_keys.apply_keys_from_config()
    errors = validate_config(config)
    if errors:
        output.insert(tk.END, "[CONFIG VALIDATION ERROR]\n" + "\n".join(errors) + "\n")
        speak("Reload failed due to config error.")
        return

    output.insert(tk.END, "[SYSTEM] Config reloaded and validated!\n")
    speak("Configuration has been reloaded.")

    # Mirror updated values in the UI controls
    volume_scale.set(config.get("tts_volume", 0.8))
    speed_scale.set(config.get("tts_speed", 1.0))
    tts_module.config.update(config)
    current_voice = config.get("tts_voice") or voice_var.get()
    voice_var.set(current_voice)

# ========== BUTTON HANDLER (UI ONLY) ==========
buttons_frame = ttk.Frame(entry_frame)
buttons_frame.pack(side=tk.LEFT)

send_button = ttk.Button(buttons_frame, text="Send", command=send)
send_button.pack(side=tk.LEFT, padx=(5, 5))
task_button = ttk.Button(buttons_frame, text="Run Task", command=send_task)
task_button.pack(side=tk.LEFT, padx=(0, 5))
reload_button = ttk.Button(buttons_frame, text="Reload Config", command=reload_config)
reload_button.pack(side=tk.LEFT, padx=(0, 5))
memory_button = ttk.Button(buttons_frame, text="Edit Memory", command=open_memory_window)
memory_button.pack(side=tk.LEFT, padx=(0, 5))
screen_button = ttk.Button(buttons_frame, text="What's on my screen?", command=open_screen_viewer)

screen_button.pack(side=tk.LEFT, padx=(0, 5))



# ========== TTS SPEED SLIDER ==========
tts_frame = ttk.Frame(main_tab)
tts_frame.pack(fill="x", padx=10, pady=(0, 10))

speed_scale = tk.Scale(
    tts_frame,
    from_=0.5,
    to=2.0,
    resolution=0.1,
    orient=tk.HORIZONTAL,
    label="TTS Speed",
    command=lambda v: tts_module.set_speed(float(v)),
)
speed_scale.set(config.get("tts_speed", 1.0))
speed_scale.pack(side=tk.LEFT, padx=(0, 10))

# ========== TTS VOLUME SLIDER ==========
volume_scale = tk.Scale(
    tts_frame,
    from_=0.0,
    to=1.0,
    resolution=0.05,
    orient=tk.HORIZONTAL,
    label="Volume",
    command=lambda v: tts_module.set_volume(float(v)),
)
volume_scale.set(config.get("tts_volume", 0.8))
volume_scale.pack(side=tk.LEFT, padx=(0, 10))

# ========== TTS VOICE MENU ==========
voices = tts_module.list_voices()
voice_var = tk.StringVar()
current_voice = config.get("tts_voice") or (voices[0] if voices else "")
voice_var.set(current_voice)
voice_menu = ttk.OptionMenu(tts_frame, voice_var, current_voice, *voices, command=lambda v: tts_module.set_voice(v))
voice_menu.configure(text="TTS Voice")
voice_menu.pack(side=tk.LEFT)

# ---------- Hotkeys Tab ----------
# Hotkey assignment for wake/sleep
assign_frame = ttk.Frame(hotkey_tab, padding=10)
assign_frame.pack(fill="x")

ttk.Label(assign_frame, text="Wake Hotkey:").grid(row=0, column=0, sticky="w")
wake_hotkey_var = tk.StringVar(value=wake_sleep_hotkey.WAKE_HOTKEY)
wake_entry = ttk.Entry(assign_frame, textvariable=wake_hotkey_var, width=20)
wake_entry.grid(row=0, column=1, sticky="w")

ttk.Label(assign_frame, text="Sleep Hotkey:").grid(row=1, column=0, sticky="w")
sleep_hotkey_var = tk.StringVar(value=wake_sleep_hotkey.SLEEP_HOTKEY)
sleep_entry = ttk.Entry(assign_frame, textvariable=sleep_hotkey_var, width=20)
sleep_entry.grid(row=1, column=1, sticky="w")

assign_status = ttk.Label(assign_frame, text="")
assign_status.grid(row=3, column=0, columnspan=2, pady=(5, 0))

def apply_hotkeys() -> None:
    msg = wake_sleep_hotkey.set_hotkeys(
        wake_hotkey_var.get().strip(), sleep_hotkey_var.get().strip()
    )
    assign_status.config(text=msg)

ttk.Button(assign_frame, text="Apply Hotkeys", command=apply_hotkeys).grid(
    row=2, column=0, columnspan=2, pady=(5, 5)
)

macro_name_var = tk.StringVar()
macro_frame = ttk.Frame(hotkey_tab, padding=10)
macro_frame.pack(fill="both", expand=True)

ttk.Label(macro_frame, text="Macro Name:").pack(anchor="w")
macro_entry = ttk.Entry(macro_frame, textvariable=macro_name_var)
macro_entry.pack(fill="x", pady=(0, 5))

macro_status = ttk.Label(macro_frame, text="")
macro_status.pack(pady=(0, 10))


def start_macro_recording() -> None:
    """Start recording a macro after a short countdown."""
    name = macro_name_var.get().strip()
    if not name:
        macro_status.config(text="Enter a macro name first.")
        return

    count = 3

    def record_macro_thread() -> None:
        from modules import automation_learning

        path = automation_learning.record_macro(name)
        def _cb() -> None:
            macro_status.config(text=f"Saved to {path}")
            update_macro_buttons()

        macro_status.after(0, _cb)

    def countdown_step() -> None:
        nonlocal count
        if count > 0:
            macro_status.config(text=f"Recording in {count}...")
            macro_status.after(1000, countdown_step)
            count -= 1
        else:
            macro_status.config(text="Recording... Press ESC to stop.")
            threading.Thread(target=record_macro_thread, daemon=True).start()

    countdown_step()


ttk.Button(macro_frame, text="Record Macro", command=start_macro_recording).pack(
    pady=(0, 10)
)

# --- Macro Button Grid ---
macro_buttons_frame = ttk.Frame(macro_frame)
macro_buttons_frame.pack(fill="both", expand=True)
macro_buttons: list[ttk.Button] = []

def _run_macro(name: str) -> None:
    """Play the macro ``name`` and show status."""
    from modules.automation_learning import play_macro

    result = play_macro(name)
    macro_status.config(text=result)


def update_macro_buttons() -> None:
    """Refresh the macro grid based on saved macros."""
    from modules.automation_learning import list_macros

    macros = list_macros()
    for i, btn in enumerate(macro_buttons):
        if i < len(macros):
            name = macros[i]
            btn.configure(
                text=name,
                state=tk.NORMAL,
                command=lambda n=name: _run_macro(n),
            )
        else:
            btn.configure(
                text=f"Slot {i + 1}", command=lambda: None, state=tk.DISABLED
            )


for r in range(5):
    for c in range(6):
        btn = ttk.Button(macro_buttons_frame, text=f"Slot {r * 6 + c + 1}")
        btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
        macro_buttons.append(btn)
for i in range(6):
    macro_buttons_frame.columnconfigure(i, weight=1)

update_macro_buttons()


def _remove_macro(name: str) -> None:
    """Delete ``name`` macro file and unregister the action."""
    from modules.automation_learning import MACRO_DIR
    from state_manager import remove_action

    try:
        path = os.path.join(MACRO_DIR, f"{name}.json")
        if os.path.exists(path):
            os.remove(path)
    except Exception as exc:  # pragma: no cover - file I/O error
        log_error(f"[GUI] remove macro error: {exc}")
    remove_action(name)
    update_macro_buttons()


def edit_macros() -> None:
    """Open a simple editor to delete individual or all macros."""
    win = tk.Toplevel(root)
    win.title("Edit Macros")
    listbox = tk.Listbox(win)
    listbox.pack(fill="both", expand=True, padx=10, pady=10)

    def _refresh() -> None:
        listbox.delete(0, tk.END)
        from modules.automation_learning import list_macros

        for m in list_macros():
            listbox.insert(tk.END, m)

    status = ttk.Label(win, text="")
    status.pack()

    def delete_selected() -> None:
        if not listbox.curselection():
            status.config(text="Select a macro first.")
            return
        name = listbox.get(listbox.curselection()[0])
        _remove_macro(name)
        status.config(text=f"Deleted {name}")
        _refresh()

    def delete_all() -> None:
        for name in listbox.get(0, tk.END):
            _remove_macro(name)
        status.config(text="All macros deleted")
        _refresh()

    btn_frame = ttk.Frame(win)
    btn_frame.pack(pady=5)
    ttk.Button(btn_frame, text="Delete Selected", command=delete_selected).pack(
        side=tk.LEFT, padx=5
    )
    ttk.Button(btn_frame, text="Delete All", command=delete_all).pack(
        side=tk.LEFT, padx=5
    )

    _refresh()


ttk.Button(macro_frame, text="Edit Macros", command=edit_macros).pack(pady=(0, 5))


# ---------- Module Generator Tab ----------
gen_name_var = tk.StringVar()
ttk.Label(module_tab, text="Module Name:").pack(anchor="w", padx=10, pady=(10, 0))
gen_name_entry = ttk.Entry(module_tab, textvariable=gen_name_var)
gen_name_entry.pack(fill="x", padx=10)

ttk.Label(module_tab, text="Description:").pack(anchor="w", padx=10, pady=(10, 0))
gen_desc = tk.Text(module_tab, height=4)
gen_desc.pack(fill="x", padx=10)

# -- API Keys Section --
api_frame = ttk.LabelFrame(module_tab, text="API Keys")
api_frame.pack(fill="x", padx=10, pady=(10, 5))
openai_var = tk.StringVar(value=config.get("api_keys", {}).get("openai", ""))
anthropic_var = tk.StringVar(value=config.get("api_keys", {}).get("anthropic", ""))
google_var = tk.StringVar(value=config.get("api_keys", {}).get("google", ""))
ttk.Label(api_frame, text="OpenAI:").grid(row=0, column=0, sticky="w")
ttk.Entry(api_frame, textvariable=openai_var, width=40).grid(row=0, column=1, sticky="ew")
ttk.Label(api_frame, text="Anthropic:").grid(row=1, column=0, sticky="w")
ttk.Entry(api_frame, textvariable=anthropic_var, width=40).grid(row=1, column=1, sticky="ew")
ttk.Label(api_frame, text="Google:").grid(row=2, column=0, sticky="w")
ttk.Entry(api_frame, textvariable=google_var, width=40).grid(row=2, column=1, sticky="ew")
api_frame.columnconfigure(1, weight=1)

def save_api_keys() -> None:
    keys = {
        "openai": openai_var.get().strip(),
        "anthropic": anthropic_var.get().strip(),
        "google": google_var.get().strip(),
    }
    api_keys.save_api_keys(keys)
    gen_status.config(text="API keys saved.")

ttk.Button(api_frame, text="Save Keys", command=save_api_keys).grid(row=3, column=0, columnspan=2, pady=5)

# Provider selection
provider_var = tk.StringVar(value="openai")
ttk.Label(module_tab, text="Provider:").pack(anchor="w", padx=10)
ttk.OptionMenu(module_tab, provider_var, "openai", "openai", "anthropic", "google").pack(anchor="w", padx=10)

ttk.Label(module_tab, text="Preview:").pack(anchor="w", padx=10, pady=(10, 0))
gen_preview = tk.Text(module_tab, height=15)
gen_preview.pack(fill="both", expand=True, padx=10)
gen_status = ttk.Label(module_tab, text="")
gen_status.pack(anchor="w", padx=10, pady=(5, 0))

def generate_preview() -> None:
    desc = gen_desc.get("1.0", tk.END).strip()
    if not desc:
        gen_status.config(text="Enter a description first.")
        return
    try:
        from modules.module_generator import CodexClient

        client = CodexClient(provider=provider_var.get())
        code = client.generate_code(desc)
        if not code:
            gen_status.config(text="No code returned")
            return
        gen_preview.delete("1.0", tk.END)
        gen_preview.insert("1.0", code)
        save_btn.config(state=tk.NORMAL)
        cancel_btn.config(state=tk.NORMAL)
        gen_status.config(text="Preview generated. Click Save to keep it.")
        generate_preview.current_code = code
    except Exception as exc:  # pragma: no cover - network failure
        gen_status.config(text=f"Error: {exc}")

generate_preview.current_code = ""

def save_generated() -> None:
    code = generate_preview.current_code
    if not code:
        gen_status.config(text="Generate code first.")
        return
    name = gen_name_var.get().strip() or None
    try:
        from modules import module_generator

        path = module_generator.save_module_code(code, name=name)
        gen_status.config(text=f"Saved to {path}")
        gen_preview.delete("1.0", tk.END)
        save_btn.config(state=tk.DISABLED)
        cancel_btn.config(state=tk.DISABLED)
        generate_preview.current_code = ""
    except Exception as exc:
        gen_status.config(text=f"Error: {exc}")

def cancel_generated() -> None:
    gen_preview.delete("1.0", tk.END)
    save_btn.config(state=tk.DISABLED)
    cancel_btn.config(state=tk.DISABLED)
    generate_preview.current_code = ""
    gen_status.config(text="Cancelled")

btn_frame_gen = ttk.Frame(module_tab)
btn_frame_gen.pack(pady=5)
gen_btn = ttk.Button(btn_frame_gen, text="Generate Preview", command=generate_preview)
gen_btn.pack(side=tk.LEFT, padx=5)
save_btn = ttk.Button(btn_frame_gen, text="Save Module", state=tk.DISABLED, command=save_generated)
save_btn.pack(side=tk.LEFT, padx=5)
cancel_btn = ttk.Button(btn_frame_gen, text="Cancel", state=tk.DISABLED, command=cancel_generated)
cancel_btn.pack(side=tk.LEFT, padx=5)

# ---------- Image Generator Tab ----------
img_prompt = tk.Text(image_tab, height=4)
img_prompt.pack(fill="x", padx=10, pady=(10, 0))

# Source toggle
source_var = tk.StringVar(value="cloud")
ttk.Label(image_tab, text="Source:").pack(anchor="w", padx=10, pady=(5, 0))
source_menu = ttk.OptionMenu(
    image_tab,
    source_var,
    "cloud",
    "cloud",
    "local",
    command=lambda _v: toggle_source(),
)
source_menu.pack(anchor="w", padx=10)

# Stable Diffusion settings
sd_model_var = tk.StringVar(value="")
ttk.Label(image_tab, text="SD Model Path:").pack(anchor="w", padx=10, pady=(5, 0))
sd_model_entry = ttk.Entry(image_tab, textvariable=sd_model_var, width=50)
sd_model_entry.pack(fill="x", padx=10)

sd_device_var = tk.StringVar(value=gpu.get_device())
ttk.Label(image_tab, text="Device:").pack(anchor="w", padx=10, pady=(5, 0))
sd_device_menu = ttk.OptionMenu(
    image_tab,
    sd_device_var,
    "cpu",
    "cpu",
    "cuda",
)
sd_device_menu.pack(anchor="w", padx=10)

size_var = tk.StringVar(value="512x512")
ttk.Label(image_tab, text="Size:").pack(anchor="w", padx=10, pady=(5, 0))
ttk.OptionMenu(image_tab, size_var, "512x512", "256x256", "512x512", "1024x1024").pack(anchor="w", padx=10)

def toggle_source(*_args) -> None:
    """Enable or disable local model fields based on ``source_var``."""
    state = tk.NORMAL if source_var.get() == "local" else tk.DISABLED
    sd_model_entry.config(state=state)
    sd_device_menu.config(state=state)

toggle_source()

img_preview = ttk.Label(image_tab)
img_preview.pack(pady=10)
img_status = ttk.Label(image_tab, text="")
img_status.pack(anchor="w", padx=10, pady=(5, 0))

def generate_image_btn() -> None:
    prompt = img_prompt.get("1.0", tk.END).strip()
    if not prompt:
        img_status.config(text="Enter a prompt first.")
        return
    img_status.config(text="Generating...")

    def _run() -> None:
        if source_var.get() == "local":
            path = sd_generator.generate_image(
                prompt,
                sd_model_var.get(),
                device=sd_device_var.get(),
            )
        else:
            path = image_generator.generate_image(prompt, size=size_var.get())

        def _update() -> None:
            if path.endswith(".png") and os.path.exists(path):
                if Image and ImageTk:
                    try:
                        img = Image.open(path)
                        photo = ImageTk.PhotoImage(img)
                        img_preview.configure(image=photo)
                        img_preview.image = photo
                    except Exception:
                        img_preview.configure(image="")
                img_status.config(text=f"Saved to {path}")
            else:
                img_preview.configure(image="")
                img_status.config(text=path)

        img_status.after(0, _update)

    threading.Thread(target=_run, daemon=True).start()

ttk.Button(image_tab, text="Generate Image", command=generate_image_btn).pack(pady=5)

# ---------- Web Activity Tab ----------
web_search_var = tk.StringVar()
ttk.Label(web_tab, text="Search or URL:").pack(anchor="w", padx=10, pady=(10, 0))
web_entry = ttk.Entry(web_tab, textvariable=web_search_var)
web_entry.pack(fill="x", padx=10)

if HtmlFrame:
    web_view = HtmlFrame(web_tab)
    web_view.pack(fill="both", expand=True, padx=10, pady=10)
else:
    # Fallback text widget if tkinterweb isn't installed
    web_view = tk.Text(web_tab, height=20)
    web_view.insert(
        "1.0",
        "tkinterweb not installed. URLs will open in your default browser.\n",
    )
    web_view.config(state=tk.DISABLED)
    web_view.pack(fill="both", expand=True, padx=10, pady=10)

# Listbox showing visited URLs
history_box = tk.Listbox(web_tab, height=5)
history_box.pack(fill="x", padx=10, pady=(0, 10))


def _load_url(url: str) -> None:
    view = web_view if HtmlFrame else None
    web_activity.load_url(url, view)
    history_box.delete(0, tk.END)
    for item in web_activity.get_history()[-50:]:
        history_box.insert(tk.END, item)


def run_web_search(_event=None) -> None:
    query = web_search_var.get().strip()
    web_search_var.set("")
    if not query:
        return
    url = web_activity.create_search_url(query)
    _load_url(url)


def open_selected(_event=None):
    if not history_box.curselection():
        return
    url = history_box.get(history_box.curselection()[0])
    _load_url(url)


history_box.bind("<Double-Button-1>", open_selected)
web_entry.bind("<Return>", run_web_search)
ttk.Button(web_tab, text="Go", command=run_web_search).pack(pady=(0, 10))
set_webview_callback(_load_url)

# ---------- Settings Tab ----------
use_remote_var = tk.BooleanVar(value=bool(config.get("llm_url")))
url_var = tk.StringVar(value=config.get("llm_url", "http://localhost:11434/v1/chat/completions"))

def _toggle_remote() -> None:
    state = tk.NORMAL if use_remote_var.get() else tk.DISABLED
    url_entry.config(state=state)

ttk.Checkbutton(
    settings_tab,
    text="Use remote Ollama server",
    variable=use_remote_var,
    command=_toggle_remote,
).pack(anchor="w", padx=10, pady=(10, 5))

ttk.Label(settings_tab, text="LLM URL:").pack(anchor="w", padx=10)
url_entry = ttk.Entry(settings_tab, textvariable=url_var, width=50)
url_entry.pack(fill="x", padx=10)

# Settings tab currently only supports toggling remote LLM usage

def save_settings() -> None:
    cfg = config_loader.config
    if use_remote_var.get():
        cfg["llm_url"] = url_var.get().strip()
    else:
        cfg.pop("llm_url", None)
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    config_loader.config = cfg
    output.insert(tk.END, "[SYSTEM] Settings saved.\n")
    reload_config()

ttk.Button(settings_tab, text="Save Settings", command=save_settings).pack(pady=10)
_toggle_remote()

# ---------- Speech Learning Tab ----------
speech_label = ttk.Label(
    speech_tab,
    text="Practice speaking or teach new wake/sleep phrases. Read the prompts and review the results.",
)
speech_label.pack(pady=(10, 5))


def _set_ro_text(widget: tk.Text, text: str) -> None:
    """Replace ``widget`` contents while keeping it read-only."""

    widget.config(state=tk.NORMAL)
    widget.delete("1.0", tk.END)
    widget.insert("1.0", text)
    widget.config(state=tk.DISABLED)


def _run_learning(prompts, widget, update_phrases=False):
    """Run speech learning for ``prompts`` and display results."""

    _set_ro_text(widget, "")
    results = speech_learning.read_sentences(prompts, speak_func=tts_module.speak)
    for heard in results:
        widget.insert(tk.END, heard + "\n")
    if update_phrases and len(results) >= 2:
        from phrase_manager import add_wake_phrase, add_sleep_phrase

        widget.insert(tk.END, add_wake_phrase(results[0]) + "\n")
        widget.insert(tk.END, add_sleep_phrase(results[1]) + "\n")


def run_wake_sleep():
    _run_learning(
        speech_learning.WAKE_SLEEP_PROMPTS,
        wake_result,
        update_phrases=True,
    )


def run_sentence():
    _run_learning(speech_learning.SENTENCE_PROMPTS, sentence_result)


def run_paragraph():
    _run_learning(speech_learning.PARAGRAPH_PROMPTS, paragraph_result)

wake_frame = ttk.Frame(speech_tab)
wake_frame.pack(fill="x", padx=10, pady=5)
wake_btn = ttk.Button(wake_frame, text="Learn Wake/Sleep", command=run_wake_sleep)
wake_btn.pack(side=tk.LEFT, padx=(0, 5))
wake_col = ttk.Frame(wake_frame)
wake_col.pack(side=tk.LEFT, fill="both", expand=True)
ttk.Label(wake_col, text="\n".join(speech_learning.WAKE_SLEEP_PROMPTS)).pack(anchor="w")
wake_result = ReadOnlyText(wake_col, height=len(speech_learning.WAKE_SLEEP_PROMPTS), width=60, wrap=tk.WORD)
wake_result.pack(fill="x")

sentence_frame = ttk.Frame(speech_tab)
sentence_frame.pack(fill="x", padx=10, pady=5)
sentence_btn = ttk.Button(sentence_frame, text="Sentence", command=run_sentence)
sentence_btn.pack(side=tk.LEFT, padx=(0, 5))
sentence_col = ttk.Frame(sentence_frame)
sentence_col.pack(side=tk.LEFT, fill="both", expand=True)
ttk.Label(sentence_col, text="\n".join(speech_learning.SENTENCE_PROMPTS)).pack(anchor="w")
sentence_result = ReadOnlyText(sentence_col, height=len(speech_learning.SENTENCE_PROMPTS), width=60, wrap=tk.WORD)
sentence_result.pack(fill="x")

paragraph_frame = ttk.Frame(speech_tab)
paragraph_frame.pack(fill="x", padx=10, pady=5)
paragraph_btn = ttk.Button(paragraph_frame, text="Paragraph", command=run_paragraph)
paragraph_btn.pack(side=tk.LEFT, padx=(0, 5))
paragraph_col = ttk.Frame(paragraph_frame)
paragraph_col.pack(side=tk.LEFT, fill="both", expand=True)
ttk.Label(paragraph_col, text="\n".join(speech_learning.PARAGRAPH_PROMPTS)).pack(anchor="w")
paragraph_result = ReadOnlyText(paragraph_col, height=3, width=60, wrap=tk.WORD)
paragraph_result.pack(fill="x")


# ========== START VOICE LISTENERS & SCHEDULE THREADS ==========
wake_sleep_hotkey.start_hotkeys()
threading.Thread(
    target=start_voice_listener,
    args=(output, VOSK_MODEL_PATH, lambda: mic_hard_muted),  # UI output, model path, mic state
    daemon=True
).start()

# ========== SYSTEM TRAY ICON ==========
def make_icon_image():
    """Return a tray icon image or ``None`` if Pillow is unavailable."""
    if Image is None:
        return None
    img = Image.new("RGB", (64, 64), "black")
    draw = ImageDraw.Draw(img)
    draw.text((18, 24), "AI", fill="white")
    return img

def start_tray():
    def tray_start_listening(icon, item):
        set_listening(True)
        speak("I'm listening.")
        output.insert(tk.END, "\U0001F399\ufe0f Listening started via tray.\n")
        output.see("end")

    def tray_stop_listening(icon, item):
        set_listening(False)
        speak("Going to sleep.")
        output.insert(tk.END, "\U0001F634 Listening stopped via tray.\n")
        output.see("end")

    def tray_quit(icon, item):
        icon.stop()
        root.quit()
        os._exit(0)

    if pystray is None:
        print("[Tray] pystray not installed; system tray icon disabled")
        return
    icon = pystray.Icon(
        "assistant",
        make_icon_image(),
        "AI Assistant",
        menu=pystray.Menu(
            pystray.MenuItem("Show", lambda _: root.deiconify()),
            pystray.MenuItem("Hide", lambda _: root.withdraw()),
            pystray.MenuItem("Start Listening", tray_start_listening),
            pystray.MenuItem("Stop Listening", tray_stop_listening),
            pystray.MenuItem("Quit", tray_quit)
        )
    )
    icon.run()

if pystray is not None:
    threading.Thread(target=start_tray, daemon=True).start()

# ========== WELCOME MESSAGE ==========
output.insert(tk.END, "Assistant: Welcome to your local AI assistant! Speak or type your prompt.\n")
output.insert(tk.END, "Assistant: Try: capture region 100 200 300 300  | click image red_button.png\n\n")

# ========= Watcher Thread ========
def start_config_watcher():
    if not WATCHDOG_AVAILABLE:
        print("[ConfigWatcher] watchdog not available; config auto-reload disabled")
        return
    config_path = "config.json"
    handler = ConfigFileChangeHandler(reload_callback=reload_config, config_path=config_path)
    observer = Observer()
    observer.schedule(handler, path=".", recursive=False)
    observer.start()
    print("[ConfigWatcher] Watching for config changes...")
    # Keep observer running (background)
    while True:
        time.sleep(1)

# Start watcher thread if watchdog is available
if WATCHDOG_AVAILABLE:
    threading.Thread(target=start_config_watcher, daemon=True).start()

# ========== MAINLOOP ==========
root.mainloop()
