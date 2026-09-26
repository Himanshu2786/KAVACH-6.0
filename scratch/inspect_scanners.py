import os
import sys
import inspect
from pathlib import Path

repo_root = Path(".").resolve()
sys.path.insert(0, str(repo_root))

def inspect_all_scanners():
    print("=== INSPECTING ALL BACKEND SCANNERS ===")
    import backend.app.scanners as sc_pkg
    from backend.app.scanners.file_scanner import file_scanner
    from backend.app.scanners.network_scanner import network_scanner
    from backend.app.scanners.permissions_manager import permissions_manager
    from backend.app.scanners.process_scanner import process_scanner
    from backend.app.scanners.software_scanner import software_scanner
    from backend.app.scanners.startup_scanner import startup_scanner
    from backend.app.scanners.system_security_scanner import system_security_scanner

    scanners = [
        ("file_scanner", file_scanner),
        ("network_scanner", network_scanner),
        ("permissions_manager", permissions_manager),
        ("process_scanner", process_scanner),
        ("software_scanner", software_scanner),
        ("startup_scanner", startup_scanner),
        ("system_security_scanner", system_security_scanner),
    ]

    for name, obj in scanners:
        print(f"\n--- {name} ({obj.__class__.__name__}) ---")
        for m in dir(obj):
            if not m.startswith("_"):
                attr = getattr(obj, m)
                if callable(attr):
                    sig = str(inspect.signature(attr))
                    doc = (inspect.getdoc(attr) or "").split("\n")[0]
                    print(f"  def {m}{sig}: {doc}")

if __name__ == "__main__":
    inspect_all_scanners()
