import os
import sys
import glob
import re
import json
from pathlib import Path

repo_root = Path(".").resolve()

def analyze_all():
    print("=== SEARCHING TODOS / FIXMES / BUGS IN CODEBASE ===")
    for ext in ["*.py", "*.ts", "*.tsx"]:
        for f in repo_root.rglob(ext):
            if any(p in str(f) for p in ["node_modules", ".git", ".pytest_cache", "dist", "build"]):
                continue
            with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                for idx, line in enumerate(fp, 1):
                    if any(w in line for w in ["TODO", "FIXME", "BUG", "HACK", "XXX", "KNOWN-BUG"]):
                        print(f"{f.relative_to(repo_root)}:{idx} -> {line.strip()}")

    print("\n=== SEARCHING VERIFICATION COMMANDS IN REPO ===")
    commands = []
    for f in repo_root.rglob("*.py"):
        if any(p in str(f) for p in ["node_modules", ".git", ".pytest_cache", "dist", "build"]):
            continue
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
        matches = re.findall(r'(?:verification_command|command_executed|reproduction_command)[\'\"]?\s*[:=]\s*[\'\"]([^\'\"]+)[\'\"]', content)
        for m in matches:
            commands.append((str(f.relative_to(repo_root)), m))
        curl_matches = re.findall(r'[\'\"\(](curl\s+[^;\'\"\)\n]+)[\'\" \)]', content)
        for c in curl_matches:
            commands.append((str(f.relative_to(repo_root)), c))

    print(f"Total commands found: {len(commands)}")
    for file, cmd in set(commands):
        print(f"[{file}] -> {cmd}")

if __name__ == "__main__":
    analyze_all()
