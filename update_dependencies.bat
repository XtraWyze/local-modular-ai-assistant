@echo off
REM Update requirements.txt based on module REQUIREMENTS and install them
cd /d "%~dp0"
python update_dependencies.py
pause
