"""
KAVACH 5.0 — Assessment History Finding Count Consistency Regression Tests

Regression tests verifying that:
1. Assessment Audit History aggregation accurately counts confirmed findings.
2. A confirmed finding with a STILL_OPEN re-test still counts as one confirmed finding in History.
3. KAVACH-WM-20260923-A018 returns total_findings = 1, confirmed_findings = 1 across all endpoints:
   - GET /api/assessments
   - GET /api/assessments/{id}
   - GET /api/assessments/world-monitor/latest
   - GET /api/reports/{id}
   - GET /api/assessments/{id}/posture
4. Older assessments remain isolated and unaffected.
5. Re-test status STILL_OPEN does NOT reduce the confirmed count to zero.
6. The source of truth is consistent across History, Findings, Report Export, and Risk Scoring.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.models import Assessment, Finding, EvidenceRecord, ReVerificationRecord
from backend.app.core.time import ist_isoformat
from backend.app.services.report_service import report_service
from backend.app.services.assessment_service import assessment_service

client = TestClient(app)


def test_kavach_wm_20260923_a018_history_consistency():
    """
    Verifies that KAVACH-WM-20260923-A018:
    - Assessment status = COMPLETED
    - Total findings = 1
    - Confirmed findings = 1
    - Displays '1 confirmed / 1 total' in the History list.
    """
    # 1. Test GET /api/assessments (used directly by AssessmentHistoryPage)
    res = client.get("/api/assessments")
    assert res.status_code == 200
    assessments = res.json()
    target = next((a for a in assessments if a["id"] == "KAVACH-WM-20260923-A018"), None)
    assert target is not None, "Assessment KAVACH-WM-20260923-A018 must exist in /api/assessments"
    assert target["status"] == "COMPLETED"
    assert target["total_findings"] == 1
    assert target["confirmed_findings"] == 1, (
        f"Expected 1 confirmed finding in History for KAVACH-WM-20260923-A018, got {target['confirmed_findings']}"
    )

    # 2. Test GET /api/assessments/KAVACH-WM-20260923-A018
    res_single = client.get("/api/assessments/KAVACH-WM-20260923-A018")
    assert res_single.status_code == 200
    data_single = res_single.json()
    assert data_single["status"] == "COMPLETED"
    assert data_single["total_findings"] == 1
    assert data_single["confirmed_findings"] == 1

    # 3. Test GET /api/assessments/world-monitor/latest
    res_latest = client.get("/api/assessments/world-monitor/latest")
    assert res_latest.status_code == 200
    data_latest = res_latest.json()
    if data_latest.get("id") == "KAVACH-WM-20260923-A018":
        assert data_latest["total_findings"] == 1
        assert data_latest["confirmed_findings"] == 1


def test_parity_with_report_and_posture_modules():
    """
    Ensures History source of truth matches Report Export and Risk Scoring for KAVACH-WM-20260923-A018.
    """
    db = SessionLocal()
    try:
        # Report Service
        rep_data = report_service.generate_report_data(db, "KAVACH-WM-20260923-A018")
        exec_sum = rep_data["executive_summary"]
        assert exec_sum["total_findings"] == 1
        assert exec_sum["confirmed_findings"] == 1

        # Posture Service
        posture = assessment_service.calculate_security_posture(db, "KAVACH-WM-20260923-A018")
        assert posture["total_findings"] == 1
        assert posture["confirmed_count"] == 1

        # Assessment Enriched
        res = client.get("/api/assessments/KAVACH-WM-20260923-A018")
        assert res.status_code == 200
        asm_data = res.json()
        assert asm_data["total_findings"] == exec_sum["total_findings"]
        assert asm_data["confirmed_findings"] == exec_sum["confirmed_findings"]
    finally:
        db.close()


def test_confirmed_finding_with_still_open_retest_counts_in_history():
    """
    Regression Test:
    Creates a temporary test assessment with:
    - 1 Finding initially marked CONFIRMED.
    - Baseline Evidence marked CONFIRMED.
    - Re-test executed resulting in STILL_OPEN (finding.status = 'STILL_OPEN').
    - Asserts that History displays 1 confirmed / 1 total.
    """
    db = SessionLocal()
    now_str = ist_isoformat()
    test_asm_id = f"ASM-REG-RETEST-{uuid.uuid4().hex[:6].upper()}"
    test_finding_id = f"FND-{uuid.uuid4().hex[:6].upper()}"
    test_ev_id = f"EVD-{uuid.uuid4().hex[:6].upper()}"
    test_retest_id = f"REV-{uuid.uuid4().hex[:6].upper()}"

    try:
        asm = Assessment(
            id=test_asm_id,
            name="Regression Test Assessment (STILL_OPEN Re-test)",
            target_url="https://test.example.com",
            description="Testing STILL_OPEN finding count in history",
            environment="Testing",
            scope="App",
            authorization_confirmed=True,
            modules_enabled='["API Security"]',
            status="COMPLETED",
            progress=100,
            current_stage="REPORT",
            is_demo=False,
            started_at=now_str,
            completed_at=now_str
        )
        db.add(asm)

        finding = Finding(
            id=test_finding_id,
            assessment_id=test_asm_id,
            title="Public API Schema Exposure",
            category="API Security",
            description="OpenAPI specification publicly available",
            affected_component="/openapi.json",
            base_severity="MEDIUM",
            priority="MEDIUM",
            priority_score=5.5,
            status="STILL_OPEN",  # Lifecycle state after re-test determined issue remains open
            evidence_status="VERIFIED",
            ai_analysis_status="COMPLETED",
            cwe_id="CWE-200",
            owasp_category="API3:2023",
            created_at=now_str,
            updated_at=now_str
        )
        db.add(finding)

        evd = EvidenceRecord(
            id=test_ev_id,
            finding_id=test_finding_id,
            evidence_type="API Documentation Probe",
            source="Local Probe",
            timestamp=now_str,
            description="HTTP GET /openapi.json returned 200 OK",
            validation_result="CONFIRMED",
            integrity_hash="abcdef1234567890abcdef1234567890",
            evidence_nature="REAL EVIDENCE",
            what_found="OpenAPI Schema exposed",
            where_found="/openapi.json",
            confidence_level="HIGH"
        )
        db.add(evd)

        retest = ReVerificationRecord(
            id=test_retest_id,
            finding_id=test_finding_id,
            timestamp=now_str,
            previous_status="CONFIRMED",
            new_status="STILL_OPEN",
            verification_verdict="STILL_OPEN",
            command_executed="curl -k -s https://test.example.com/openapi.json",
            output_before="200 OK OpenAPI schema",
            output_after="200 OK OpenAPI schema",
            summary="Vulnerability persists on target live endpoint.",
            target_url="https://test.example.com/openapi.json"
        )
        db.add(retest)
        db.commit()

        # Query endpoint
        res = client.get(f"/api/assessments/{test_asm_id}")
        assert res.status_code == 200
        data = res.json()

        assert data["total_findings"] == 1
        assert data["confirmed_findings"] == 1, (
            f"Expected 1 confirmed finding for STILL_OPEN status, got {data['confirmed_findings']}"
        )

        # Also verify in list endpoint
        res_list = client.get("/api/assessments")
        assert res_list.status_code == 200
        item = next((a for a in res_list.json() if a["id"] == test_asm_id), None)
        assert item is not None
        assert item["total_findings"] == 1
        assert item["confirmed_findings"] == 1

    finally:
        # Cleanup test records
        db.query(ReVerificationRecord).filter(ReVerificationRecord.id == test_retest_id).delete()
        db.query(EvidenceRecord).filter(EvidenceRecord.id == test_ev_id).delete()
        db.query(Finding).filter(Finding.id == test_finding_id).delete()
        db.query(Assessment).filter(Assessment.id == test_asm_id).delete()
        db.commit()
        db.close()


def test_remediated_finding_does_not_count_as_confirmed():
    """
    Verifies that a remediated finding (VERIFIED_REMEDIATED or RESOLVED) does NOT count as an active confirmed finding.
    """
    db = SessionLocal()
    now_str = ist_isoformat()
    test_asm_id = f"ASM-REG-REM-{uuid.uuid4().hex[:6].upper()}"
    test_finding_id = f"FND-REM-{uuid.uuid4().hex[:6].upper()}"

    try:
        asm = Assessment(
            id=test_asm_id,
            name="Remediated Finding Assessment",
            target_url="https://test-rem.example.com",
            status="COMPLETED",
            progress=100,
            current_stage="REPORT",
            is_demo=False,
            started_at=now_str,
            completed_at=now_str
        )
        db.add(asm)

        finding = Finding(
            id=test_finding_id,
            assessment_id=test_asm_id,
            title="Old Remediated Issue",
            category="Security Headers",
            base_severity="LOW",
            status="VERIFIED_REMEDIATED",  # Successfully resolved
            evidence_status="VERIFIED",
            created_at=now_str,
            updated_at=now_str
        )
        db.add(finding)
        db.commit()

        res = client.get(f"/api/assessments/{test_asm_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["total_findings"] == 1
        assert data["confirmed_findings"] == 0, (
            f"Remediated finding must not count as confirmed; got {data['confirmed_findings']}"
        )
    finally:
        db.query(Finding).filter(Finding.id == test_finding_id).delete()
        db.query(Assessment).filter(Assessment.id == test_asm_id).delete()
        db.commit()
        db.close()


def test_older_assessments_remain_isolated_and_unaffected():
    """
    Verifies that clean assessments (zero findings) and empty assessments remain at 0 confirmed / 0 total.
    """
    res = client.get("/api/assessments")
    assert res.status_code == 200
    assessments = res.json()

    # Find known clean assessments
    for asm in assessments:
        if asm["id"] in ("ASM-TEST-REAL-A", "ASM-TEST-REAL-B", "ASM-2B96CD00"):
            assert asm["total_findings"] == 0
            assert asm["confirmed_findings"] == 0
