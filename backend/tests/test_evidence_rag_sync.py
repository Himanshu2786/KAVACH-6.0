"""
Regression tests for KAVACH 5.0 — Technical Evidence & RAG-Grounded AI Output Synchronization (WM-API-DOCS-A018).

Validates:
1. /openapi.json is parsed and validated as OpenAPI before openapi_detected=true.
2. GET is the recorded probe method in empirical evidence and terminal verification.
3. The Evidence Validation AI panel cannot fall back to the old generic clickjacking/data-extraction text.
4. AI/RAG, Evidence Validation, Finding Dossier, and Report Export use the same canonical explanation.
"""

import json
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.models import Finding, EvidenceRecord
from backend.app.services.ai_analysis_service import ai_analysis_service
from backend.app.services.validation_service import validation_service, verify_openapi_document_delivery
from backend.app.services.report_service import ReportService
from backend.app.api.routes.findings import _serialize_finding

@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_openapi_parsed_before_openapi_detected_true():
    """
    Regression Test 1:
    /openapi.json must be parsed/validated as OpenAPI before openapi_detected=true.
    Invalid JSON, non-OpenAPI payloads, and HEAD responses must NOT set openapi_detected=true.
    """
    # 1. Non-OpenAPI JSON
    dummy_json = json.dumps({"status": "healthy", "service": "auth"}).encode("utf-8")
    eval_dummy = verify_openapi_document_delivery(
        status_code=200,
        content_type="application/json",
        body=dummy_json,
        http_method="GET"
    )
    assert eval_dummy["schema_detected"] is False, "Arbitrary JSON must NOT trigger schema_detected"
    assert eval_dummy.get("openapi_detected") is not True

    # 2. HTML 200 response (non-OpenAPI)
    html_body = b"<!DOCTYPE html><html><body><h1>Welcome</h1></body></html>"
    eval_html = verify_openapi_document_delivery(
        status_code=200,
        content_type="text/html",
        body=html_body,
        http_method="GET"
    )
    assert eval_html["schema_detected"] is False, "Generic HTML must NOT trigger schema_detected"

    # 3. Real OpenAPI 3.1.0 document
    openapi_body = json.dumps({
        "openapi": "3.1.0",
        "info": {
            "title": "WorldMonitor API",
            "version": "1.0.0"
        },
        "servers": [{"url": "https://api.worldmonitor.app"}]
    }).encode("utf-8")
    eval_valid = verify_openapi_document_delivery(
        status_code=200,
        content_type="application/json; charset=utf-8",
        body=openapi_body,
        http_method="GET"
    )
    assert eval_valid["delivered"] is True
    assert eval_valid["schema_detected"] is True
    assert eval_valid.get("openapi_detected") is True
    assert eval_valid["version"] == "3.1.0"
    assert eval_valid["title"] == "WorldMonitor API"

    # 4. Check model property on EvidenceRecord with mock non-OpenAPI raw_data
    fake_ev = EvidenceRecord(
        id="EV-TEST-NON-OPENAPI",
        raw_data=json.dumps({"endpoint": "/test", "http_method": "GET", "body": "hello"})
    )
    assert fake_ev.openapi_detected is False, "EvidenceRecord without verified openapi must have openapi_detected=False"

    # 5. Check real GET probe record in DB
    db = SessionLocal()
    try:
        ev = db.query(EvidenceRecord).filter(EvidenceRecord.id == "EV-WM-API-DOCS-A018-GET").first()
        assert ev is not None
        assert ev.openapi_detected is True
        assert ev.openapi_version == "3.1.0"
        assert ev.schema_title == "WorldMonitor API"
    finally:
        db.close()


def test_get_is_recorded_probe_method(db_session, client):
    """
    Regression Test 2:
    GET is the recorded probe method in empirical evidence and terminal verification.
    """
    # 1. DB EvidenceRecord property
    ev = db_session.query(EvidenceRecord).filter(EvidenceRecord.id == "EV-WM-API-DOCS-A018-GET").first()
    assert ev is not None
    assert ev.http_method == "GET"
    assert ev.http_status == 200
    assert ev.content_type == "application/json; charset=utf-8"
    assert ev.unauthenticated is True
    assert ev.authorization_state == "PUBLIC"

    # 2. API evidence endpoint
    res = client.get("/api/evidence?finding_id=WM-API-DOCS-A018")
    assert res.status_code == 200
    evds = res.json()
    get_ev = next(e for e in evds if e["id"] == "EV-WM-API-DOCS-A018-GET")
    assert get_ev["http_method"] == "GET"
    assert get_ev["http_status"] == 200
    assert "JSON/HTML" not in (get_ev.get("observed_output") or "")

    # 3. Terminal verification data
    term_data = validation_service.get_terminal_verification(db_session, "WM-API-DOCS-A018")
    assert "-Method Head" not in term_data["command"]
    assert "-Method HEAD" not in term_data["command"]
    assert "-Method Get" in term_data["command"] or "curl -k -s" in term_data["command"]


