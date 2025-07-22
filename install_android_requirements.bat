@echo off
REM Install Android build dependencies
cd /d "%~dp0"
python -m pip install -r android_requirements.txt
pause

