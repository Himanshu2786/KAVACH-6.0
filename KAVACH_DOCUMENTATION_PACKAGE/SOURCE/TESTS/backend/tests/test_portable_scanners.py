"""
KAVACH 5.0 - Test Suite for Portable Windows Scanners and Consent Enforcement
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.scanners import (
    permissions_manager,
    file_scanner,
    process_scanner,
    software_scanner,
    startup_scanner,
    network_scanner,
    system_security_scanner
)

client = TestClient(app)

def test_permissions_manager_default_and_updates():
    """Verify permissions manager defaults and update logic."""
    permissions_manager.reset_all()
    assert not permissions_manager.is_granted("files")
    assert not permissions_manager.is_granted("processes")
    assert not permissions_manager.is_granted("installed_apps")

    # Grant files only
    permissions_manager.set_permission("files", True)
    assert permissions_manager.is_granted("files")
    assert not permissions_manager.is_granted("processes")

    # Reset
    permissions_manager.reset_all()
    assert not permissions_manager.is_granted("files")

def test_file_scanner_on_demo_training_samples():
    """Verify file scanner on safe demo training artifacts."""
    sample_dir = os.path.join(os.getcwd(), "demo", "training_samples")
    assert os.path.exists(sample_dir), "Demo training samples directory must exist"

    results = file_scanner.scan_path(sample_dir)
    assert results["status"] == "COMPLETED"
    assert results["scanned_count"] > 0
    assert len(results["findings"]) > 0

    # Inspect finding structure
    finding = results["findings"][0]
    assert "id" in finding
    assert "title" in finding
    assert "evidence" in finding
    assert "integrity_hash" in finding["evidence"]
    assert "terminal_verification" in finding
    assert "command" in finding["terminal_verification"]
    assert "remediation" in finding

def test_process_scanner_read_only():
    """Verify process scanner safely lists active processes."""
    results = process_scanner.scan_processes(max_processes=50)
    assert results["status"] == "COMPLETED"
    assert results["scanned_count"] > 0
    assert "processes_sample" in results

def test_software_scanner_audit():
    """Verify installed software scanner runs and categorizes software."""
    results = software_scanner.scan_software()
    assert results["status"] == "COMPLETED"
    assert results["scanned_count"] >= 0
    assert "summary" in results

def test_startup_scanner_audit():
    """Verify startup scanner inspects startup locations without modifying files."""
    results = startup_scanner.scan_startup()
    assert results["status"] == "COMPLETED"
    assert results["scanned_count"] >= 0

def test_network_scanner_audit():
    """Verify network scanner inspects interfaces and listening sockets."""
    results = network_scanner.scan_network()
    assert results["status"] == "COMPLETED"
    assert "interfaces" in results
    assert "listeners_sample" in results

def test_system_security_scanner_audit():
    """Verify system security scanner checks baseline UAC and Firewall."""
    results = system_security_scanner.scan_system_security()
    assert results["status"] == "COMPLETED"
    assert "checks" in results

def test_api_permission_denial_enforces_zero_collection():
    """
    CRITICAL GOLDEN RULE TEST:
    If permissions are denied: NO COLLECTION, NO SCANNING, NO FAKE RESULTS.
    Shows: 'Not scanned — permission not granted.'
    """
    # 1. Reset permissions
    client.post("/api/portable/permissions", json={
        "permissions": {
            "files": False,
            "processes": False,
            "installed_apps": False,
            "startup_items": False,
            "network": False,
            "system_security": False
        }
    })

    # 2. Run scan
    res = client.post("/api/portable/scan", json={"target_folder": "demo/training_samples"})
    assert res.status_code == 200
    data = res.json()["results"]

    # All module summaries must report DENIED with zero findings
    for mod_name, mod_info in data["module_summaries"].items():
        assert mod_info["status"] == "DENIED"
        assert mod_info["summary"] == "Not scanned — permission not granted."
        assert mod_info["findings_count"] == 0

    assert len(data["findings"]) == 0

def test_api_permission_granted_executes_scanners():
    """Verify that when files permission is granted, files are scanned."""
    # Grant files and network
    client.post("/api/portable/permissions", json={
        "permissions": {
            "files": True,
            "processes": False,
            "installed_apps": False,
            "startup_items": False,
            "network": True,
            "system_security": False
        }
    })

    res = client.post("/api/portable/scan", json={"target_folder": "demo/training_samples"})
    assert res.status_code == 200
    data = res.json()["results"]

    # Files must be COMPLETED
    assert data["module_summaries"]["files"]["status"] == "COMPLETED"
    assert data["module_summaries"]["network"]["status"] == "COMPLETED"
    # Denied categories remain denied
    assert data["module_summaries"]["processes"]["status"] == "DENIED"
    assert data["module_summaries"]["installed_apps"]["status"] == "DENIED"
