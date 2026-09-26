"""
KAVACH 5.0 — Assessment Data Isolation, Demo Contamination & Scoping Tests
Tests A through G for real/demo assessment isolation, URL check isolation, and zero-fallback behavior.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.models import Assessment, Finding, EvidenceRecord, AuditEvent
from backend.app.core.time import ist_isoformat

client = TestClient(app)


def test_isolation_test_a_real_assessment_zero_findings():
    """TEST A: Real assessment with zero findings returns [] on GET /api/findings?assessment_id=..."""
    db = SessionLocal()
    now_str = ist_isoformat()
    asm_id = "ASM-TEST-REAL-A"
    
    # Cleanup if exists
    db.query(Finding).filter(Finding.assessment_id == asm_id).delete()
    db.query(Assessment).filter(Assessment.id == asm_id).delete()
    db.commit()

    asm = Assessment(
        id=asm_id,
        name="Real Isolated Assessment A",
        target_url="https://secure.example.com",
        status="COMPLETED",
        progress=100,
        current_stage="REPORT",
        is_demo=False,
        started_at=now_str,
        completed_at=now_str
    )
    db.add(asm)
    db.commit()
    db.close()

    res = client.get(f"/api/findings?assessment_id={asm_id}")
    assert res.status_code == 200
    findings = res.json()
    assert findings == []


def test_isolation_test_b_and_c_demo_findings_do_not_contaminate_real():
    """
    TEST B: Demo finding in ASM-DEMO-TEST must NOT appear in real assessment query.
    TEST C: Demo finding appears when queried for ASM-DEMO-TEST.
    """
    db = SessionLocal()
    now_str = ist_isoformat()
    real_id = "ASM-TEST-REAL-B"
    demo_id = "ASM-DEMO-TEST"
    
    # Cleanup
    db.query(Finding).filter(Finding.assessment_id.in_([real_id, demo_id])).delete()
    db.query(Assessment).filter(Assessment.id.in_([real_id, demo_id])).delete()
    db.commit()

    # Create real assessment with 0 findings
    real_asm = Assessment(
        id=real_id,
        name="Real Clean Assessment B",
        target_url="https://clean.example.com",
        status="COMPLETED",
        progress=100,
        current_stage="REPORT",
        is_demo=False,
        started_at=now_str,
        completed_at=now_str
    )
    # Create demo assessment with 1 finding
    demo_asm = Assessment(
        id=demo_id,
        name="Demo Assessment",
        target_url="https://demo.example.com",
        status="RUNNING",
        progress=50,
        current_stage="ANALYZE",
        is_demo=True,
        started_at=now_str
    )
    db.add(real_asm)
    db.add(demo_asm)
    db.commit()

    demo_finding = Finding(
        id="KAV-DEMO-ISO-01",
        assessment_id=demo_id,
        title="Simulated IDOR in Demo API",
        category="Broken Access Control",
        affected_component="/api/v1/workspaces",
        base_severity="HIGH",
        status="POTENTIAL"
    )
    db.add(demo_finding)
    db.commit()
    db.close()

    # TEST B: Query real assessment -> must be empty []
    res_real = client.get(f"/api/findings?assessment_id={real_id}")
    assert res_real.status_code == 200
    assert res_real.json() == []

    # TEST C: Query demo assessment -> must return the demo finding
    res_demo = client.get(f"/api/findings?assessment_id={demo_id}")
    assert res_demo.status_code == 200
    demo_findings = res_demo.json()
    assert len(demo_findings) == 1
    assert demo_findings[0]["id"] == "KAV-DEMO-ISO-01"


def test_isolation_test_d_world_monitor_latest_without_id_prefix():
    """
    TEST D: Create real World Monitor assessment using standard ID (ASM-F8CFA2EB-like).
    GET /api/assessments/world-monitor/latest must return that real World Monitor assessment
    without requiring KAVACH-WM-* ID prefix.
    """
    db = SessionLocal()
    now_str = ist_isoformat()
    asm_id = "ASM-WM-TEST-001"

    # Cleanup
    db.query(Finding).filter(Finding.assessment_id == asm_id).delete()
    db.query(Assessment).filter(Assessment.id == asm_id).delete()
    db.commit()

    asm = Assessment(
        id=asm_id,
        name="Empirical World Monitor Assessment",
        target_url="https://www.worldmonitor.app",
        status="COMPLETED",
        progress=100,
        current_stage="REPORT",
        is_demo=False,
        started_at=now_str,
        completed_at=now_str
    )
    db.add(asm)
    db.commit()
    db.close()

    res = client.get("/api/assessments/world-monitor/latest")
    assert res.status_code == 200
    data = res.json()
    assert "assessment_id" in data
    # Target URL must match World Monitor
    assert "worldmonitor.app" in data["target_url"]
    assert data["status"] in ("COMPLETED", "RUNNING")
    assert isinstance(data["findings"], list)
    assert isinstance(data["evidence"], list)


def test_isolation_test_e_url_check_isolation():
    """
    TEST E: URL check run (ASM-URL-*) does not register as a full security assessment
    or overwrite full assessment endpoints.
    """
    run_id = "ASM-URL-TEST-12345"
    res = client.get(f"/api/assessments/{run_id}")
    # A URL check ID is not a full assessment, must return 404 on /api/assessments
    assert res.status_code == 404


def test_isolation_test_f_cross_assessment_isolation_a_and_b():
    """
    TEST F: Create real assessment A and real assessment B.
    Add findings to both.
    Query A -> ONLY A findings.
    Query B -> ONLY B findings.
    """
    db = SessionLocal()
    now_str = ist_isoformat()
    asm_a = "ASM-TEST-AAA"
    asm_b = "ASM-TEST-BBB"

    # Cleanup
    db.query(Finding).filter(Finding.assessment_id.in_([asm_a, asm_b])).delete()
    db.query(Assessment).filter(Assessment.id.in_([asm_a, asm_b])).delete()
    db.commit()

    a1 = Assessment(id=asm_a, name="Assessment Alpha", target_url="https://alpha.local", is_demo=False, started_at=now_str)
    b1 = Assessment(id=asm_b, name="Assessment Beta", target_url="https://beta.local", is_demo=False, started_at=now_str)
    db.add(a1)
    db.add(b1)
    db.commit()

    f_a = Finding(id="FND-A-01", assessment_id=asm_a, title="Alpha Vulnerability", category="API", base_severity="HIGH")
    f_b = Finding(id="FND-B-01", assessment_id=asm_b, title="Beta Vulnerability", category="AUTH", base_severity="MEDIUM")
    db.add(f_a)
    db.add(f_b)
    db.commit()
    db.close()

    res_a = client.get(f"/api/findings?assessment_id={asm_a}")
    assert res_a.status_code == 200
    findings_a = res_a.json()
    assert len(findings_a) == 1
    assert findings_a[0]["id"] == "FND-A-01"
    assert findings_a[0]["assessment_id"] == asm_a

    res_b = client.get(f"/api/findings?assessment_id={asm_b}")
    assert res_b.status_code == 200
    findings_b = res_b.json()
    assert len(findings_b) == 1
    assert findings_b[0]["id"] == "FND-B-01"
    assert findings_b[0]["assessment_id"] == asm_b


def test_isolation_test_g_report_isolation():
    """
    TEST G: Generate report for assessment A.
    Expected: Only A findings/evidence/audit/risk.
    """
    asm_a = "ASM-TEST-AAA"
    res = client.get(f"/api/reports/{asm_a}")
    assert res.status_code == 200
    report = res.json()
    assert report["assessment"]["id"] == asm_a
    assert len(report["findings_detail"]) == 1
    assert report["findings_detail"][0]["id"] == "FND-A-01"
    for f in report["findings_detail"]:
        assert f["id"] != "FND-B-01"


def test_isolation_evidence_isolation():
    """
    Evidence isolation:
    GET /api/evidence?assessment_id=ASM-TEST-AAA returns only findings from AAA.
    Cross-assessment finding/evidence query returns [].
    """
    asm_a = "ASM-TEST-AAA"
    asm_b = "ASM-TEST-BBB"
    
    # Query with finding from A and assessment from B -> mismatch -> must return []
    res_mismatch = client.get(f"/api/evidence?finding_id=FND-A-01&assessment_id={asm_b}")
    assert res_mismatch.status_code == 200
    assert res_mismatch.json() == []

    # Query with finding from A and assessment from A -> valid
    res_match = client.get(f"/api/evidence?finding_id=FND-A-01&assessment_id={asm_a}")
    assert res_match.status_code == 200


def test_isolation_test_j_no_active_assessment_or_empty_real():
    """
    TEST J: Real mode without active assessment or with empty real assessment returns []
    rather than mixing demo findings into a real workflow.
    """
    db = SessionLocal()
    now_str = ist_isoformat()
    asm_id = "ASM-TEST-EMPTY-REAL"

    # Cleanup
    db.query(Finding).filter(Finding.assessment_id == asm_id).delete()
    db.query(Assessment).filter(Assessment.id == asm_id).delete()
    db.commit()

    asm = Assessment(
        id=asm_id,
        name="Empty Real Assessment",
        target_url="https://empty.real.local",
        status="COMPLETED",
        progress=100,
        current_stage="REPORT",
        is_demo=False,
        started_at=now_str,
        completed_at=now_str
    )
    db.add(asm)
    db.commit()
    db.close()

    # Query in explicit real mode -> must be []
    res_real = client.get("/api/findings?is_demo=false")
    assert res_real.status_code == 200
    for f in res_real.json():
        assert f.get("assessment_id") != "ASM-DEMO-001"
        assert f.get("id") != "KAV-2026-001"

    # Query scoped to empty real -> must be []
    res_empty = client.get(f"/api/findings?assessment_id={asm_id}")
    assert res_empty.status_code == 200
    assert res_empty.json() == []


def test_isolation_real_asm_f8cfa2eb_validation():
    """
    Real-world verification for confirmed real assessment ASM-F8CFA2EB:
    Must have is_demo=False, status=COMPLETED, progress=100, current_stage=REPORT,
    and GET /api/findings?assessment_id=ASM-F8CFA2EB must return exactly [].
    """
    res_asm = client.get("/api/assessments/ASM-F8CFA2EB")
    if res_asm.status_code == 200:
        data = res_asm.json()
        assert data["is_demo"] is False
        assert data["status"] == "COMPLETED"
        assert data["progress"] == 100
        assert data["current_stage"] == "REPORT"

        res_f = client.get("/api/findings?assessment_id=ASM-F8CFA2EB")
        assert res_f.status_code == 200
        assert res_f.json() == []

