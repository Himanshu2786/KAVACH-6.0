"""
KAVACH Test Suite: The 3 Real Security Detections
End-to-end verification through the full 8-step lifecycle:
  Scanner -> Observation -> SHA-256 Evidence -> Finding -> Simple Explanation -> Technical Evidence -> Remediation -> Re-verification
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.url_scanner_service import url_scanner_service
from backend.app.scanners.network_scanner import network_scanner
from backend.app.scanners.file_scanner import file_scanner

client = TestClient(app)


# =====================================================================
# DETECTION 1: Web Security (Missing Observable Security Headers & TLS)
# =====================================================================
@pytest.mark.anyio
async def test_detection_1_web_security_end_to_end():
    # 1. Scanner & Real Observation against local backend
    target = "http://127.0.0.1:8000"
    res = await url_scanner_service.assess_url(target)

    # 2. Verify Scanner executed successfully
    assert res["success"] is True
    assert res["target_url"] == target
    assert res["hostname"] == "127.0.0.1"
    assert res["supported_checks"] >= 6
    assert len(res["checks"]) >= 6

    # 3. Real Findings Generated
    findings = res["findings"]
    assert len(findings) > 0, "Web security scan must generate findings for unhardened HTTP endpoint"

    f1 = findings[0]
    # 4. Cryptographic SHA-256 Evidence
    assert "evidence" in f1
    evd = f1["evidence"]
    assert len(evd["integrity_hash"]) == 64, "Evidence hash must be 64-character SHA-256"
    assert evd["raw_observation"] is not None

    # 5. Simple Explanation
    assert "simple_evidence" in f1
    se = f1["simple_evidence"]
    assert "what_found" in se
    assert "where_found" in se
    assert "why_matters" in se
    assert "possible_impact" in se
    assert "what_you_can_do" in se

    # 6. Technical Evidence
    assert "technical_evidence" in f1
    te = f1["technical_evidence"]
    assert "scanner" in te
    assert "rule" in te
    assert "timestamp" in te

    # 7. Remediation
    assert "remediation" in f1
    rem = f1["remediation"]
    assert "how_to_fix" in rem
    assert "why_matters" in rem

    # 8. Re-verification
    reverify_res = await url_scanner_service.reverify_url(target)
    assert reverify_res["success"] is True
    assert "reverification" in reverify_res
    assert "rechecked_at" in reverify_res["reverification"]
    assert reverify_res["reverification"]["current_findings_count"] == len(findings)


# =====================================================================
# DETECTION 2: Network Exposure (Listening Network Service Assessment)
# =====================================================================
def test_detection_2_network_exposure_end_to_end():
    # 1. System Observation via OS psutil
    res = network_scanner.scan_network()
    assert res["status"] == "COMPLETED"
    assert "listeners_sample" in res
    assert "interfaces" in res

    # 2. Check listeners
    listeners = res["listeners_sample"]
    assert len(listeners) > 0, "System must have at least one active listening socket"

    # 3. Verify exposure findings calibration
    # Look for listening port 8000 or any discovered exposure
    findings = res["findings"]
    assert len(findings) > 0, "Network scanner must identify listening service exposures"

    # Find the exposure finding
    exposure_finding = None
    for f in findings:
        if "Service Exposure Detected" in f["title"]:
            exposure_finding = f
            break

    if exposure_finding:
        # 4. Calibration: Must NOT say "Port Vulnerability Detected"
        assert "Service Exposure Detected" in exposure_finding["title"]
        assert exposure_finding["status"] in ("NEEDS REVIEW", "CONFIRMED")
        assert "Port Vulnerability" not in exposure_finding["title"]

        # 5. Cryptographic SHA-256 Evidence
        assert "evidence" in exposure_finding
        assert len(exposure_finding["evidence"]["integrity_hash"]) == 64

        # 6. Simple Explanation
        assert "simple_evidence" in exposure_finding
        se = exposure_finding["simple_evidence"]
        assert "A listening port does not automatically mean a vulnerability exists" in se["why_matters"]
        assert "what_found" in se

        # 7. Technical Evidence
        assert "technical_evidence" in exposure_finding
        te = exposure_finding["technical_evidence"]
        assert te["protocol"] == "TCP"
        assert "port" in te
        assert "connection_state" in te
        assert te["connection_state"] == "LISTEN"

        # 8. Remediation
        assert "remediation" in exposure_finding
        assert "how_to_fix" in exposure_finding["remediation"]


# =====================================================================
# DETECTION 3: Suspicious File Indicator (Double Extension & Metadata)
# =====================================================================
def test_detection_3_suspicious_file_end_to_end():
    sample_dir = os.path.join(os.getcwd(), "demo", "training_samples")
    assert os.path.exists(sample_dir), "Sample directory must exist"

    # 1. File Observation & Metadata Extraction
    res = file_scanner.scan_path(sample_dir)
    assert res["status"] == "COMPLETED"
    assert res["scanned_count"] >= 4

    # 2. Locate Double Extension Finding
    suspicious_finding = None
    for f in res["findings"]:
        if "Double Extension Detected" in f["title"]:
            suspicious_finding = f
            break

    assert suspicious_finding is not None, "Scanner must detect suspicious double-extension file"
    assert "suspicious_invoice.pdf.exe" in suspicious_finding["title"]
    assert suspicious_finding["category"] == "Malware & Threat Indicators"
    assert suspicious_finding["severity"] == "HIGH"
    assert suspicious_finding["status"] == "CONFIRMED"

    # 3. Cryptographic SHA-256 Evidence
    evd = suspicious_finding["evidence"]
    assert len(evd["integrity_hash"]) == 64
    assert "Disguised Extension: .pdf" in evd["raw_observation"]
    assert "Executable Suffix: .exe" in evd["raw_observation"]

    # 4. Simple Explanation
    se = suspicious_finding["simple_evidence"]
    assert "deceptive double extension" in se["what_found"]
    assert "why_matters" in se
    assert "possible_impact" in se
    assert "what_you_can_do" in se

    # 5. Technical Evidence
    te = suspicious_finding["technical_evidence"]
    assert te["disguised_extension"] == ".pdf"
    assert te["executable_extension"] == ".exe"
    assert len(te["sha256"]) == 64
    assert te["rule"] == "FILE-SUSPICIOUS-DOUBLE-EXTENSION"

    # 6. Remediation & Verification Command
    assert "remediation" in suspicious_finding
    assert "terminal_verification" in suspicious_finding
    assert "Get-Item" in suspicious_finding["terminal_verification"]["command"]


# =====================================================================
# API Endpoints Test for All 3 Detections
# =====================================================================
def test_detection_api_routes():
    # Test URL Check API endpoint
    res_url = client.post("/api/url-check/scan", json={"url": "http://127.0.0.1:8000"})
    assert res_url.status_code == 200
    data_url = res_url.json()
    assert data_url["success"] is True
    assert "security_score" in data_url
    assert len(data_url["findings"]) > 0

    # Test URL Check latest
    res_latest = client.get("/api/url-check/latest")
    assert res_latest.status_code == 200
    assert res_latest.json()["success"] is True

    # Test URL Check re-verify
    res_rev = client.post("/api/url-check/re-verify", json={"url": "http://127.0.0.1:8000"})
    assert res_rev.status_code == 200
    assert "reverification" in res_rev.json()
