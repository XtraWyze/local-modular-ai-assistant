@echo off
REM Install all Python dependencies
cd /d "%~dp0"
python -m pip install -r requirements.txt
pause
