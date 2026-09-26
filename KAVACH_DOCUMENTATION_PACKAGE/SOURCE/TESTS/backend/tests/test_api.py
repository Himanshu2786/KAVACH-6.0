try:
    import pytest
except ImportError:
    pytest = None

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.data.seed_data import seed_database
from backend.app.models.models import Finding

client = TestClient(app)

def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()
    yield

def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "AI Hypothesizes. Evidence Confirms." in data["tagline"]

def test_system_status():
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["backend_status"] == "ONLINE"
    assert "READY" in data["knowledge_engine"]

def test_ollama_health_offline_handling():
    """Verify system does not crash when Ollama is offline."""
    response = client.get("/api/system/ollama")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("online", "offline")
    assert "selected_model" in data

def test_system_geolocate_endpoint():
    """Verify real geolocation endpoint returns structured location without fabricating data."""
    response = client.get("/api/system/geolocate")
    assert response.status_code == 200
    data = response.json()
    assert "location_type" in data
    assert data["location_type"] in ("APPROXIMATE_NETWORK_LOCATION", "LOCATION_UNAVAILABLE", "LOCATION_DENIED")
    if data.get("success"):
        assert data["latitude"] is not None
        assert data["longitude"] is not None
        assert -90 <= data["latitude"] <= 90
        assert -180 <= data["longitude"] <= 180
    else:
        assert data["latitude"] is None
        assert data["longitude"] is None

def test_assessment_creation_scope_guard():
    # Attempt without authorization confirmation
    res_fail = client.post("/api/assessments", json={
        "name": "Unauthorized Target",
        "target_url": "http://example.com",
        "authorization_confirmed": False
    })
    assert res_fail.status_code == 400

    # Valid authorized creation
    res_ok = client.post("/api/assessments", json={
        "name": "Generic Assessment Target",
        "target_url": "https://example.com",
        "description": "Authorized security posture evaluation.",
        "environment": "Testing Environment",
        "scope": "Complete Web Platform Surface",
        "authorization_confirmed": True,
        "modules_enabled": ["API Security", "Security Headers"]
    })
    assert res_ok.status_code == 200
    asm = res_ok.json()
    assert asm["id"].startswith("ASM-")
    assert asm["status"] == "RUNNING"
    assert asm["current_stage"] == "DISCOVER"

def test_findings_retrieval():
    response = client.get("/api/findings?is_demo=true")
    assert response.status_code == 200
    findings = response.json()
    assert len(findings) >= 5
    first = findings[0]
    assert "id" in first
    assert "status" in first
    assert "base_severity" in first

def test_knowledge_correlation():
    response = client.get("/api/knowledge/correlate?category=Broken%20Access%20Control&title=IDOR")
    assert response.status_code == 200
    data = response.json()
    assert data["cwe"] is not None
    assert "CWE-639" in data["cwe"]["id"] or "CWE-284" in data["cwe"]["id"]
    assert data["owasp"] is not None

def test_ai_analysis_and_rule_based_fallback():
    # Ensure test finding status is POTENTIAL before analysis
    db = SessionLocal()
    f = db.query(Finding).filter(Finding.id == "KAV-2026-004").first()
    if f:
        f.status = "POTENTIAL"
        db.commit()
    db.close()

    # Test on finding KAV-2026-004 (potential auth issue)
    res = client.post("/api/findings/KAV-2026-004/analyze")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    # Verify hypothesis exists and confidence is numerical
    assert "security_hypothesis" in data["data"]["analysis"]
    assert float(data["data"]["analysis"]["confidence"]) > 0
    # Crucial Rule: AI hypothesis MUST NOT confirm vulnerability!
    updated = data["updated_finding"]
    assert updated["status"] != "CONFIRMED"

def test_evidence_validation_confirms_finding():
    # We create evidence for a finding and verify status transitions to CONFIRMED
    evd_res = client.post("/api/evidence", json={
        "finding_id": "KAV-2026-004",
        "evidence_type": "Authentication Behavior",
        "description": "Validation test confirmed server accepted forged unsigned JWT.",
        "raw_data": "GET /api/v1/auth/verify HTTP/1.1\nAuthorization: Bearer forged_token\nHTTP/1.1 200 OK",
        "validation_result": "CONFIRMED",
        "source": "PyTest Security Probe"
    })
    assert evd_res.status_code == 200
    evd = evd_res.json()
    assert len(evd["integrity_hash"]) == 64  # SHA-256 hash length

    # Now verify the finding has transitioned to CONFIRMED based on this evidence
    finding_res = client.get("/api/findings/KAV-2026-004")
    assert finding_res.status_code == 200
    assert finding_res.json()["status"] == "CONFIRMED"
    assert finding_res.json()["evidence_status"] == "VERIFIED"

def test_risk_prioritization_calculation():
    res = client.get("/api/risk/prioritization/ASM-DEMO-001")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 4
    # Highest priority item should be top of list
    assert items[0]["priority_score"] >= items[-1]["priority_score"]
    assert "explanation" in items[0]
    assert "summary_statement" in items[0]["explanation"]

def test_remediation_details():
    res = client.get("/api/remediation/KAV-2026-001")
    assert res.status_code == 200
    plan = res.json()
    assert "quick_fix" in plan
    assert "detailed_fix" in plan
    assert "code_sample" in plan

def test_report_generation():
    # JSON Report
    json_res = client.get("/api/reports/ASM-DEMO-001")
    assert json_res.status_code == 200
    rep = json_res.json()
    assert "executive_summary" in rep
    assert "prioritized_findings" in rep

    # HTML Printable Report
    html_res = client.get("/api/reports/ASM-DEMO-001/html")
    assert html_res.status_code == 200
    assert "text/html" in html_res.headers["content-type"]
    assert "KAVACH 6.0" in html_res.text
    assert "@media print" in html_res.text

def test_terminal_verification():
    res = client.get("/api/evidence/KAV-2026-001/terminal")
    assert res.status_code == 200
    data = res.json()
    assert data["assessment_id"] == "ASM-DEMO-001"
    assert data["evidence_id"].startswith("EVD-")
    assert "curl" in data["command"]
    assert data["expected_output"] != ""
    assert data["observed_output"] != ""
    assert data["integrity_hash"] != ""
    assert len(data["verification_steps"]) == 4

def test_re_verification():
    res = client.post("/api/evidence/KAV-2026-001/re-verify", json={
        "command_executed": "curl -i -s -k 'https://www.worldmonitor.app/api/v1/workspaces/ws-9921/sensitive'",
        "force_status": "RESOLVED"
    })
    assert res.status_code == 200
    rev = res.json()
    assert rev["finding_id"] == "KAV-2026-001"
    assert rev["new_status"] == "RESOLVED"
    assert "summary" in rev
    assert rev["output_after"] != ""
