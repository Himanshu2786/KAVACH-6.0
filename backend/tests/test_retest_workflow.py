import hashlib
import json
import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import Base, engine, SessionLocal, migrate_schema
from backend.app.models.models import Assessment, Finding, EvidenceRecord, ReVerificationRecord, AuditEvent
from backend.app.services.validation_service import validation_service
from backend.app.services.report_service import report_service

client = TestClient(app)

@pytest.fixture(autouse=True)
def init_db():
    Base.metadata.create_all(bind=engine)
    migrate_schema(engine)
    db = SessionLocal()
    yield db
    db.close()

def create_sample_assessment_and_finding(db, target_url="https://test.local", title="Missing Content-Security-Policy (CSP) Header"):
    asm_id = f"ASM-TEST-{uuid.uuid4().hex[:6]}"
    f_id = f"FND-TEST-{uuid.uuid4().hex[:6]}"
    ev_id = f"EVD-TEST-{uuid.uuid4().hex[:6]}"

    asm = Assessment(
        id=asm_id,
        name="Test Re-Verification Assessment",
        target_url=target_url,
        environment="staging",
        scope="authorized-test",
        status="COMPLETED",
        authorization_confirmed=True
    )
    db.add(asm)
    db.flush()

    finding = Finding(
        id=f_id,
        assessment_id=asm_id,
        title=title,
        category="INSECURE_CONFIGURATION",
        affected_component="HTTP Response Headers",
        base_severity="MEDIUM",
        status="CONFIRMED",
        evidence_status="CONFIRMED",
        cwe_id="CWE-1021",
        owasp_category="A05:2021-Security Misconfiguration"
    )
    db.add(finding)
    db.flush()

    raw_before = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nServer: nginx\r\n\r\n(No CSP header present in response)"
    expected_hash = hashlib.sha256(raw_before.encode("utf-8")).hexdigest()

    before_ev = EvidenceRecord(
        id=ev_id,
        finding_id=f_id,
        evidence_type="HTTP_RESPONSE_HEADERS",
        source=f"curl -I {target_url}",
        timestamp="2026-09-21T10:00:00+05:30",
        description="Missing Content-Security-Policy header in initial scan baseline.",
        raw_data=raw_before,
        integrity_hash=expected_hash,
        validation_result="CONFIRMED",
        evidence_nature="REAL EVIDENCE"
    )
    db.add(before_ev)
    db.commit()

    return asm_id, f_id, ev_id

def test_before_evidence_immutability(init_db):
    """Phase 4 & 11: Verify original baseline evidence is NEVER overwritten during re-test."""
    db = init_db
    asm_id, f_id, ev_id = create_sample_assessment_and_finding(db)

    original_ev = db.query(EvidenceRecord).filter(EvidenceRecord.id == ev_id).first()
    orig_hash = original_ev.integrity_hash
    orig_desc = original_ev.description
    orig_ts = original_ev.timestamp

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.http_version = "1.1"
    mock_resp.headers = {
        "content-security-policy": "default-src 'self'",
        "content-type": "text/html"
    }
    mock_resp.text = "Patched secure application"

    with patch("backend.app.services.validation_service.httpx.get", return_value=mock_resp):
        res = validation_service.re_verify_finding(db, f_id)

    # Baseline BEFORE evidence must remain untouched
    after_query_orig_ev = db.query(EvidenceRecord).filter(EvidenceRecord.id == ev_id).first()
    assert after_query_orig_ev.integrity_hash == orig_hash
    assert after_query_orig_ev.description == orig_desc
    assert after_query_orig_ev.timestamp == orig_ts

    # Verify a distinct AFTER evidence was created
    assert res.after_evidence_id != ev_id
    assert res.verification_verdict == "VERIFIED_REMEDIATED"
    assert res.new_status == "VERIFIED_REMEDIATED"

def test_real_sha256_evidence_hash_calculation(init_db):
    """Phase 4 & 11: Real SHA-256 hash must be accurately computed from raw observation."""
    db = init_db
    asm_id, f_id, ev_id = create_sample_assessment_and_finding(db)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.http_version = "1.1"
    mock_resp.headers = {
        "content-security-policy": "default-src 'self'; script-src 'self' https://trusted.cdn",
        "server": "KAVACH-SecureGate/1.0"
    }
    mock_resp.text = "Secured HTML Body"

    with patch("backend.app.services.validation_service.httpx.get", return_value=mock_resp):
        res = validation_service.re_verify_finding(db, f_id)

    after_ev = db.query(EvidenceRecord).filter(EvidenceRecord.id == res.after_evidence_id).first()
    assert after_ev is not None
    
    # Recalculate hash from stored raw_data
    computed_hash = hashlib.sha256(after_ev.raw_data.encode("utf-8")).hexdigest()
    assert after_ev.integrity_hash == computed_hash
    assert res.after_evidence_hash == computed_hash

