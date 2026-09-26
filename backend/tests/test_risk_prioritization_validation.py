"""
Regression test for Risk Prioritization Response Validation.
Verifies that:
1. Findings with null base_severity or evidence_status are resolved from persisted data.
2. GET /api/risk/prioritization/{assessment_id} returns HTTP 200 (no 500 ResponseValidationError).
3. The response satisfies the Pydantic schema with non-null strings for base_severity and evidence_strength.
4. Real World Monitor assessment KAVACH-WM-20260922-2FC1 returns schema-valid risk items.
5. Findings remain strictly assessment-scoped.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.main import app
from backend.app.core.database import get_db, SessionLocal
from backend.app.models.models import Assessment, Finding, EvidenceRecord
from backend.app.services.risk_service import risk_service
from backend.app.schemas.schemas import RiskPrioritizationItem

client = TestClient(app)


def test_reproduce_and_verify_null_field_resolution():
    """
    Simulates a finding that previously had base_severity = None and evidence_status = None.
    Verifies that the risk calculation resolves genuine values from persisted evidence and returns HTTP 200.
    """
    db: Session = SessionLocal()
    asm_id = "TEST-ASM-RISK-REGRESSION-01"
    fnd_id = "TEST-FND-RISK-01"
    ev_id = "TEST-EV-RISK-01"

    try:
        # Clean up any leftover test data
        db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == fnd_id).delete()
        db.query(Finding).filter(Finding.id == fnd_id).delete()
        db.query(Assessment).filter(Assessment.id == asm_id).delete()
        db.commit()

        # 1. Create Assessment
        asm = Assessment(
            id=asm_id,
            name="Risk Regression Test Assessment",
            target_url="https://test.example.com",
            environment="Testing Environment",
            status="COMPLETED",
            progress=100
        )
        db.add(asm)

        # 2. Create Finding with base_severity=None and evidence_status=None to reproduce the bug
        f = Finding(
            id=fnd_id,
            assessment_id=asm_id,
            title="Regression Test Unvalidated Finding",
            category="API security",
            affected_component="https://test.example.com/api",
            base_severity=None,
            severity="MEDIUM",
            status="CONFIRMED",
            evidence_status=None,
            priority_score=5.0
        )
        db.add(f)

        # 3. Attach empirical confirmed evidence
        ev = EvidenceRecord(
            id=ev_id,
            finding_id=fnd_id,
            evidence_type="API Security Probe",
            validation_result="CONFIRMED",
            confidence_level="HIGH",
            evidence_nature="REAL EVIDENCE",
            what_found="API schema exposure verified"
        )
        db.add(ev)
        db.commit()

        # 4. Invoke API endpoint GET /api/risk/prioritization/{assessment_id}
        response = client.get(f"/api/risk/prioritization/{asm_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()
        assert len(data) == 1
        item = data[0]

        # 5. Verify every required field in RiskPrioritizationItem
        assert item["finding_id"] == fnd_id
        assert item["title"] == "Regression Test Unvalidated Finding"
        assert item["category"] == "API security"
        assert item["affected_component"] == "https://test.example.com/api"
        assert item["base_severity"] == "MEDIUM", f"Expected 'MEDIUM', got {item['base_severity']}"
        assert item["status"] == "CONFIRMED"
        assert item["evidence_strength"] == "VERIFIED", f"Expected 'VERIFIED', got {item['evidence_strength']}"
        assert isinstance(item["priority_score"], (int, float))
        assert item["calculated_priority"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
        assert "component_criticality" in item
        assert "data_sensitivity" in item
        assert "exposure" in item
        assert "explanation" in item

        # 6. Verify explanation structure has non-null levels
        exp = item["explanation"]
        assert exp["base_severity"]["level"] == "MEDIUM"
        assert exp["evidence_strength"]["level"] == "VERIFIED"
        assert "None" not in exp["summary_statement"]

        # 7. Validate through Pydantic model directly to guarantee zero schema mismatch
        validated = RiskPrioritizationItem(**item)
        assert validated.base_severity == "MEDIUM"
        assert validated.evidence_strength == "VERIFIED"

    finally:
        db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == fnd_id).delete()
        db.query(Finding).filter(Finding.id == fnd_id).delete()
        db.query(Assessment).filter(Assessment.id == asm_id).delete()
        db.commit()
        db.close()


def test_real_world_monitor_assessment_risk_endpoint():
    """
    Verifies that the live assessment KAVACH-WM-20260922-2FC1 returns HTTP 200
    and a schema-valid response for WM-API-DOCS-2FC1.
    """
    response = client.get("/api/risk/prioritization/KAVACH-WM-20260922-2FC1")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert len(data) >= 1

    target_item = next((x for x in data if x["finding_id"] == "WM-API-DOCS-2FC1"), None)
    assert target_item is not None, "WM-API-DOCS-2FC1 not found in prioritization output"

    assert target_item["base_severity"] == "MEDIUM"
    assert target_item["calculated_priority"] == "MEDIUM"
    assert target_item["priority_score"] == 5.92
    assert target_item["status"] == "CONFIRMED"
    assert target_item["evidence_strength"] == "VERIFIED"
    assert target_item["affected_component"] == "https://www.worldmonitor.app/openapi.json"
    assert target_item["category"] == "API security"

    # Verify Pydantic validation passes cleanly
    validated = RiskPrioritizationItem(**target_item)
    assert validated.base_severity == "MEDIUM"
    assert validated.evidence_strength == "VERIFIED"


def test_risk_prioritization_assessment_isolation():
    """
    Ensures that risk prioritization for KAVACH-WM-20260922-2FC1 does not contaminate
    or include findings from other assessments (such as ASM-DEMO-001).
    """
    resp_wm = client.get("/api/risk/prioritization/KAVACH-WM-20260922-2FC1")
    assert resp_wm.status_code == 200
    wm_findings = [x["finding_id"] for x in resp_wm.json()]

    resp_demo = client.get("/api/risk/prioritization/ASM-DEMO-001")
    assert resp_demo.status_code == 200
    demo_findings = [x["finding_id"] for x in resp_demo.json()]

    # WM must contain its finding, must not contain demo finding
    assert "WM-API-DOCS-2FC1" in wm_findings
    assert "KAV-2026-004" not in wm_findings

    # Demo must contain its finding, must not contain WM finding
    assert "KAV-2026-004" in demo_findings
    assert "WM-API-DOCS-2FC1" not in demo_findings


def test_evidence_strength_and_finding_status_semantic_consistency():
    """
    Regression test proving:
    1. evidence_strength != finding status as concepts (e.g. status='STILL_OPEN' while evidence_strength='VERIFIED').
    2. exported risk explanation cannot contain contradictory values (outer evidence_strength matches explanation.level).
    3. rationale describes evidence strength, not merely repeating finding status.
    4. priority_score for WM-API-DOCS-CB52 is derived deterministically from the scoring model as 5.92.
    5. Underlying facts remain intact: status is STILL_OPEN, baseline evidence is CONFIRMED.
    """
    # 1. Fetch risk prioritization for real World Monitor assessment CB52
    response = client.get("/api/risk/prioritization/KAVACH-WM-20260922-CB52")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert len(data) >= 1
    target = next((x for x in data if x["finding_id"] == "WM-API-DOCS-CB52"), None)
    assert target is not None, "WM-API-DOCS-CB52 must exist in prioritization output"

    # 2. Assert distinct concepts: status is STILL_OPEN, but evidence_strength is VERIFIED
    assert target["status"] == "STILL_OPEN", f"Expected status 'STILL_OPEN', got {target['status']}"
    assert target["evidence_strength"] == "VERIFIED", f"Expected evidence_strength 'VERIFIED', got {target['evidence_strength']}"
    assert target["evidence_strength"] != target["status"], "evidence_strength and finding status must be separate concepts!"

    # 3. Assert explanation internal consistency
    exp = target["explanation"]
    ev_exp = exp["evidence_strength"]
    assert ev_exp["level"] == target["evidence_strength"], (
        f"Internal inconsistency: outer evidence_strength '{target['evidence_strength']}' "
        f"does not match explanation.evidence_strength.level '{ev_exp['level']}'"
    )
    assert ev_exp["level"] == "VERIFIED"
    assert ev_exp["level"] != target["status"], "explanation.evidence_strength.level must NOT be finding status!"
    assert ev_exp["score"] == 10.0, f"Expected score 10.0 for VERIFIED, got {ev_exp['score']}"
    assert "STILL_OPEN" not in ev_exp["rationale"], "Rationale must describe evidence strength, not repeat finding status!"
    assert "VERIFIED" in ev_exp["rationale"], "Rationale must mention evidence strength level!"

    # 4. Assert calculated priority_score derived from scoring formula
    # Composite = (5.0*0.30) + (7.5*0.25) + (4.0*0.20) + (10.0*0.15) + (9.0*0.10) = 6.575
    # Testing Environment multiplier = 0.90 -> round(6.575 * 0.90, 2) = 5.92
    assert target["priority_score"] == 5.92, f"Expected priority_score 5.92, got {target['priority_score']}"
    assert target["calculated_priority"] == "MEDIUM"

    # 5. Assert Pydantic validation passes cleanly
    validated = RiskPrioritizationItem(**target)
    assert validated.status == "STILL_OPEN"
    assert validated.evidence_strength == "VERIFIED"
    assert validated.priority_score == 5.92

    # 6. Verify Findings API consistency
    finding_resp = client.get("/api/findings/WM-API-DOCS-CB52")
    assert finding_resp.status_code == 200
    f_data = finding_resp.json()
    assert f_data["status"] == "STILL_OPEN"
    assert f_data["evidence_status"] == "VERIFIED"
    assert f_data["priority_score"] == 5.92

    # 7. Verify Reports API / Exported JSON consistency
    report_resp = client.get("/api/reports/KAVACH-WM-20260922-CB52")
    assert report_resp.status_code == 200
    rep_data = report_resp.json()
    rep_prioritized = rep_data["prioritized_findings"][0]
    assert rep_prioritized["priority_score"] == 5.92
    assert rep_prioritized["evidence_strength"] == "VERIFIED"
    assert rep_prioritized["status"] == "STILL_OPEN"
    rep_finding = rep_data["findings_detail"][0]
    assert rep_finding["priority_score"] == 5.92
    assert rep_finding["status"] == "STILL_OPEN"
    assert rep_finding["evidence_status"] == "VERIFIED"

    # 8. Verify baseline evidence is preserved as CONFIRMED
    assert any(e["id"] == "EV-WM-API-DOCS-CB52" and e["validation_result"] == "CONFIRMED" for e in rep_finding["evidence"])


def test_audit_event_assessment_level_finding_id_mapping():
    """
    Verifies that logging assessment-level events like ASSESSMENT_STARTED
    does not incorrectly populate finding_id with the assessment_id.
    """
    from services.storage_service import StorageService
    storage = StorageService()

    asm_id = "TEST-ASM-AUDIT-REGRESSION-01"
    evt_id = storage.log_audit_event(
        event_type="ASSESSMENT_STARTED",
        action="assessment started",
        actor="KAVACH Engine",
        assessment_id=asm_id,
        object_name=asm_id,
        finding_id=None,
        result="RUNNING",
        details={"name": "Audit Mapping Test"}
    )

    try:
        with storage._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, event_type, assessment_id, finding_id, object FROM audit_events WHERE id = ?", (evt_id,))
            row = cursor.fetchone()
            assert row is not None, "Audit event must be logged"
            assert row["event_type"] == "ASSESSMENT_STARTED"
            assert row["assessment_id"] == asm_id
            assert row["finding_id"] is None, (
                f"Expected finding_id to be None for assessment-level event, got: {row['finding_id']}"
            )
    finally:
        with storage._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM audit_events WHERE id = ?", (evt_id,))
            conn.commit()

