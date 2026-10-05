@echo off
setlocal enabledelayedexpansion
color 0B

title KAVACH - Development Launcher (FastAPI + Vite React)

set "PROJECT_ROOT=%~dp0"
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"
cd /d "%PROJECT_ROOT%"

echo ============================================================
echo      KAVACH - FULL STACK DEVELOPMENT LAUNCHER
echo      FastAPI Backend (8000) + React Three.js Web (5173)
echo ============================================================
echo.

:: Detect Python environment
set "PYTHON_EXE=python"
if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe"
    goto :python_found
)
if exist "%PROJECT_ROOT%\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%\venv\Scripts\python.exe"
    goto :python_found
)
if exist "%PROJECT_ROOT%\env\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%\env\Scripts\python.exe"
    goto :python_found
)

:python_found

:: 0. Check and Start Ollama AI Engine (Port 11434)
echo [0/3] Checking Local Ollama AI Engine on http://127.0.0.1:11434 ...
powershell -Command "$c = New-Object Net.Sockets.TcpClient; try { $c.Connect('127.0.0.1', 11434); Write-Output 'ONLINE' } catch { Write-Output 'OFFLINE' } finally { $c.Close() }" | findstr /i "ONLINE" >nul
if not errorlevel 1 goto :ollama_online

echo [Ollama] Ollama service not detected on port 11434. Starting Ollama...
set "OLLAMA_EXE="
if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
if not defined OLLAMA_EXE if exist "%ProgramFiles%\Ollama\ollama.exe" set "OLLAMA_EXE=%ProgramFiles%\Ollama\ollama.exe"
if not defined OLLAMA_EXE (
    where ollama >nul 2>&1
    if not errorlevel 1 set "OLLAMA_EXE=ollama"
)
if defined OLLAMA_EXE (
    start "Ollama AI Engine" /min "%OLLAMA_EXE%" serve
    echo [Ollama] Started Ollama service in background.
    ping 127.0.0.1 -n 3 >nul
    goto :ollama_done
)
echo [Ollama] Ollama binary not found. KAVACH will use deterministic rule engine.
goto :ollama_done

:ollama_online
echo [0/3] Ollama AI Engine is ONLINE on port 11434.

:ollama_done
echo.

:: 1. Start FastAPI Backend Service
echo [1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "KAVACH FastAPI Backend" cmd /k "cd /d "%PROJECT_ROOT%" && "%PYTHON_EXE%" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [*] Waiting for FastAPI Backend to be ready on port 8000...
powershell -NoProfile -Command "$sw = [Diagnostics.Stopwatch]::StartNew(); while ($sw.Elapsed.TotalSeconds -lt 15) { try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1', 8000); $c.Close(); Write-Host ' [FastAPI] Backend is ONLINE on port 8000!'; exit 0 } catch { Start-Sleep -Milliseconds 400 } }; Write-Host ' [FastAPI] Continuing...'"

:: 2. Start Vite React Frontend
echo [2/3] Starting Vite React Frontend on http://localhost:5173 ...
start "KAVACH Vite Frontend" cmd /k "cd /d "%PROJECT_ROOT%\frontend" && npm run dev -- --host 127.0.0.1 --port 5173"

echo [*] Waiting for Vite Frontend to be ready on port 5173...
powershell -NoProfile -Command "$sw = [Diagnostics.Stopwatch]::StartNew(); while ($sw.Elapsed.TotalSeconds -lt 12) { try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1', 5173); $c.Close(); Write-Host ' [Vite] Frontend is ONLINE on port 5173!'; exit 0 } catch { Start-Sleep -Milliseconds 300 } }; Write-Host ' [Vite] Continuing...'"

:: 3. Open Browser
echo [3/3] Opening KAVACH Web Dashboard in default browser...
start http://localhost:5173

echo.
echo ============================================================
echo   KAVACH Development Environment is Running!
echo   - Web Dashboard : http://localhost:5173
echo   - FastAPI API   : http://127.0.0.1:8000/api
echo   - Swagger Docs  : http://127.0.0.1:8000/docs
echo   - RAG Status    : http://127.0.0.1:8000/api/rag/status
echo ============================================================
echo.
pause
