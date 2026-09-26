import os
import sys
import glob
import json
import inspect
from pathlib import Path

repo_root = Path(".").resolve()

def analyze():
    print("=== 1. CHECKING TEST FILES ===")
    test_files = list(glob.glob("backend/tests/*.py")) + list(glob.glob("tests/*.py")) + list(glob.glob("test_*.py"))
    for tf in sorted(test_files):
        print(f"Test File: {tf}")
        with open(tf, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        test_defs = [l.strip() for l in lines if l.startswith("def test_")]
        for td in test_defs:
            print(f"  - {td}")

    print("\n=== 2. CHECKING BACKEND SCANNERS ===")
    scanners = glob.glob("backend/app/scanners/*.py")
    for sc in sorted(scanners):
        print(f"Scanner: {sc}")
        with open(sc, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("class ") or line.startswith("def "):
                    print(f"  {line.strip()}")

    print("\n=== 3. CHECKING DESKTOP UI PAGES ===")
    ui_pages = glob.glob("ui/*.py")
    for up in sorted(ui_pages):
        print(f"UI Page: {up}")
        with open(up, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("class ") or line.startswith("def __init__") or "def build" in line or "def init_ui" in line:
                    print(f"  {line.strip()}")

    print("\n=== 4. CHECKING BATCH & SHELL SCRIPTS ===")
    bat_files = list(glob.glob("*.bat")) + list(glob.glob("*.cmd")) + list(glob.glob("*.ps1"))
    for bf in sorted(bat_files):
        print(f"\n--- SCRIPT: {bf} ---")
        with open(bf, "r", encoding="utf-8", errors="ignore") as f:
            print(f.read())

if __name__ == "__main__":
    analyze()
