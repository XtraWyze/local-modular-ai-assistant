@echo off
REM Activate the virtual environment
call venv\Scripts\activate

REM Launch the CLI assistant
python cli_assistant.py

REM Keep the window open so you can read any output
pause
