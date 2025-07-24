@echo off
REM Clone LocalAI, text-generation-webui, and Ollama repositories
cd /d "%~dp0"
py install_llm_backends.py --all
pause
