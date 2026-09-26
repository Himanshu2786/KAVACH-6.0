@echo off
title KAVACH - Local Ollama AI Service Launcher
echo ====================================================================
echo                 KAVACH LOCAL AI SERVICE LAUNCHER
echo ====================================================================
echo.
echo Checking for local Ollama installation...

where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Ollama executable was not found in your system PATH.
    echo.
    echo Please install Ollama from https://ollama.com/download
    echo or ensure it is installed in:
    echo   %%LOCALAPPDATA%%\Programs\Ollama\ollama.exe
    echo.
    pause
    exit /b 1
)

echo [+] Ollama detected on system.
echo [*] Setting OLLAMA_ORIGINS=* for KAVACH browser/backend connectivity...
set OLLAMA_ORIGINS=*

echo [*] Starting local Ollama service on http://127.0.0.1:11434...
echo [*] Press CTRL+C at any time to stop the AI service.
echo.
ollama serve
