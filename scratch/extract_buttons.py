import os
import glob
import re
import sys
from pathlib import Path

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(".").resolve()

def extract_buttons():
    fe_files = list((repo_root / "frontend" / "src").rglob("*.tsx"))
    desktop_files = list((repo_root / "ui").glob("*.py")) + list((repo_root / "widgets").glob("*.py"))
    
    print("=== FRONTEND BUTTON INVENTORY ===")
    fe_buttons = []
    for f in sorted(fe_files):
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
        # Find button text or onClick handlers
        btns = re.findall(r'<button[^>]*>(.*?)</button>', content, re.DOTALL)
        for b in btns:
            clean_b = re.sub(r'<[^>]+>', '', b).strip()
            clean_b = re.sub(r'\{.*?\}', '', clean_b).strip()
            if clean_b and len(clean_b) < 60:
                fe_buttons.append((f.name, clean_b))
    
    for f, b in sorted(set(fe_buttons)):
        print(f"[{f}] {b}")

    print("\n=== DESKTOP BUTTON INVENTORY ===")
    dt_buttons = []
    for f in sorted(desktop_files):
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
        btns = re.findall(r'QPushButton\([\'\"]([^\'\"]+)[\'\"]\)', content)
        for b in btns:
            dt_buttons.append((f.name, b))
        btns2 = re.findall(r'setText\([\'\"]([^\'\"]+)[\'\"]\)', content)
        for b in btns2:
            if any(k in b.lower() for k in ["scan", "run", "verify", "export", "check", "assess", "refresh", "view", "details"]):
                dt_buttons.append((f.name, b))
    
    for f, b in sorted(set(dt_buttons)):
        print(f"[{f}] {b}")

if __name__ == "__main__":
    extract_buttons()
