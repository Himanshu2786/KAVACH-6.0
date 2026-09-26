import os
import sys
import json
import re
from pathlib import Path

repo_root = Path(".").resolve()

def inspect_validation_service():
    path = repo_root / "backend" / "app" / "services" / "validation_service.py"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        print(f"=== VALIDATION SERVICE ({path}) ===")
        print(f.read())

def inspect_forensic_export():
    path = repo_root / "backend" / "app" / "services" / "forensic_export_service.py"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        print(f"=== FORENSIC EXPORT SERVICE ({path}) ===")
        print(f.read()[:2000])

def inspect_app_tsx():
    path = repo_root / "frontend" / "src" / "App.tsx"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        print(f"=== FRONTEND APP.TSX ===")
        print(f.read()[:2000])

if __name__ == "__main__":
    inspect_validation_service()
    inspect_forensic_export()
    inspect_app_tsx()
