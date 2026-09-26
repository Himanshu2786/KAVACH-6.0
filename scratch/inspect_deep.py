import os
import sys
import json
import re
from pathlib import Path

repo_root = Path(".").resolve()

def inspect_wmae():
    path = repo_root / "backend" / "app" / "services" / "world_monitor_assessment_engine.py"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    print(f"=== WORLD MONITOR ASSESSMENT ENGINE ({len(code.splitlines())} lines) ===")
    
    # Extract findings defined
    finding_matches = re.findall(r'(\{[^\{\}]*?"title":[^\{\}]*?\})', code, re.DOTALL)
    print(f"Found approximately {len(finding_matches)} finding templates / objects in code")

    # Look for command templates
    commands = re.findall(r'verification_command[\'\"]?\s*:\s*[\'\"]([^\'\"]+)[\'\"]', code)
    print(f"\nVerification Commands in WMAE ({len(commands)}):")
    for cmd in set(commands):
        print(f"  - {cmd}")

def inspect_cvss():
    print("\n=== CVSS & RISK ENGINE INSPECTION ===")
    rpath = repo_root / "backend" / "app" / "services" / "risk_service.py"
    with open(rpath, "r", encoding="utf-8", errors="ignore") as f:
        print("--- backend/app/services/risk_service.py ---")
        print(f.read()[:1500])

    rpath2 = repo_root / "core" / "risk_engine.py"
    with open(rpath2, "r", encoding="utf-8", errors="ignore") as f:
        print("--- core/risk_engine.py ---")
        print(f.read()[:1500])

def inspect_audit():
    print("\n=== AUDIT ENGINE INSPECTION ===")
    apath = repo_root / "backend" / "app" / "core" / "audit.py"
    with open(apath, "r", encoding="utf-8", errors="ignore") as f:
        print(f.read())

if __name__ == "__main__":
    inspect_wmae()
    inspect_cvss()
    inspect_audit()
