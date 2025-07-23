@echo off
REM Clone LocalAI and text-generation-webui repositories
cd /d "%~dp0"
py install_llm_backends.py --all
pause
