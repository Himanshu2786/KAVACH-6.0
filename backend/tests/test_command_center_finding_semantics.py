"""
KAVACH 5.0 — Regression Tests: Command Center Finding Count Semantics

Proves:
1. Confirmation state (evidence has validated finding exists) vs
   Remediation state (STILL_OPEN = re-verification has not resolved finding) separation.
2. For KAVACH-WM-20260923-A018:
   - Total findings = 1 (WM-API-DOCS-A018)
   - Lifecycle status = STILL_OPEN
   - Technical evidence = VERIFIED / CONFIRMED
   - Assessment-scoped confirmed count = 1
3. Zero-finding assessments yield 0 confirmed / 0 total.
4. Re-test records are not counted as separate findings.
"""

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.models import Assessment, Finding, EvidenceRecord, ReVerificationRecord
from backend.app.api.routes.assessments import _enrich_assessment


def test_command_center_semantics_a018_confirmed_still_open():
    db = SessionLocal()
    try:
        asm = db.query(Assessment).filter(Assessment.id == "KAVACH-WM-20260923-A018").first()
        assert asm is not None, "KAVACH-WM-20260923-A018 must exist in database"

        # Check findings belonging strictly to this assessment
        findings = db.query(Finding).filter(Finding.assessment_id == asm.id).all()
        assert len(findings) == 1, "A018 must have exactly 1 finding"

        f = findings[0]
        assert f.id == "WM-API-DOCS-A018"
        # Lifecycle status is preserved as STILL_OPEN
        assert f.status == "STILL_OPEN", "Lifecycle status must be preserved as STILL_OPEN"
        # Technical evidence is verified
        assert f.evidence_status == "VERIFIED", "Evidence status must be VERIFIED"

        # Verify evidence records
        baseline_evidence = [
            e for e in f.evidence_records
            if e.validation_result == "CONFIRMED"
        ]
        assert len(baseline_evidence) >= 1, "Finding must have at least 1 confirmed baseline evidence record"

        # Verify enriched assessment counts
        enriched = _enrich_assessment(asm, db)
        assert enriched["total_findings"] == 1, "Enriched total_findings must be 1"
        assert enriched["confirmed_findings"] == 1, "Enriched confirmed_findings must be 1"

        # Ensure re-test records exist but are NOT counted as separate findings
        retest_count = db.query(ReVerificationRecord).filter(
            ReVerificationRecord.finding_id == f.id
        ).count()
        assert retest_count >= 1, "Re-verification records exist for finding"
        # Findings count remains 1, not 1 + retest_count
        assert len(findings) == 1

    finally:
        db.close()


def test_command_center_api_findings_payload():
    client = TestClient(app)
    resp = client.get("/api/findings?assessment_id=KAVACH-WM-20260923-A018")
    assert resp.status_code == 200
    data = resp.json()

    assert len(data) == 1, "API must return exactly 1 finding for A018"
    finding = data[0]
    assert finding["id"] == "WM-API-DOCS-A018"
    assert finding["status"] == "STILL_OPEN"
    assert finding["evidence_status"] == "VERIFIED"

    # Frontend aggregation verification simulation
    def is_confirmed(f):
        if f.get("evidence_status") == "REQUIRES_SOURCE_VALIDATION":
            return False
        if f.get("evidence_status") == "VERIFIED":
            return True
        if f.get("status") in ("CONFIRMED", "STILL_OPEN", "VERIFIED"):
            return True
        if any(e.get("validation_result") == "CONFIRMED" for e in f.get("evidence_records", [])):
            return True
        return False

    confirmed_count = sum(1 for f in data if is_confirmed(f))
    assert confirmed_count == 1, "Command Center calculation must yield 1 confirmed"
    assert f"{confirmed_count} confirmed / {len(data)} total" == "1 confirmed / 1 total"


def test_command_center_zero_finding_assessment():
    client = TestClient(app)
    # Non-existent or empty assessment ID returns 0 findings
    resp = client.get("/api/findings?assessment_id=EMPTY-ASSESSMENT-000")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0

    confirmed_count = sum(1 for f in data if f.get("status") in ("CONFIRMED", "STILL_OPEN"))
    assert confirmed_count == 0
    assert f"{confirmed_count} confirmed / {len(data)} total" == "0 confirmed / 0 total"