def test_ai_panel_cannot_fallback_to_generic_clickjacking_or_headers(db_session, client):
    """
    Regression Test 3:
    The Evidence Validation AI panel cannot fall back to the old generic clickjacking/data-extraction text.
    """
    # 1. Finding directly in DB
    finding = db_session.query(Finding).filter(Finding.id == "WM-API-DOCS-A018").first()
    assert finding is not None

    # AI Summary must describe the actual OpenAPI document detected
    assert "openapi" in finding.ai_summary.lower()
    assert "200" in finding.ai_summary

    # Potential Impact must NOT claim unproven attacks as demonstrated
    # It must state them in the NOT prove section
    impact_lower = finding.ai_potential_impact.lower()
    assert "not prove" in impact_lower
    unproven_part = impact_lower.split("not prove:")[1]
    assert "clickjacking" in unproven_part
    assert "data extraction" in unproven_part
    assert "account compromise" in unproven_part
    assert "privilege escalation" in unproven_part

    # It must not mention security headers in remediation
    for step in json.loads(finding.recommended_remediation):
        assert "content-security-policy" not in step.lower()
        assert "x-frame-options" not in step.lower()
        assert "strict-transport-security" not in step.lower()

    # 2. Finding returned by API
    res = client.get("/api/findings/WM-API-DOCS-A018")
    assert res.status_code == 200
    api_finding = res.json()
    assert "clickjacking" not in api_finding["ai_potential_impact"].split("NOT prove:")[0].lower()
    assert "reverse proxy header" not in " ".join(api_finding["recommended_remediation"]).lower()


def test_ai_rag_and_evidence_validation_use_same_canonical_explanation(db_session):
    """
    Regression Test 4:
    AI/RAG, Evidence Validation, Finding Dossier, and Report Export use the same canonical explanation.
    """
    canonical = ai_analysis_service.get_canonical_api_docs_explanation()
    finding = db_session.query(Finding).filter(Finding.id == "WM-API-DOCS-A018").first()
    evidence = db_session.query(EvidenceRecord).filter(EvidenceRecord.id == "EV-WM-API-DOCS-A018-GET").first()

    # 1. Offline rule fallback from AI Analysis Service
    offline_analysis = ai_analysis_service._generate_structured_rule_fallback(finding, evidence)
    assert offline_analysis["what_was_found"] == canonical["what_was_found"]
    assert offline_analysis["why_it_matters"] == canonical["why_it_matters"]
    assert offline_analysis["possible_impact"] == canonical["possible_impact"]
    assert offline_analysis["recommended_action"] == canonical["recommended_action"]
    assert offline_analysis["how_to_fix"] == canonical["how_to_fix"]
    assert offline_analysis["how_to_verify"] == canonical["how_to_verify"]

    # 2. Finding serialization (used by Finding Dossier & Evidence Validation page)
    serialized = _serialize_finding(finding)
    assert serialized["ai_potential_impact"] == canonical["possible_impact"]
    assert serialized["ai_summary"] == canonical["ai_summary"]
    assert serialized["recommended_remediation"] == canonical["recommended_remediation"]

    # 3. Report Export Service findings detail
    report_service = ReportService()
    report_data = report_service.generate_report_data(db_session, finding.assessment_id)
    rep_finding = next(f for f in report_data["findings_detail"] if f["id"] == "WM-API-DOCS-A018")
    assert rep_finding["ai_potential_impact"] == canonical["possible_impact"]
    assert rep_finding["ai_summary"] == canonical["ai_summary"]
    assert rep_finding["ai_hypothesis"] == canonical["ai_hypothesis"]


def test_existing_evidence_integrity_hash_preserved(db_session):
    """
    Regression Test:
    Historical baseline evidence record EV-WM-API-DOCS-A018 was NOT modified or deleted,
    and its SHA-256 hash was preserved.
    """
    baseline_ev = db_session.query(EvidenceRecord).filter(EvidenceRecord.id == "EV-WM-API-DOCS-A018").first()
    assert baseline_ev is not None, "Baseline record EV-WM-API-DOCS-A018 must remain in DB"
    assert baseline_ev.integrity_hash == "4958a3a45ce7375b3b32da36c78334b5365e52d24f95ba7c05464bdee29abe38", (
        "Baseline SHA-256 hash must NOT be modified or fabricated"
    )

    get_ev = db_session.query(EvidenceRecord).filter(EvidenceRecord.id == "EV-WM-API-DOCS-A018-GET").first()
    assert get_ev is not None, "GET record EV-WM-API-DOCS-A018-GET must exist in DB"
    assert get_ev.integrity_hash == "dc1b4710a6c560fa9d4f30d9b2b55f6e71ae6467b8f66890f04558a7bde93c13"
