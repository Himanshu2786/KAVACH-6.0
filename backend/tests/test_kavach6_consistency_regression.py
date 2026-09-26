"""
KAVACH 6.0 — QA Consistency & Regression Test Suite
Validates:
1. Canonical KAVACH 6.0 platform branding across API health, JSON report, HTML report, and forensic package
2. Re-test data model and validation terminology (validation_meaning, lifecycle_status, final_status, verdict, condition_improved, change_detected)
3. OpenAPI endpoint canonical path (/openapi.json) without clipping or truncation
4. Distinction between deterministic KAVACH priority score and CVSS
5. Cryptographic evidence hash integrity
6. Empirical World Monitor assessment selection logic
7. Command Center and navigation route coverage
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.services.report_service import report_service
from backend.app.services.forensic_export_service import forensic_export_service
from backend.app.api.routes.assessments import get_latest_world_monitor_assessment
from backend.app.models.models import Assessment, Finding, EvidenceRecord

client = TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_kavach6_api_version_metadata():
    """Verify API health endpoint returns canonical KAVACH 6.0 version."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["version"] == "6.0.0"
    assert "KAVACH" in data["platform"]


def test_kavach6_json_export_metadata(db: Session):
    """Verify JSON report metadata exports canonical KAVACH 6.0 platform branding."""
    rep = report_service.generate_report_data(db, "KAVACH-WM-20260923-A018")
    assert rep is not None
    assert "metadata" in rep
    assert "KAVACH v6.0" in rep["metadata"]["platform"]
    assert "KAVACH 5.0" not in rep["metadata"]["platform"]


def test_kavach6_printable_report_header():
    """Verify HTML printable report header displays KAVACH 6.0 brand title."""
    res = client.get("/api/reports/KAVACH-WM-20260923-A018/html")
    assert res.status_code == 200
    assert "KAVACH 6.0 // SECURITY ASSESSMENT INTELLIGENCE REPORT" in res.text
    assert "KAVACH 5.0 // SECURITY ASSESSMENT INTELLIGENCE REPORT" not in res.text


def test_kavach6_forensic_export_metadata():
    """Verify forensic reproducibility package exports canonical KAVACH 6.0 metadata."""
    pkg = forensic_export_service.generate_forensic_package("KAVACH-WM-20260923-A018")
    assert pkg is not None
    assert pkg.get("kavach_forensic_package_version") == "6.0"
    meta = pkg.get("metadata", {})
    assert "KAVACH 6.0" in meta.get("engine", "")
    assert meta.get("version") == "6.0.0-PROD"


def test_kavach6_forensic_html_branding():
    """Verify forensic HTML export document displays KAVACH 6.0 branding and footer."""
    pkg = forensic_export_service.generate_forensic_package("KAVACH-WM-20260923-A018")
    html_content = forensic_export_service.render_html_dossier(pkg)
    assert "KAVACH 6.0 — Forensic Assessment & Reproducibility Package" in html_content
    assert "Generated deterministically by KAVACH 6.0 Security Intelligence Engine" in html_content
    assert "KAVACH 5.0" not in html_content


def test_openapi_json_endpoint_integrity(db: Session):
    """Verify the canonical endpoint is /openapi.json and not truncated or mistyped as openapi.js."""
    finding = db.query(Finding).filter(Finding.id == "WM-API-DOCS-A018").first()
    assert finding is not None
    assert finding.affected_component == "https://www.worldmonitor.app/openapi.json"
    assert not finding.affected_component.endswith(".js")

    evds = db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == "WM-API-DOCS-A018").all()
    assert len(evds) > 0
    for ev in evds:
        if ev.where_found and "openapi" in ev.where_found:
            assert ev.where_found.endswith(".json")
            assert not ev.where_found.endswith(".js")
        if ev.verification_command and "openapi" in ev.verification_command:
            assert "openapi.json" in ev.verification_command
            assert "openapi.js" not in ev.verification_command.replace("openapi.json", "")


def test_retest_validation_meaning_and_lifecycle_consistency(db: Session):
    """
    Verify retest evidence objects explain 'UNCONFIRMED' with validation_meaning,
    lifecycle_status, and explicit lack of security improvement without falsely marking resolved.
    """
    rep = report_service.generate_report_data(db, "KAVACH-WM-20260923-A018")
    f_detail = rep["findings_detail"][0]
    assert f_detail["id"] == "WM-API-DOCS-A018"
    assert f_detail["status"] == "STILL_OPEN"

    retest_evds = f_detail["retest_evidence"]
    assert len(retest_evds) > 0
    for rev in retest_evds:
        assert rev["validation_result"] == "UNCONFIRMED"
        assert rev["validation_meaning"] == "REMEDIATION_UNCONFIRMED_FLAW_PERSISTS"
        assert rev["final_status"] == "STILL_OPEN"
        assert rev["verdict"] == "STILL_OPEN"
        assert rev["condition_improved"] is False
        assert rev["change_detected"] is False


def test_retest_records_semantics(db: Session):
    """Verify re_verifications comparison items maintain consistent STILL_OPEN semantics."""
    rep = report_service.generate_report_data(db, "KAVACH-WM-20260923-A018")
    f_detail = rep["findings_detail"][0]
    retests = f_detail["re_verifications"]
    assert len(retests) > 0
    for rv in retests:
        assert rv["retest_status"] == "STILL_OPEN"
        assert rv["final_status"] == "STILL_OPEN"
        assert rv["condition_improved"] is False
        assert rv["change_detected"] is False
        assert rv["verification_verdict"] == "STILL_OPEN"


def test_deterministic_priority_score_vs_cvss_distinction(db: Session):
    """
    Verify KAVACH deterministic priority score (5.92 / 10.0) is maintained
    and distinguished from external CVSS scoring models.
    """
    rep = report_service.generate_report_data(db, "KAVACH-WM-20260923-A018")
    f_detail = rep["findings_detail"][0]
    assert f_detail["priority_score"] == 5.92
    assert f_detail["priority_scale"] == "10.0"
    assert f_detail["priority_score_formatted"] == "5.92 / 10.0"
    assert f_detail["base_severity"] in ("MEDIUM", "MODERATE")


def test_evidence_integrity_and_hash_format(db: Session):
    """Verify all evidence records have valid 64-character hexadecimal SHA-256 hashes."""
    evds = db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == "WM-API-DOCS-A018").all()
    assert len(evds) > 0
    for ev in evds:
        assert ev.integrity_hash is not None
        assert len(ev.integrity_hash) == 64
        int(ev.integrity_hash, 16)


def test_assessment_context_selection_logic(db: Session):
    """Verify get_latest_world_monitor_assessment selects the authentic empirical assessment."""
    latest = get_latest_world_monitor_assessment(db)
    assert latest is not None
    assert latest["status"] != "NO_ASSESSMENT_RUN"
    assert "https://www.worldmonitor.app" in latest["target_url"]
    assert latest["assessment_id"].startswith("KAVACH-WM-")


def test_command_center_navigation_routes_coverage():
    """Verify critical Command Center KPI target routes resolve valid API endpoints."""
    routes = [
        "/api/assessments",
        "/api/findings",
        "/api/evidence",
        "/api/health",
        "/api/reports/KAVACH-WM-20260923-A018",
    ]
    for r in routes:
        resp = client.get(r)
        assert resp.status_code in (200, 307)
