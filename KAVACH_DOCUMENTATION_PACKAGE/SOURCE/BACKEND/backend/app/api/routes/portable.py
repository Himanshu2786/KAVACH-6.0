"""
KAVACH 5.0 - Portable Windows Assessment API Routes
Endpoints for Permission Dashboard, Consent Enforcement, and Modular Local Scanners.
"""

import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...scanners import (
    permissions_manager,
    file_scanner,
    process_scanner,
    software_scanner,
    startup_scanner,
    network_scanner,
    system_security_scanner
)

router = APIRouter(prefix="/portable", tags=["Portable Windows Assessment"])

class PermissionUpdateRequest(BaseModel):
    permissions: Dict[str, bool]

class ScanExecutionRequest(BaseModel):
    target_folder: Optional[str] = "demo/training_samples"

# In-memory store for current portable assessment session
_latest_scan_results: Dict[str, Any] = {
    "status": "IDLE",
    "findings": [],
    "module_summaries": {},
    "timestamp": None
}

@router.get("/permissions")
def get_permissions():
    """Retrieve the current consent and permission state for all 6 categories."""
    perms = permissions_manager.get_all_permissions()
    return {
        "success": True,
        "permissions": [p.model_dump() for p in perms]
    }

@router.post("/permissions")
def update_permissions(req: PermissionUpdateRequest):
    """Update granted permissions explicitly approved by the user."""
    updated = permissions_manager.set_multiple(req.permissions)
    return {
        "success": True,
        "permissions": [p.model_dump() for p in updated]
    }

@router.post("/scan")
def execute_portable_assessment(req: ScanExecutionRequest):
    """
    Executes security assessment ONLY for categories where permission was explicitly granted.
    For any denied category: NO COLLECTION, NO SCANNING, NO FAKE RESULTS.
    """
    global _latest_scan_results
    all_findings = []
    module_summaries = {}

    # 1. Files Scanner
    if permissions_manager.is_granted("files"):
        folder = req.target_folder or "demo/training_samples"
        res = file_scanner.scan_path(folder)
        module_summaries["files"] = {
            "status": res["status"],
            "summary": res["summary"],
            "findings_count": len(res.get("findings", [])),
            "scanned_count": res.get("scanned_count", 0)
        }
        all_findings.extend(res.get("findings", []))
    else:
        module_summaries["files"] = {
            "status": "DENIED",
            "summary": "Not scanned — permission not granted.",
            "findings_count": 0,
            "scanned_count": 0
        }

    # 2. Process Scanner
    if permissions_manager.is_granted("processes"):
        res = process_scanner.scan_processes()
        module_summaries["processes"] = {
            "status": res["status"],
            "summary": res["summary"],
            "findings_count": len(res.get("findings", [])),
            "scanned_count": res.get("scanned_count", 0)
        }
        all_findings.extend(res.get("findings", []))
    else:
        module_summaries["processes"] = {
            "status": "DENIED",
            "summary": "Not scanned — permission not granted.",
            "findings_count": 0,
            "scanned_count": 0
        }

    # 3. Installed Applications Scanner
    if permissions_manager.is_granted("installed_apps"):
        res = software_scanner.scan_software()
        module_summaries["installed_apps"] = {
            "status": res["status"],
            "summary": res["summary"],
            "findings_count": len(res.get("findings", [])),
            "scanned_count": res.get("scanned_count", 0)
        }
        all_findings.extend(res.get("findings", []))
    else:
        module_summaries["installed_apps"] = {
            "status": "DENIED",
            "summary": "Not scanned — permission not granted.",
            "findings_count": 0,
            "scanned_count": 0
        }

    # 4. Startup Items Scanner
    if permissions_manager.is_granted("startup_items"):
        res = startup_scanner.scan_startup()
        module_summaries["startup_items"] = {
            "status": res["status"],
            "summary": res["summary"],
            "findings_count": len(res.get("findings", [])),
            "scanned_count": res.get("scanned_count", 0)
        }
        all_findings.extend(res.get("findings", []))
    else:
        module_summaries["startup_items"] = {
            "status": "DENIED",
            "summary": "Not scanned — permission not granted.",
            "findings_count": 0,
            "scanned_count": 0
        }

    # 5. Network Information Scanner
    if permissions_manager.is_granted("network"):
        res = network_scanner.scan_network()
        module_summaries["network"] = {
            "status": res["status"],
            "summary": res["summary"],
            "findings_count": len(res.get("findings", [])),
            "scanned_count": res.get("scanned_count", 0)
        }
        all_findings.extend(res.get("findings", []))
    else:
        module_summaries["network"] = {
            "status": "DENIED",
            "summary": "Not scanned — permission not granted.",
            "findings_count": 0,
            "scanned_count": 0
        }

    # 6. System Security Configuration Scanner
    if permissions_manager.is_granted("system_security"):
        res = system_security_scanner.scan_system_security()
        module_summaries["system_security"] = {
            "status": res["status"],
            "summary": res["summary"],
            "findings_count": len(res.get("findings", [])),
            "scanned_count": res.get("scanned_count", 0)
        }
        all_findings.extend(res.get("findings", []))
    else:
        module_summaries["system_security"] = {
            "status": "DENIED",
            "summary": "Not scanned — permission not granted.",
            "findings_count": 0,
            "scanned_count": 0
        }

    from backend.app.core.time import ist_isoformat
    _latest_scan_results = {
        "status": "COMPLETED",
        "findings": all_findings,
        "module_summaries": module_summaries,
        "timestamp": ist_isoformat()
    }

    return {
        "success": True,
        "results": _latest_scan_results
    }

@router.get("/results")
def get_portable_results():
    """Returns the latest local assessment findings and per-module summaries."""
    return {
        "success": True,
        "results": _latest_scan_results
    }

@router.get("/demo-samples")
def get_demo_samples():
    """Lists safe training samples available for demonstration."""
    sample_dir = "demo/training_samples"
    samples = []
    if os.path.exists(sample_dir):
        for f in os.listdir(sample_dir):
            full_p = os.path.join(sample_dir, f)
            if os.path.isfile(full_p):
                samples.append({
                    "name": f,
                    "path": full_p,
                    "size_bytes": os.path.getsize(full_p),
                    "label": "DEMO / TRAINING ARTIFACT"
                })
    return {
        "success": True,
        "sample_dir": sample_dir,
        "samples": samples
    }
