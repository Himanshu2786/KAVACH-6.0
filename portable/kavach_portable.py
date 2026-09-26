"""
KAVACH 6.0 - Portable Windows Standalone Launcher (USB Edition)
Launches the embedded FastAPI backend on 127.0.0.1:8000 and auto-opens the default browser.
Can be executed directly from a USB drive or packaged into dist/KAVACH.exe via PyInstaller.
"""

import os
import sys
import time
import webbrowser
import threading
import uvicorn

# Fix working directory when running frozen inside PyInstaller bundle
if getattr(sys, 'frozen', False):
    basedir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    os.chdir(os.path.dirname(sys.executable))
else:
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(basedir)

if basedir not in sys.path:
    sys.path.insert(0, basedir)

from backend.app.main import app

def open_browser():
    """Wait for local server initialization then launch default web browser."""
    time.sleep(1.5)
    url = "http://127.0.0.1:8000"
    print(f"\n=======================================================")
    print(f"  KAVACH 6.0 — PORTABLE WINDOWS SECURITY ASSESSMENT")
    print(f"  USB EDITION — ACTIVE ON {url}")
    print(f"=======================================================\n")
    try:
        webbrowser.open(url)
    except Exception as ex:
        print(f"[!] Could not auto-launch browser: {ex}. Please open {url} manually.")

def main():
    print("[*] Initializing KAVACH 6.0 Portable Environment...")
    print(f"[*] Base Directory: {basedir}")
    print("[*] Enforcing Consent-Based Zero-Collection Boundaries...")
    print("[*] Starting Local Server on 127.0.0.1:8000...")

    # Start browser in background daemon thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Uvicorn server on loopback interface
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=False
    )

if __name__ == "__main__":
    main()
