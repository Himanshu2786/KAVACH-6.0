import os
import json
from pathlib import Path

ROOT = Path(r"c:\Users\Himanshu Raj\OneDrive\Desktop\KHAALI KAVACH\KAVACH 6.0")

IGNORE_DIRS = {".git", "node_modules", ".pytest_cache", "__pycache__", ".vscode", "dist"}

def get_category(p: Path, rel: str) -> str:
    parts = rel.replace("\\", "/").split("/")
    first = parts[0]
    ext = p.suffix.lower()

    if first == "frontend":
        return "frontend"
    if first == "backend":
        return "backend"
    if first == "AI":
        return "AI"
    if first == "docs":
        return "docs"
    if first == "INFO":
        return "docs"
    if first == "KAVACH_DOCUMENTATION_PACKAGE":
        return "docs/legacy_package"
    if first == "..KAVACH_COMPLETE_PROJECT":
        return "legacy"
    if first == "reports":
        return "reports"
    if first == "scripts":
        return "scripts"
    if first == "tools":
        return "tools"
    if first == "deploy":
        return "deployment"
    if first == "scratch":
        return "scratch"
    if first == "core":
        return "desktop_core"
    if first == "services":
        return "desktop_services"
    if first == "app":
        return "desktop_app"
    if first == "ui":
        return "desktop_ui"
    if first == "widgets":
        return "desktop_widgets"
    if first == "portable":
        return "portable"
    if first == "KAVACH_USB":
        return "portable_usb"
    if first == "demo":
        return "demo"
    if first == "build":
        return "build"
    if first == "logs":
        return "logs"

    # Root files
    if ext == ".md":
        return "docs"
    if ext in (".bat", ".ps1", ".sh"):
        return "scripts"
    if ext in (".yml", ".yaml"):
        return "deployment"
    if "dockerfile" in p.name.lower() or p.name in ("Caddyfile", ".env.example", ".env.production.example"):
        return "deployment"
    if p.name.startswith("test_") and ext == ".py":
        return "tests"
    if ext == ".db":
        return "database"
    if ext == ".spec":
        return "build"
    if p.name == "requirements.txt":
        return "build"
    if p.name == "main.py":
        return "desktop_entry"
    if p.name == ".gitignore":
        return "git"
    return "other"

inventory = []

for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
    for f in files:
        full_path = Path(root) / f
        try:
            rel = str(full_path.relative_to(ROOT))
        except ValueError:
            continue

        cat = get_category(full_path, rel)
        size = full_path.stat().st_size
        ext = full_path.suffix.lower()

        # Is root file?
        is_root = "\\" not in rel and "/" not in rel

        inventory.append({
            "rel_path": rel,
            "filename": f,
            "ext": ext,
            "size": size,
            "category": cat,
            "is_root": is_root
        })

print(f"Total inventory items (excluding node_modules/git/pycache): {len(inventory)}")
root_items = [i for i in inventory if i["is_root"]]
print(f"Total root items: {len(root_items)}")

by_cat = {}
for i in inventory:
    by_cat[i["category"]] = by_cat.get(i["category"], 0) + 1

for c, count in sorted(by_cat.items(), key=lambda x: -x[1]):
    print(f"  {c}: {count} files")

out_file = ROOT / "scratch" / "inventory_summary.json"
with open(out_file, "w", encoding="utf-8") as fp:
    json.dump({
        "total": len(inventory),
        "root_items": root_items,
        "categories": by_cat
    }, fp, indent=2)

print(f"Inventory saved to {out_file}")
