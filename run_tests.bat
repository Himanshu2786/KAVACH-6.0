@echo off
title KAVACH Automated Test Suite
echo ===================================================
echo   Running KAVACH Automated Test Suite
echo ===================================================
echo.
python -m backend.tests.run_tests
echo.
pause
