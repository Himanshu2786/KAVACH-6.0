@echo off
title KAVACH 6.0 - Generate Complete ChatGPT Snapshot
color 0B
cls

echo ===============================================================================
echo                KAVACH 6.0 - COMPLETE AI PROJECT SNAPSHOT GENERATOR
echo ===============================================================================
echo.
echo [*] Scanning repository and generating ..KAVACH_COMPLETE_PROJECT.md...
echo.

python tools\generate_chatgpt_snapshot.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [X] Failed to generate snapshot! Please verify Python is installed and accessible.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ===============================================================================
echo [V] SUCCESS: ..KAVACH_COMPLETE_PROJECT.md generated!
echo     You can now provide this single file to ChatGPT for 100%% complete context.
echo ===============================================================================
echo.
pause
