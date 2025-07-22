import subprocess
import sys
from pathlib import Path


def main():
    """Install packages from requirements.txt using pip."""
    req_file = Path(__file__).with_name("requirements.txt")
    if not req_file.exists():
        print("requirements.txt not found", file=sys.stderr)
        sys.exit(1)
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(req_file)]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)


if __name__ == "__main__":
    main()
