@echo off
REM Ensure we run from the script directory
cd /d "%~dp0"

REM Launch the GUI assistant
python gui_assistant.py

REM Keep the window open so you can read any output
pause
