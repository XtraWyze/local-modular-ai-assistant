@echo off
REM Ensure commands run from this script's directory
pushd %~dp0

REM Activate the virtual environment from project root
call ..\venv\Scripts\activate

REM Run the example test script
python test_full_run.py

popd

REM Keep the window open so you can read the output
pause
