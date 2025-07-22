from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

class ConfigFileChangeHandler(FileSystemEventHandler):
    def __init__(self, reload_callback, config_path):
        """Initialize with the callback to run when ``config_path`` changes."""
        super().__init__()
        self.reload_callback = reload_callback
        self.config_path = config_path

    def on_modified(self, event):
        # Only reload if config file itself is touched
        if event.src_path.endswith(self.config_path):
            print("[ConfigWatcher] config.json modified, reloading...")
            self.reload_callback()

def start_watcher(config_path, reload_callback):
    """Start watching a config file for changes."""
    handler = ConfigFileChangeHandler(reload_callback, os.path.basename(config_path))
    observer = Observer()
    observer.schedule(handler, path=os.path.dirname(config_path) or ".", recursive=False)
    observer.start()
    return observer

def stop_watcher(observer):
    """Stop a previously started config watcher."""
    observer.stop()
    observer.join()
