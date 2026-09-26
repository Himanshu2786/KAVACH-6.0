@echo off
setlocal EnableExtensions EnableDelayedExpansion
color 0A

title KAVACH 6.0 — Sovereign Security Intelligence Platform

:: Determine the exact directory where this batch file is located
set "PROJECT_ROOT=%~dp0"
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"
cd /d "%PROJECT_ROOT%"

echo ============================================================
echo         KAVACH 6.0 — ONE-CLICK APPLICATION LAUNCHER
echo          "AI Hypothesizes. Evidence Confirms."
echo ============================================================
echo.

:: 1. Discover Python Executable (Default to system 'python')
set "PYTHON_EXE=python"

if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe"
    echo [ENV] Using project virtual environment (.venv)
    goto :python_found
)
if exist "%PROJECT_ROOT%\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%\venv\Scripts\python.exe"
    echo [ENV] Using project virtual environment (venv)
    goto :python_found
)
if exist "%PROJECT_ROOT%\env\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%\env\Scripts\python.exe"
    echo [ENV] Using project virtual environment (env)
    goto :python_found
)
echo [ENV] Using system Python

:python_found

:: 2. Test if Python runs successfully
"%PYTHON_EXE%" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo [ERROR] Python is not installed or not found in system PATH.
    echo.
    echo KAVACH requires Python 3.10+ to run.
    echo Please install Python from: https://www.python.org/downloads/
    echo During installation, make sure to check:
    echo   [x] "Add Python to PATH"
    echo ============================================================
    echo.
    pause
    exit /b 1
)

:: 3. Launch KAVACH Python Startup Engine
echo [LAUNCH] Initiating KAVACH Security Platform...
echo.

"%PYTHON_EXE%" "%PROJECT_ROOT%\scripts\launch_kavach.py"

set "EXIT_CODE=%errorlevel%"

if %EXIT_CODE% neq 0 (
    echo.
    echo ============================================================
    echo [ERROR] KAVACH closed with an error (Code: %EXIT_CODE%).
    echo Detailed startup logs are available at:
    echo   %PROJECT_ROOT%\logs\kavach_launcher.log
    echo ============================================================
    echo.
    pause
)

exit /b %EXIT_CODE%
