import datetime
import os
import threading

_LOGFILE = "assistant_errors.log"
_LOGLOCK = threading.Lock()

def log_error(message, context=None, level="ERROR"):
    """
    Log an error (or info/warning) with timestamp and optional context.
    Args:
        message (str): The error or message to log.
        context (str, optional): More details or user input that caused it.
        level (str): 'ERROR', 'WARNING', 'INFO', etc.
    """
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{time_str}] [{level}] {message}"
    if context:
        log_entry += f" | Context: {context}"
    with _LOGLOCK:
        with open(_LOGFILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

def get_errors(level_filter=None, max_lines=100):
    """
    Read errors from log, optionally filtered by level, most recent first.
    Args:
        level_filter (str or list): Only return logs with this level(s).
        max_lines (int): Max lines to return (for long logs).
    Returns:
        List[str]: Lines from the log file.
    """
    if not os.path.exists(_LOGFILE):
        return []
    with open(_LOGFILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Reverse for most-recent-first
    lines = lines[::-1][:max_lines]
    if level_filter:
        if isinstance(level_filter, str):
            level_filter = [level_filter]
        lines = [l for l in lines if any(f"[{lvl}]" in l for lvl in level_filter)]
    return lines

def clear_errors():
    """Delete the log file."""
    with _LOGLOCK:
        if os.path.exists(_LOGFILE):
            os.remove(_LOGFILE)

def log_info(message, context=None):
    log_error(message, context=context, level="INFO")

def log_warning(message, context=None):
    log_error(message, context=context, level="WARNING")

# Optionally, a convenience print function for terminal/debug
def print_last_errors(n=10):
    errors = get_errors(max_lines=n)
    if errors:
        print("=== Last Errors ===")
        for line in errors:
            print(line.strip())
    else:
        print("No errors logged.")

# For command-line test/debug
if __name__ == "__main__":
    log_error("Example error for test", context="Testing context")
    log_info("Just an info message.")
    log_warning("Just a warning!", context="Demo")
    print_last_errors(5)
