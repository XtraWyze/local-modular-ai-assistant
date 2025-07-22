@echo off
REM Build the Android APK using Buildozer (see BUILD_ANDROID.md)
cd /d "%~dp0"
call venv\Scripts\activate
python build_apk.py
pause
