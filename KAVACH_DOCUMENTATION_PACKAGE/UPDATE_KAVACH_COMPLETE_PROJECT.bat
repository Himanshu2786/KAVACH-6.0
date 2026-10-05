@echo off
setlocal enabledelayedexpansion
title KAVACH 6.0 - Self-Updating Project Documentation Package
color 0B
cls

echo ===============================================================================
echo        KAVACH 6.0 -- AUTONOMOUS DOCUMENTATION AND SOURCE SNAPSHOT UPDATER
echo ===============================================================================
echo.

:: 1. Detect Package Directory and Project Root dynamically
set "PACKAGE_DIR=%~dp0"
:: Remove trailing backslash if present
if "%PACKAGE_DIR:~-1%"=="\" set "PACKAGE_DIR=%PACKAGE_DIR:~0,-1%"

for %%I in ("%PACKAGE_DIR%\..") do set "PROJECT_ROOT=%%~fI"

echo [*] Detected Package Directory : %PACKAGE_DIR%
echo [*] Detected Project Root      : %PROJECT_ROOT%
echo.

:: 2. Detect Python executable
set "PYTHON_CMD="
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python"
    goto :RUN_UPDATER
)

where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=py -3"
    goto :RUN_UPDATER
)

:: Check common Windows Python installation paths
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :RUN_UPDATER
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :RUN_UPDATER
)
if exist "%ProgramFiles%\Python311\python.exe" (
    set "PYTHON_CMD=%ProgramFiles%\Python311\python.exe"
    goto :RUN_UPDATER
)

echo [X] ERROR: Python 3 executable could not be found in PATH or standard directories.
echo     Please ensure Python 3 is installed and added to your system PATH.
echo.
pause
exit /b 1

:RUN_UPDATER
echo [*] Using Python: %PYTHON_CMD%
echo [*] Executing updater script...
echo.

"%PYTHON_CMD%" "%PACKAGE_DIR%\tools\update_kavach_complete_project.py" --root "%PROJECT_ROOT%" --package "%PACKAGE_DIR%"

set "EXIT_CODE=%ERRORLEVEL%"
if %EXIT_CODE% neq 0 (
    echo.
    echo ===============================================================================
    echo [X] FAILED: Documentation package update failed with error code %EXIT_CODE%.
    echo ===============================================================================
    echo.
    pause
    exit /b %EXIT_CODE%
)

echo.
echo ===============================================================================
echo [V] SUCCESS: KAVACH 6.0 Documentation Package has been updated successfully!
echo     - Master Document : %PACKAGE_DIR%\..KAVACH_COMPLETE_PROJECT.md
echo     - File Manifest   : %PACKAGE_DIR%\PROJECT_FILE_MANIFEST.md
echo     - Curated Source  : %PACKAGE_DIR%\SOURCE\
echo     - Latest Snapshot : %PACKAGE_DIR%\SNAPSHOT\latest_update.json
echo ===============================================================================
echo.
pause
exit /b 0
