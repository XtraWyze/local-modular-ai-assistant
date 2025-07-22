@echo off
REM Build a standalone executable for the Local Modular AI Assistant

REM 1. Create a virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    py -3 -m venv venv
)

REM 2. Activate the virtual environment
call venv\Scripts\activate

REM 3. Install requirements and PyInstaller
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM 4. Build the executable using PyInstaller
pyinstaller gui_assistant.py ^
  --onefile --noconfirm ^
  --add-data "modules;modules" ^
  --add-data "vosk-model-small-en-us-0.15;vosk-model-small-en-us-0.15" ^
  --add-data "config.json;." ^
  --add-data "assistant_memory.json;." ^
  --icon icon.ico

pause
