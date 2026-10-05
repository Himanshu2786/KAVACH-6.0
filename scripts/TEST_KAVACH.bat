@echo off
setlocal EnableExtensions EnableDelayedExpansion

title KAVACH 6.0 — Automated Test Suite Runner

set "PROJECT_ROOT=%~dp0.."
for %%i in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fi"
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"
cd /d "%PROJECT_ROOT%"

echo ============================================================
echo           KAVACH 6.0 — AUTOMATED TEST SUITE
echo ============================================================
echo.

:: Detect Python
set "PYTHON_EXE=python"

if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe"
    echo [ENV] Using virtual environment (.venv)
    goto :python_found
)
if exist "%PROJECT_ROOT%\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%\venv\Scripts\python.exe"
    echo [ENV] Using virtual environment (venv)
    goto :python_found
)
if exist "%PROJECT_ROOT%\env\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%\env\Scripts\python.exe"
    echo [ENV] Using virtual environment (env)
    goto :python_found
)
echo [ENV] Using system Python

:python_found

echo.
echo [1/4] Running Desktop Application UI Suite...
echo ------------------------------------------------------------
"%PYTHON_EXE%" "%PROJECT_ROOT%\test_desktop_app.py"
set "TEST1_RES=%errorlevel%"

echo.
echo [2/4] Running Filesystem and Rule Scanner Suite...
echo ------------------------------------------------------------
"%PYTHON_EXE%" "%PROJECT_ROOT%\test_scanner_suite.py"
set "TEST2_RES=%errorlevel%"

echo.
echo [3/4] Running RAG Vector Intelligence and Grounding Suite...
echo ------------------------------------------------------------
"%PYTHON_EXE%" -m pytest "%PROJECT_ROOT%\backend\tests\test_rag.py" -v
set "TEST3_RES=%errorlevel%"

echo.
echo [4/4] Running Real World Monitor Assessment Suite (Enterprise VAPT)...
echo ------------------------------------------------------------
"%PYTHON_EXE%" -m pytest "%PROJECT_ROOT%\backend\tests\test_world_monitor_assessment.py" -v
set "TEST4_RES=%errorlevel%"

echo.
echo ============================================================
echo                    TEST SUITE RESULTS
echo ============================================================
if %TEST1_RES% equ 0 (
    echo  [PASS] Desktop Application UI Initialization
) else (
    echo  [FAIL] Desktop Application UI Initialization (Code: %TEST1_RES%)
)

if %TEST2_RES% equ 0 (
    echo  [PASS] Filesystem and Rule Scanner Suite
) else (
    echo  [FAIL] Filesystem and Rule Scanner Suite (Code: %TEST2_RES%)
)

if %TEST3_RES% equ 0 (
    echo  [PASS] RAG Vector Intelligence and Grounding Suite
) else (
    echo  [FAIL] RAG Vector Intelligence and Grounding Suite (Code: %TEST3_RES%)
)

if %TEST4_RES% equ 0 (
    echo  [PASS] Real World Monitor Assessment Suite (Enterprise VAPT)
) else (
    echo  [FAIL] Real World Monitor Assessment Suite (Code: %TEST4_RES%)
)
echo ============================================================
echo.
pause
