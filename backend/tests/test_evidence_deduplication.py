"""
KAVACH 5.0 — Regression Tests: Evidence Deduplication & Lifecycle Distinction

Verifies:
1. Two technical evidence artifacts for one finding (WM-API-DOCS-A018) do NOT become two confirmed vulnerability proofs.
2. Canonical active evidence is EV-WM-API-DOCS-A018-GET.
3. Historical original live probe EV-WM-API-DOCS-A018 is preserved in the database (not deleted).
4. Executive metrics count unique active vulnerability proofs:
   - total_findings = 1
   - confirmed_findings = 1
   - confirmed_evidence = 1
   - evidence_proofs = 1
   - technical_evidence_captured = 2
5. Re-test records remain separate and do NOT increase executive evidence proof counts.
6. Detailed report section displays both evidence artifacts with their canonical vs historical distinctions.
"""

import pytest
from backend.app.core.database import SessionLocal
from backend.app.models.models import Finding, EvidenceRecord, Assessment
from backend.app.services.report_service import report_service
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

ASSESSMENT_ID = "KAVACH-WM-20260923-A018"
FINDING_ID = "WM-API-DOCS-A018"
CANONICAL_EVD_ID = "EV-WM-API-DOCS-A018-GET"
HISTORICAL_EVD_ID = "EV-WM-API-DOCS-A018"


def test_evidence_database_records_preserved():
    """Prove both baseline evidence records are preserved in the database."""
    db = SessionLocal()
    try:
        evds = db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == FINDING_ID).all()
        evd_ids = [e.id for e in evds]
        
        assert CANONICAL_EVD_ID in evd_ids, f"Canonical evidence {CANONICAL_EVD_ID} must exist in DB"
        assert HISTORICAL_EVD_ID in evd_ids, f"Historical evidence {HISTORICAL_EVD_ID} must not be deleted from DB"

        # Check properties on canonical
        canonical_rec = db.query(EvidenceRecord).filter(EvidenceRecord.id == CANONICAL_EVD_ID).first()
        assert canonical_rec.is_canonical is True
        assert canonical_rec.lifecycle_status == "CANONICAL"
        assert canonical_rec.validation_result == "CONFIRMED"

        # Check properties on historical
        historical_rec = db.query(EvidenceRecord).filter(EvidenceRecord.id == HISTORICAL_EVD_ID).first()
        assert historical_rec.is_canonical is False
        assert historical_rec.lifecycle_status == "HISTORICAL"
        assert historical_rec.validation_result == "CONFIRMED"

    finally:
        db.close()


def test_executive_metrics_unique_proof_deduplication():
    """Prove executive summary counts unique verified proof (=1) not raw row count (=2)."""
    db = SessionLocal()
    try:
        report_data = report_service.generate_report_data(db, ASSESSMENT_ID)
        exec_sum = report_data["executive_summary"]

        assert exec_sum["total_findings"] == 1
        assert exec_sum["confirmed_findings"] == 1
        assert exec_sum["confirmed_evidence"] == 1, (
            f"Evidence Confirmed must be 1 (unique confirmed proof), got {exec_sum['confirmed_evidence']}"
        )
        assert exec_sum["evidence_proofs"] == 1, (
            f"Evidence Proofs must be 1, got {exec_sum['evidence_proofs']}"
        )
        assert exec_sum["baseline_confirmed_evidence"] == 1
        assert exec_sum["technical_evidence_captured"] == 2, (
            f"Technical evidence captured must be 2, got {exec_sum['technical_evidence_captured']}"
        )
        assert exec_sum["canonical_active_evidence"] == CANONICAL_EVD_ID
        assert HISTORICAL_EVD_ID in exec_sum["historical_evidence"]

    finally:
        db.close()


def test_detailed_findings_evidence_distinction():
    """Prove detailed report section lists both records distinguishing canonical vs historical."""
    db = SessionLocal()
    try:
        report_data = report_service.generate_report_data(db, ASSESSMENT_ID)
        finding_detail = next(f for f in report_data["findings_detail"] if f["id"] == FINDING_ID)

        evidence_list = finding_detail["evidence"]
        assert len(evidence_list) == 2, f"Detailed section must show both 2 baseline records, got {len(evidence_list)}"

        ev_map = {e["id"]: e for e in evidence_list}
        assert CANONICAL_EVD_ID in ev_map
        assert HISTORICAL_EVD_ID in ev_map

        assert ev_map[CANONICAL_EVD_ID]["is_canonical"] is True
        assert ev_map[CANONICAL_EVD_ID]["lifecycle_status"] == "CANONICAL"
        assert "GET" in ev_map[CANONICAL_EVD_ID]["relationship_note"]

        assert ev_map[HISTORICAL_EVD_ID]["is_canonical"] is False
        assert ev_map[HISTORICAL_EVD_ID]["lifecycle_status"] == "HISTORICAL"
        assert "audit" in ev_map[HISTORICAL_EVD_ID]["relationship_note"].lower()

    finally:
        db.close()


def test_html_report_deduplication_and_badges():
    """Prove HTML report reflects Evidence Confirmed = 1 and renders distinct badges."""
    db = SessionLocal()
    try:
        html = report_service.generate_html_report(db, ASSESSMENT_ID)

        # Unique Proof KPI
        assert "Evidence Confirmed (Proof: 1)" in html
        assert "Technical Evidence Captured" in html

        # Both records present with badges
        assert CANONICAL_EVD_ID in html
        assert "CANONICAL ACTIVE PROOF" in html
        assert HISTORICAL_EVD_ID in html
        assert "HISTORICAL ARTIFACT (SUPERSEDED)" in html

    finally:
        db.close()


def test_api_report_export_json_endpoint():
    """Prove the REST API export returns deduplicated unique proof count."""
    res = client.get(f"/api/reports/{ASSESSMENT_ID}")
    assert res.status_code == 200
    data = res.json()
    exec_sum = data["executive_summary"]

    assert exec_sum["total_findings"] == 1
    assert exec_sum["confirmed_evidence"] == 1
    assert exec_sum["evidence_proofs"] == 1
    assert exec_sum["technical_evidence_captured"] == 2
    assert exec_sum["canonical_active_evidence"] == CANONICAL_EVD_ID
