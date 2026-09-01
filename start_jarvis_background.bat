@echo off
:: This script starts the Jarvis API Server in the background.
:: You can place a shortcut to this file in your Windows Startup folder:
:: Win + R -> shell:startup -> Paste shortcut here

cd /d "c:\abhyas\jarvis"

:: Start Ollama (minimized)
start /MIN ollama serve

:: Start Jarvis API visibly (using standard python.exe instead of pythonw)
start "Jarvis Server" venv\Scripts\python.exe server.py

:: Wait 10 seconds to give Jarvis and World Monitor time to boot up
timeout /t 10 /nobreak > NUL

:: Automatically open the Jarvis web interface in the default browser
start http://localhost:8000


