"""
KAVACH 5.0 - Permissions Manager
Enforces strict consent-based operational boundaries for local Windows security assessment.
If permission is denied for a category: NO COLLECTION, NO SCANNING, NO FAKE RESULTS.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field

class PermissionDetail(BaseModel):
    id: str
    name: str
    granted: bool = False
    what_accessed: str
    why_needed: str
    checks_enabled: str
    admin_required: bool = False

DEFAULT_PERMISSIONS: Dict[str, Dict[str, Any]] = {
    "files": {
        "id": "files",
        "name": "Files & Selected Folders",
        "granted": False,
        "what_accessed": "Only user-selected files, directories, and explicitly approved audit locations.",
        "why_needed": "Analyze file metadata, integrity hashes, secret patterns, and dependency configurations.",
        "checks_enabled": "SHA-256 integrity, hardcoded secrets pattern detection, outdated dependency manifests, extension anomalies.",
        "admin_required": False
    },
    "processes": {
        "id": "processes",
        "name": "Running Processes",
        "granted": False,
        "what_accessed": "Process list via standard Windows APIs (PID, name, executable path, command line where accessible).",
        "why_needed": "Identify processes executing from insecure temporary paths or with unquoted service paths.",
        "checks_enabled": "Temp-directory execution checks, unquoted executable binary paths, publisher signature audit.",
        "admin_required": False
    },
    "installed_apps": {
        "id": "installed_apps",
        "name": "Installed Applications",
        "granted": False,
        "what_accessed": "Windows Registry Uninstall keys (HKLM/HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall).",
        "why_needed": "Audit software inventory against local CVE/CWE vulnerability intelligence dictionaries.",
        "checks_enabled": "Software version identification, known CVE vulnerability correlation, patch level analysis.",
        "admin_required": False
    },
    "startup_items": {
        "id": "startup_items",
        "name": "Startup Items & Services",
        "granted": False,
        "what_accessed": "Windows Startup folders and standard Registry Run keys (HKCU & HKLM).",
        "why_needed": "Inspect persistence items configured to execute automatically on user logon.",
        "checks_enabled": "Unquoted startup paths, missing executable targets, unauthorized script autorun entries.",
        "admin_required": False
    },
    "network": {
        "id": "network",
        "name": "Network Information & Listeners",
        "granted": False,
        "what_accessed": "Local network adapter properties, active TCP/UDP listening ports, and binding addresses.",
        "why_needed": "Detect insecure or unencrypted services bound to all interfaces (0.0.0.0).",
        "checks_enabled": "Cleartext listener detection (Telnet, HTTP, unauthenticated databases), open service mapping.",
        "admin_required": False
    },
    "system_security": {
        "id": "system_security",
        "name": "System Security Configuration",
        "granted": False,
        "what_accessed": "Windows UAC status, Windows Firewall profile status, and Defender state via non-intrusive APIs.",
        "why_needed": "Validate whether baseline operating system defensive guardrails are active.",
        "checks_enabled": "UAC EnableLUA verification, Firewall profile enablement, baseline host security posture.",
        "admin_required": False
    }
}

class PermissionsManager:
    def __init__(self):
        self._permissions: Dict[str, PermissionDetail] = {
            k: PermissionDetail(**v) for k, v in DEFAULT_PERMISSIONS.items()
        }

    def get_all_permissions(self) -> List[PermissionDetail]:
        return list(self._permissions.values())

    def get_permission(self, category_id: str) -> PermissionDetail:
        if category_id not in self._permissions:
            raise ValueError(f"Unknown permission category: {category_id}")
        return self._permissions[category_id]

    def is_granted(self, category_id: str) -> bool:
        if category_id not in self._permissions:
            return False
        return self._permissions[category_id].granted

    def set_permission(self, category_id: str, granted: bool) -> PermissionDetail:
        if category_id not in self._permissions:
            raise ValueError(f"Unknown permission category: {category_id}")
        self._permissions[category_id].granted = granted
        return self._permissions[category_id]

    def set_multiple(self, permissions_map: Dict[str, bool]) -> List[PermissionDetail]:
        for k, v in permissions_map.items():
            if k in self._permissions:
                self._permissions[k].granted = bool(v)
        return self.get_all_permissions()

    def reset_all(self):
        for p in self._permissions.values():
            p.granted = False

# Global singleton for the session
permissions_manager = PermissionsManager()
