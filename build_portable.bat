@echo off
echo =======================================================
echo   KAVACH 6.0 — PORTABLE WINDOWS BUILD SCRIPT
echo   Target Output: dist/KAVACH.exe
echo =======================================================

echo [1/3] Building Frontend Production Assets...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo [!] Frontend build failed. Aborting.
    exit /b %errorlevel%
)
cd ..

echo [2/3] Verifying Python Dependencies...
pip install -r backend/requirements.txt psutil pyinstaller

echo [3/3] Packaging Portable Standalone Executable with PyInstaller...
python -m PyInstaller portable/kavach.spec --noconfirm --clean
if %errorlevel% neq 0 (
    echo [!] PyInstaller packaging failed.
    exit /b %errorlevel%
)

echo =======================================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo   Executable generated at: dist\KAVACH.exe
echo   Copy dist\KAVACH.exe to your USB drive.
echo =======================================================
pause
