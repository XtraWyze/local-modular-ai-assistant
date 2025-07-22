# desktop_shortcuts.py

import os
import sys
import difflib
import subprocess
from typing import Iterable, Dict

__all__ = ["build_shortcut_map", "open_shortcut", "build_exe_map"]

def get_desktop_path():
    """Return the current user's Desktop directory."""
    if sys.platform == "win32":
        return os.path.join(os.path.expanduser("~"), "Desktop")
    else:
        # On Linux or Mac, adjust as needed
        return os.path.join(os.path.expanduser("~"), "Desktop")

def build_exe_map(search_dirs: Iterable[str] | None = None) -> Dict[str, str]:
    """Return mapping of executable names to absolute paths.

    If ``search_dirs`` is ``None``, standard Windows directories like
    ``ProgramFiles`` and ``SystemRoot`` are scanned. The function walks each
    directory recursively and collects paths to ``.exe`` files keyed by their
    lowercase filename without the extension.
    """
    if search_dirs is None:
        search_dirs = [
            os.environ.get("ProgramFiles"),
            os.environ.get("ProgramFiles(x86)"),
            os.environ.get("SystemRoot"),
        ]

    exe_map: Dict[str, str] = {}
    for base in search_dirs:
        if not base or not os.path.exists(base):
            continue
        for root_dir, _dirs, files in os.walk(base):
            for file in files:
                if file.lower().endswith(".exe"):
                    key = os.path.splitext(file)[0].lower()
                    exe_map.setdefault(key, os.path.join(root_dir, file))
    return exe_map

def build_shortcut_map(desktop_path=None, include_system=False):
    """Return mapping of shortcut names to executable or shortcut paths.

    If ``include_system`` is ``True``, :func:`build_exe_map` is used to scan the
    system for executables and the results are merged into the returned mapping.
    """
    if desktop_path is None:
        desktop_path = get_desktop_path()
    shortcut_map: Dict[str, str] = {}
    if os.path.exists(desktop_path):
        for fname in os.listdir(desktop_path):
            if fname.endswith('.lnk'):
                key = fname[:-4].lower()  # Remove .lnk
                shortcut_map[key] = os.path.join(desktop_path, fname)
            elif fname.endswith('.url'):
                key = fname[:-4].lower()  # Web shortcuts
                shortcut_map[key] = os.path.join(desktop_path, fname)
    # Add any common apps here for direct launching
    shortcut_map.update({
        "notepad": r"C:\Windows\System32\notepad.exe",
        "calculator": r"C:\Windows\System32\calc.exe"
    })
    if include_system:
        shortcut_map.update(build_exe_map())
    return shortcut_map

def open_shortcut(command, shortcut_map=None, fuzzy=True):
    """
    Tries to open a desktop shortcut or known app matching the user's command.
    Returns a status message.
    """
    if shortcut_map is None:
        shortcut_map = build_shortcut_map()
    command = command.lower().replace("open ", "").replace("launch ", "").strip()

    # Find best match using fuzzy search
    possible_keys = list(shortcut_map.keys())
    match = None
    if fuzzy:
        matches = difflib.get_close_matches(command, possible_keys, n=1, cutoff=0.7)
        if matches:
            match = matches[0]
    if not match and command in shortcut_map:
        match = command

    if match:
        target = shortcut_map[match]
        if os.path.exists(target):
            try:
                if hasattr(os, "startfile"):
                    os.startfile(target)
                else:
                    if sys.platform == "darwin":
                        subprocess.Popen(["open", target])
                    else:
                        subprocess.Popen(["xdg-open", target])
                return f"Opening {match.title()}."
            except Exception as e:
                return f"Failed to open {match}: {e}"
        else:
            return f"Shortcut found but file does not exist: {target}"
    else:
        return "Sorry, I couldn't find a matching shortcut or app on your desktop."

def get_info():
    """Return metadata for module discovery."""
    return {
        "name": "desktop_shortcuts",
        "description": "Launch desktop shortcuts or common apps by name.",
        "functions": ["build_shortcut_map", "open_shortcut", "build_exe_map"],
    }


def get_description() -> str:
    """Return a short description of this module."""
    return "Find and open desktop shortcuts or common applications."


# Example usage for your assistant's main code:
if __name__ == "__main__":
    shortcut_map = build_shortcut_map()
    while True:
        cmd = input("Say something (e.g., 'Open Chrome'): ")
        print(open_shortcut(cmd, shortcut_map))
