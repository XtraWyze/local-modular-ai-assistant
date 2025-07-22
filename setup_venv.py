import os
import subprocess
import sys
from pathlib import Path


def run(cmd):
    """Run a shell command and exit on failure."""
    print(f"Running: {cmd}")
    subprocess.check_call(cmd, shell=True)


def main():
    project_root = Path(__file__).resolve().parent
    venv_dir = project_root / "venv"

    if not venv_dir.exists():
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])

    python_exe = venv_dir / ("Scripts" if os.name == "nt" else "bin") / (
        "python.exe" if os.name == "nt" else "python"
    )

    run(f'"{python_exe}" -m pip install --upgrade pip')
    run(f'"{python_exe}" -m pip install -r requirements.txt')
    print("Virtual environment setup complete.")


if __name__ == "__main__":
    main()
