"""Helper script to download local LLM backend frameworks."""
import argparse
import subprocess
import sys
from pathlib import Path

from error_logger import log_error

REPOS = {
    "localai": "https://github.com/go-skynet/LocalAI.git",
    "webui": "https://github.com/oobabooga/text-generation-webui.git",
    "ollama": "https://github.com/ollama/ollama.git",
}


def clone_repo(url: str, dest: Path) -> None:
    """Clone ``url`` into ``dest`` if it doesn't already exist."""
    if dest.exists():
        print(f"{dest} already exists, skipping clone")
        return
    try:
        subprocess.check_call(["git", "clone", "--depth", "1", url, str(dest)])
    except FileNotFoundError as e:
        log_error("Git executable not found", context=str(e))
        print("Git not found. Please install Git and ensure it is on your PATH.")
        sys.exit(1)


def main() -> None:
    """Clone LocalAI, text-generation-webui, and/or Ollama repositories."""
    parser = argparse.ArgumentParser(description="Download LLM backend frameworks")
    parser.add_argument("--localai", action="store_true", help="Clone LocalAI")
    parser.add_argument("--webui", action="store_true", help="Clone text-generation-webui")
    parser.add_argument("--ollama", action="store_true", help="Clone Ollama")
    parser.add_argument("--all", action="store_true", help="Clone all frameworks")
    args = parser.parse_args()

    if not any([args.localai, args.webui, args.ollama, args.all]):
        parser.print_help(sys.stderr)
        return

    if args.all or args.localai:
        clone_repo(REPOS["localai"], Path("LocalAI"))
    if args.all or args.webui:
        clone_repo(REPOS["webui"], Path("text-generation-webui"))
    if args.all or args.ollama:
        clone_repo(REPOS["ollama"], Path("ollama"))

    print("Frameworks downloaded. See each repo's README for build instructions.")


if __name__ == "__main__":
    main()
