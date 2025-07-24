# ========== IMPORTS ==========
import tkinter as tk
from tkinter import ttk
try:
    from PIL import Image, ImageDraw, ImageTk  # type: ignore
except Exception:  # Pillow is optional
    Image = ImageDraw = ImageTk = None  # type: ignore

import threading
import os
import sys
import json
import time
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
try:
    import pystray
except Exception:  # pystray is optional
    pystray = None

# ========== RESOURCE PATH & CONFIG ==========
VOSK_MODEL_PATH = resource_path("vosk-model-small-en-us-0.15")
config_loader = ConfigLoader()
config = config_loader.config


# ========== TKINTER GUI SETUP ==========
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
notebook.add(main_tab, text="Assistant")
notebook.add(speech_tab, text="Speech Learning")
notebook.add(config_tab, text="Config Editor")
notebook.add(hotkey_tab, text="Hotkeys")

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

# Main output console
output = tk.Text(frame, height=20, wrap=tk.WORD)
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
    errors = validate_config(config)
    if errors:
        output.insert(tk.END, "[CONFIG VALIDATION ERROR]\n" + "\n".join(errors) + "\n")
        speak("Reload failed due to config error.")
    else:
        output.insert(tk.END, "[SYSTEM] Config reloaded and validated!\n")
        speak("Configuration has been reloaded.")

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
        macro_status.after(
            0, lambda: macro_status.config(text=f"Saved to {path}")
        )

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

# ---------- Speech Learning Tab ----------
speech_label = ttk.Label(speech_tab, text="Click Start and read each sentence aloud:")
speech_label.pack(pady=(10, 5))

speech_results = tk.Text(speech_tab, height=10, width=60, wrap=tk.WORD)
speech_results.pack(padx=10, pady=5)

def run_speech_training():
    speech_results.delete("1.0", tk.END)
    results = speech_learning.read_sentences(speak_func=tts_module.speak)
    for prompt, heard in zip(speech_learning.DEFAULT_SENTENCES, results):
        speech_results.insert(tk.END, f"Prompt: {prompt}\nHeard: {heard}\n\n")

start_train_btn = ttk.Button(speech_tab, text="Start Training", command=run_speech_training)
start_train_btn.pack(pady=5)

# ========== START VOICE LISTENERS & SCHEDULE THREADS ==========
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
