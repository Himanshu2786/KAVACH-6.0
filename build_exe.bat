@echo off
REM ============================================================================
REM KAVACH 6.0 Desktop — Windows Executable Build Script
REM Builds a standalone, portable desktop distribution in dist\KAVACH\
REM ============================================================================

echo [KAVACH] Starting PyInstaller Build...
python -m PyInstaller --clean --noconfirm KAVACH.spec

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================================
    echo [SUCCESS] KAVACH.exe successfully compiled!
    echo Distribution folder: dist\KAVACH\
    echo You can now copy the complete dist\KAVACH\ folder to any Windows machine.
    echo ============================================================================
) else (
    echo.
    echo [ERROR] Build failed. Review PyInstaller output above.
)
pause
