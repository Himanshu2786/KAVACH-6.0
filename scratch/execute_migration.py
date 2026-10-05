import os
import shutil
import sys
from pathlib import Path

ROOT = Path(r"c:\Users\Himanshu Raj\OneDrive\Desktop\KHAALI KAVACH\KAVACH 6.0")

migration_log = []

def record(old_path, new_path, status, notes=""):
    migration_log.append({
        "old_path": str(old_path),
        "new_path": str(new_path),
        "status": status,
        "notes": notes
    })
    print(f"[{status}] {old_path} -> {new_path} ({notes})")

def safe_move(src: Path, dst: Path, note=""):
    try:
        if not src.exists():
            record(src, dst, "SKIPPED_NOT_FOUND", note)
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        record(src, dst, "MOVED", note)
        return True
    except Exception as e:
        record(src, dst, "ERROR", f"{e}")
        return False

def safe_copy(src: Path, dst: Path, note=""):
    try:
        if not src.exists():
            record(src, dst, "SKIPPED_NOT_FOUND", note)
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(str(src), str(dst), dirs_exist_ok=True)
        else:
            shutil.copy2(str(src), str(dst))
        record(src, dst, "COPIED", note)
        return True
    except Exception as e:
        record(src, dst, "ERROR", f"{e}")
        return False

print("=== Starting Step 73 Controlled Migration ===")

# 1. Create target directories
for d in ["legacy", "docs", "tests", "scripts", "deployment", "data", "build"]:
    (ROOT / d).mkdir(parents=True, exist_ok=True)

# --- CATEGORY 1: LEGACY ---
print("\n--- Migrating Legacy Materials ---")
safe_move(ROOT / "..KAVACH_COMPLETE_PROJECT", ROOT / "legacy" / "..KAVACH_COMPLETE_PROJECT", "Legacy project directory")
safe_move(ROOT / "..KAVACH_COMPLETE_PROJECT.md", ROOT / "legacy" / "..KAVACH_COMPLETE_PROJECT.md", "Legacy project monolithic markdown")

# --- CATEGORY 2: ROOT DOCUMENTATION -> docs/ ---
print("\n--- Migrating Root Documentation to docs/ ---")
doc_files = [
    "CHALLENGES_TO_SOLUTIONS.md",
    "CLEANUP_CHANGELOG.md",
    "DEBUG_BASELINE.md",
    "DEPLOYMENT.md",
    "DOCUMENTATION_UPDATE_REPORT.md",
    "KAVACH_5_VALIDATION_REPORT.md",
    "KAVACH_BACKEND_ARCHITECTURE.md",
    "KAVACH_DEPENDENCIES.md",
    "KAVACH_DEVELOPER_DOCUMENTATION.md",
    "KAVACH_MASTER_CONTEXT.md",
    "PERMISSION_SYSTEM.md",
    "START_KAVACH_GUIDE.md",
    "TEAM_ACCOUNT_SYSTEM.md",
    "TEAM_ACTIVITY_TRACKING.md",
    "TEAM_WEB_DEPLOYMENT.md",
    "TEAM_WEB_GUIDE.md",
    "TEAM_WEB_IMPLEMENTATION_REPORT.md",
    "walkthrough.md"
]

for doc in doc_files:
    safe_move(ROOT / doc, ROOT / "docs" / doc, "Root documentation")

# --- CATEGORY 3: TESTS -> tests/ ---
print("\n--- Migrating Standalone Tests to tests/ ---")
safe_copy(ROOT / "test_desktop_app.py", ROOT / "tests" / "test_desktop_app.py", "Desktop app test")
safe_copy(ROOT / "test_scanner_suite.py", ROOT / "tests" / "test_scanner_suite.py", "Scanner suite test")

# Create root shims for backwards compatibility
with open(ROOT / "test_desktop_app.py", "w", encoding="utf-8") as f:
    f.write('"""Root compatibility shim for tests/test_desktop_app.py"""\nimport runpy, sys, os\nsys.path.insert(0, os.path.dirname(__file__))\nrunpy.run_path(os.path.join(os.path.dirname(__file__), "tests", "test_desktop_app.py"), run_name="__main__")\n')
record("root/test_desktop_app.py", "tests/test_desktop_app.py", "SHIMMED", "Backwards compatibility wrapper")

with open(ROOT / "test_scanner_suite.py", "w", encoding="utf-8") as f:
    f.write('"""Root compatibility shim for tests/test_scanner_suite.py"""\nimport runpy, sys, os\nsys.path.insert(0, os.path.dirname(__file__))\nrunpy.run_path(os.path.join(os.path.dirname(__file__), "tests", "test_scanner_suite.py"), run_name="__main__")\n')
record("root/test_scanner_suite.py", "tests/test_scanner_suite.py", "SHIMMED", "Backwards compatibility wrapper")

# In tests/test_desktop_app.py and tests/test_scanner_suite.py, ensure project root is in sys.path
for t_file in [ROOT / "tests" / "test_desktop_app.py", ROOT / "tests" / "test_scanner_suite.py"]:
    if t_file.exists():
        content = t_file.read_text(encoding="utf-8")
        if "PROJECT_ROOT" not in content and "sys.path.insert" not in content:
            header = 'import sys, os\nsys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))\n'
            t_file.write_text(header + content, encoding="utf-8")

