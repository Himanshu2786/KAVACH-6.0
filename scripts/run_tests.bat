@echo off
title KAVACH Automated Test Suite
echo ===================================================
echo   Running KAVACH Automated Test Suite
echo ===================================================
echo.
cd /d "%~dp0.." && python -m backend.tests.run_tests
echo.
pause