def test_retest_unpatched_target_returns_still_open(init_db):
    """Phase 3, 5 & 10: If header remains missing, verdict must deterministically be STILL_OPEN."""
    db = init_db
    asm_id, f_id, ev_id = create_sample_assessment_and_finding(db)

    # Response still missing CSP
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.http_version = "1.1"
    mock_resp.headers = {
        "server": "nginx",
        "content-type": "text/html"
    }
    mock_resp.text = "Unpatched vulnerable page"

    with patch("backend.app.services.validation_service.httpx.get", return_value=mock_resp):
        res = validation_service.re_verify_finding(db, f_id)

    assert res.verification_verdict == "STILL_OPEN"
    assert res.new_status == "STILL_OPEN"
    
    # Check State Diff structure
    diff = json.loads(res.state_diff)
    assert diff["remediated_verdict"] == "STILL_OPEN"
    assert diff["security_improved"] is False

def test_retest_unreachable_target_returns_unable_to_verify(init_db):
    """Phase 3 & 10: Network failure or timeout must result in UNABLE_TO_VERIFY."""
    import httpx
    db = init_db
    asm_id, f_id, ev_id = create_sample_assessment_and_finding(db)

    with patch("backend.app.services.validation_service.httpx.get", side_effect=httpx.ConnectError("Connection refused")):
        res = validation_service.re_verify_finding(db, f_id)

    assert res.verification_verdict == "UNABLE_TO_VERIFY"
    assert res.new_status == "UNABLE_TO_VERIFY"
    assert "Unreachable" in res.output_after or "unreachable" in res.output_after.lower() or "connection failed" in res.output_after.lower()

def test_audit_trail_generation_sequence(init_db):
    """Phase 8: Audit events must follow RETEST_STARTED -> RETEST_OBSERVATION_CAPTURED -> RETEST_EVIDENCE_CREATED -> RETEST_STATE_COMPARISON -> RETEST_VERIFIED/UNRESOLVED."""
    db = init_db
    asm_id, f_id, ev_id = create_sample_assessment_and_finding(db)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.http_version = "1.1"
    mock_resp.headers = {"content-security-policy": "default-src 'self'"}
    mock_resp.text = "Fixed"

    with patch("backend.app.services.validation_service.httpx.get", return_value=mock_resp):
        res = validation_service.re_verify_finding(db, f_id)

    events = db.query(AuditEvent).filter(AuditEvent.finding_id == f_id).order_by(AuditEvent.timestamp.asc()).all()
    event_types = [e.event_type for e in events]

    assert "RETEST_STARTED" in event_types
    assert "RETEST_OBSERVATION_CAPTURED" in event_types
    assert "RETEST_EVIDENCE_CREATED" in event_types
    assert "RETEST_STATE_COMPARISON" in event_types
    assert "RETEST_VERIFIED" in event_types

    for e in events:
        assert e.finding_id == f_id
        assert e.assessment_id == asm_id

def test_report_includes_reverification_and_state_diff(init_db):
    """Phase 9: Final report contains before/after hashes, state diff, and audit events."""
    db = init_db
    asm_id, f_id, ev_id = create_sample_assessment_and_finding(db)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.http_version = "1.1"
    mock_resp.headers = {"content-security-policy": "default-src 'self'"}
    mock_resp.text = "Fixed"

    with patch("backend.app.services.validation_service.httpx.get", return_value=mock_resp):
        validation_service.re_verify_finding(db, f_id)

    report_data = report_service.generate_report_data(db, asm_id)
    assert report_data["executive_summary"]["total_retests_executed"] >= 1
    
    finding_entry = next(f for f in report_data["findings_detail"] if f["id"] == f_id)
    assert len(finding_entry["re_verifications"]) == 1
    rv = finding_entry["re_verifications"][0]
    assert rv["verification_verdict"] == "VERIFIED_REMEDIATED"
    assert rv["before_evidence_hash"] != ""
    assert rv["after_evidence_hash"] != ""
    assert "remediated_verdict" in rv["state_diff"]

    html = report_service.generate_html_report(db, asm_id)
    assert "BEFORE EVIDENCE" in html
    assert "AFTER EVIDENCE" in html
    assert "Deterministic Re-Test &amp; Verification Lifecycle" in html or "Deterministic Re-Test & Verification Lifecycle" in html
    assert "Cryptographic Audit Trail" in html

def test_wrong_finding_id_rejection(init_db):
    """Phase 10: Non-existent finding ID must cleanly raise ValueError."""
    db = init_db
    with pytest.raises(ValueError, match="Finding INVALID-ID not found"):
        validation_service.re_verify_finding(db, "INVALID-ID")