# --- CATEGORY 4: SCRIPTS -> scripts/ ---
print("\n--- Migrating Scripts to scripts/ ---")
script_files = [
    "1.0 UPDATE CONTEXT.bat",
    "build_exe.bat",
    "build_exe.ps1",
    "build_portable.bat",
    "run_tests.bat",
    "START KAVACH 2.0 .bat",
    "TEST_KAVACH.bat"
]

for s in script_files:
    safe_copy(ROOT / s, ROOT / "scripts" / s, "Automation / launcher script")

# Update scripts/run_tests.bat and scripts/TEST_KAVACH.bat to reference root appropriately
run_tests_script = ROOT / "scripts" / "run_tests.bat"
if run_tests_script.exists():
    content = run_tests_script.read_text(encoding="utf-8")
    content = content.replace("python -m backend.tests.run_tests", 'cd /d "%~dp0.." && python -m backend.tests.run_tests')
    run_tests_script.write_text(content, encoding="utf-8")

test_kavach_script = ROOT / "scripts" / "TEST_KAVACH.bat"
if test_kavach_script.exists():
    content = test_kavach_script.read_text(encoding="utf-8")
    content = content.replace('set "PROJECT_ROOT=%~dp0"', 'set "PROJECT_ROOT=%~dp0.."\nfor %%i in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fi"')
    test_kavach_script.write_text(content, encoding="utf-8")

# Root shims for TEST_KAVACH.bat and run_tests.bat
with open(ROOT / "TEST_KAVACH.bat", "w", encoding="utf-8") as f:
    f.write('@echo off\ncall "%~dp0scripts\\TEST_KAVACH.bat" %*\n')

with open(ROOT / "run_tests.bat", "w", encoding="utf-8") as f:
    f.write('@echo off\ncall "%~dp0scripts\\run_tests.bat" %*\n')

# Remove duplicate scripts from root now that shims exist
for s in ["1.0 UPDATE CONTEXT.bat", "build_exe.bat", "build_exe.ps1", "build_portable.bat", "START KAVACH 2.0 .bat"]:
    try:
        (ROOT / s).unlink(missing_ok=True)
        record(ROOT / s, ROOT / "scripts" / s, "MOVED_TO_SCRIPTS", "Removed redundant root copy")
    except Exception as e:
        print(f"Notice: {s}: {e}")

# --- CATEGORY 5: DEPLOYMENT -> deployment/ ---
print("\n--- Populating deployment/ ---")
safe_copy(ROOT / "Dockerfile.backend", ROOT / "deployment" / "Dockerfile.backend", "Backend Dockerfile")
safe_copy(ROOT / "Dockerfile.frontend", ROOT / "deployment" / "Dockerfile.frontend", "Frontend Dockerfile")
safe_copy(ROOT / "Caddyfile", ROOT / "deployment" / "Caddyfile", "Reverse proxy Caddyfile")
safe_copy(ROOT / "deploy" / "nginx-frontend.conf", ROOT / "deployment" / "nginx-frontend.conf", "Nginx config")
safe_copy(ROOT / ".env.example", ROOT / "deployment" / ".env.example", "Environment example")
safe_copy(ROOT / ".env.production.example", ROOT / "deployment" / ".env.production.example", "Production env example")
safe_copy(ROOT / "docker-compose.yml", ROOT / "deployment" / "docker-compose.yml", "Docker Compose stack definition")

# --- CATEGORY 6: BUILD -> build/ ---
print("\n--- Populating build/ ---")
safe_copy(ROOT / "KAVACH.spec", ROOT / "build" / "KAVACH.spec", "PyInstaller spec")
safe_copy(ROOT / "requirements.txt", ROOT / "build" / "requirements.txt", "Root requirements definition")

# --- CATEGORY 7: DATA -> data/ ---
print("\n--- Populating data/ ---")
data_readme = ROOT / "data" / "README.md"
data_readme.write_text(
    "# KAVACH 6.0 — Database & Data Architecture\n\n"
    "This directory documents the persistent data models and stores for KAVACH 6.0.\n\n"
    "## Storage Architecture\n"
    "- **Runtime SQLite Database**: `kavach.db` (Located at repository root for live local execution and dual-client sync)\n"
    "- **Production Database**: PostgreSQL (Configured via `DATABASE_URL`)\n"
    "- **Data Seeds**: `backend/app/data/seed_data.py`\n"
    "- **ORM Schemas**: `backend/app/schemas/schemas.py` and `backend/app/models/models.py`\n",
    encoding="utf-8"
)
record("data/README.md", "data/README.md", "CREATED", "Data architecture documentation")

# --- CATEGORY 8: UPDATE .gitignore ---
print("\n--- Updating .gitignore ---")
gitignore_path = ROOT / ".gitignore"
if gitignore_path.exists():
    gi_content = gitignore_path.read_text(encoding="utf-8")
    if "legacy/..KAVACH_COMPLETE_PROJECT.md" not in gi_content:
        gi_content += "\n# Legacy monolithic documentation snapshots\nlegacy/..KAVACH_COMPLETE_PROJECT.md\n"
        gitignore_path.write_text(gi_content, encoding="utf-8")
        record(".gitignore", ".gitignore", "UPDATED", "Added legacy path exclusion")

# Save migration manifest
manifest_path = ROOT / "scratch" / "migration_manifest.json"
import json
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(migration_log, f, indent=2)

print(f"\nMigration complete. Manifest written to {manifest_path}")
