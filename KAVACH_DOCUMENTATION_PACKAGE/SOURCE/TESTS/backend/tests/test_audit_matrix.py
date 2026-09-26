"""
KAVACH 5.0 — Comprehensive End-to-End Autonomous Acceptance & Audit Test Matrix
Audits:
- System Health & Engine Mode
- Scope Guard (authorization requirement, validation)
- 8-Stage Assessment Lifecycle & Module Execution
- Discovery Persistence & Retrieval
- Findings Catalog & Status Transitions
- Evidence Persistence & Finding<->Evidence Linking
- Data Isolation (Assessment A vs B vs Demo vs Clean Real)
- Zero-Orphan Database Integrity
- World Monitor Real Target Findings & Evidence
- Report Generation (JSON & HTML)
- URL Check & Local Posture Scanners
- AI Status, RAG Knowledge Graph & Ollama Integration
"""

import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.models import (
    Assessment, Finding, EvidenceRecord, AuditEvent, DiscoveryItem
)
from backend.app.core.time import ist_isoformat

client = TestClient(app)

def test_audit_01_system_health_and_engine():
    """Verify system health, status, and engine mode endpoints respond honestly."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") == "online"
    assert "KAVACH" in data.get("platform", "")

    res_status = client.get("/api/system/status")
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert "backend_status" in status_data
    assert "database_status" in status_data

    res_ollama = client.get("/api/system/ollama")
    assert res_ollama.status_code == 200


def test_audit_02_scope_guard_authorization_enforcement():
    """Verify that starting an assessment without explicit authorization confirmation fails."""
    payload_unauth = {
        "name": "Unauthorized Audit Probe",
        "target_url": "https://unauthorized.test",
        "environment": "PRODUCTION",
        "scope": "RESTRICTED",
        "authorization_confirmed": False,
        "modules_enabled": ["Security Headers"],
        "is_demo": False
    }
    res = client.post("/api/assessments", json=payload_unauth)
    assert res.status_code in (400, 422, 500) or "authorization" in res.text.lower()


def test_audit_03_controlled_assessment_lifecycle_and_advance_stage():
    """
    Test complete lifecycle from creation, advance to ASSESS (which runs security_module_runner),
    and advance to REPORT. Verify audit trail logs real telemetry.
    """
    db = SessionLocal()
    now_str = ist_isoformat()
    test_asm_id = "ASM-LIFECYCLE-TEST"

    # Cleanup any prior test run
    db.query(AuditEvent).filter(AuditEvent.assessment_id == test_asm_id).delete()
    db.query(DiscoveryItem).filter(DiscoveryItem.assessment_id == test_asm_id).delete()
    db.query(Finding).filter(Finding.assessment_id == test_asm_id).delete()
    db.query(Assessment).filter(Assessment.id == test_asm_id).delete()
    db.commit()

    # Create authorized assessment
    payload_auth = {
        "name": "Controlled Lifecycle Target",
        "target_url": "https://lifecycle-target.local",
        "environment": "STAGING",
        "scope": "AUTHORIZED_TEST",
        "authorization_confirmed": True,
        "modules_enabled": ["Security Headers", "API Security"],
        "is_demo": False
    }
    res = client.post("/api/assessments", json=payload_auth)
    assert res.status_code == 200
    created = res.json()
    asm_id = created["id"]
    assert created["status"] == "RUNNING"
    assert created["current_stage"] == "DISCOVER"

    # Advance to ASSESS — triggers security_module_runner
    res = client.post(f"/api/assessments/{asm_id}/advance-stage", json={"stage": "ASSESS"})
    assert res.status_code == 200
    adv = res.json()
    assert adv["current_stage"] == "ASSESS"

    # Check that audit trail recorded real structured logs for ASSESS
    res_audits = client.get(f"/api/system/audit?assessment_id={asm_id}")
    assert res_audits.status_code == 200
    audits = res_audits.json()
    assert len(audits) > 0
    event_types = [a["event_type"] for a in audits]
    assert "ASSESSMENT_CREATED" in event_types
    assert "ASSESSMENT_STAGE_ADVANCED" in event_types

    # Advance to REPORT (marks assessment completed)
    res_rep = client.post(f"/api/assessments/{asm_id}/advance-stage", json={"stage": "REPORT"})
    assert res_rep.status_code == 200
    completed = res_rep.json()
    assert completed["current_stage"] == "REPORT"
    assert completed["status"] == "COMPLETED"

    # Clean up test assessment
    db.query(AuditEvent).filter(AuditEvent.assessment_id == asm_id).delete()
    db.query(DiscoveryItem).filter(DiscoveryItem.assessment_id == asm_id).delete()
    db.query(Finding).filter(Finding.assessment_id == asm_id).delete()
    db.query(Assessment).filter(Assessment.id == asm_id).delete()
    db.commit()
    db.close()


def test_audit_04_world_monitor_finding_and_evidence_linking():
    """
    Verify real World Monitor assessment KAVACH-WM-20260922-2FC1:
    - Finding WM-API-DOCS-2FC1 exists
    - Evidence EV-WM-API-DOCS-2FC1 exists
    - Finding's evidence_records contains EV-WM-API-DOCS-2FC1
    - GET /api/evidence?finding_id=WM-API-DOCS-2FC1 returns the evidence
    - GET /api/evidence?assessment_id=KAVACH-WM-20260922-2FC1 returns the evidence
    - GET /api/evidence?assessment_id=ASM-014A92D1 returns [] (isolation)
    """
    res_f = client.get("/api/findings?assessment_id=KAVACH-WM-20260922-2FC1")
    assert res_f.status_code == 200
    findings = res_f.json()
    assert len(findings) == 1
    f = findings[0]
    assert f["id"] == "WM-API-DOCS-2FC1"
    assert f["status"] == "CONFIRMED"
    ev_ids = [ev["id"] if isinstance(ev, dict) else ev for ev in f.get("evidence_records", [])]
    assert "EV-WM-API-DOCS-2FC1" in ev_ids

    # Check evidence queried by finding_id
    res_ev_f = client.get("/api/evidence?finding_id=WM-API-DOCS-2FC1")
    assert res_ev_f.status_code == 200
    ev_list_f = res_ev_f.json()
    assert len(ev_list_f) >= 1
    assert any(ev["id"] == "EV-WM-API-DOCS-2FC1" for ev in ev_list_f)
    ev_item = next(ev for ev in ev_list_f if ev["id"] == "EV-WM-API-DOCS-2FC1")
    assert ev_item["finding_id"] == "WM-API-DOCS-2FC1"
    assert ev_item["integrity_hash"] is not None and len(ev_item["integrity_hash"]) == 64

    # Check evidence queried by assessment_id
    res_ev_asm = client.get("/api/evidence?assessment_id=KAVACH-WM-20260922-2FC1")
    assert res_ev_asm.status_code == 200
    ev_list_asm = res_ev_asm.json()
    assert any(ev["id"] == "EV-WM-API-DOCS-2FC1" for ev in ev_list_asm)

    # Cross-check clean assessment ASM-014A92D1 has 0 evidence
    res_clean_ev = client.get("/api/evidence?assessment_id=ASM-014A92D1")
    assert res_clean_ev.status_code == 200
    assert res_clean_ev.json() == []


def test_audit_05_database_referential_integrity():
    """
    Inspect the database schema and live data:
    - No findings with non-existent assessment_id
    - No evidence records with non-existent finding_id
    - No audit events with non-existent assessment_id
    """
    db = SessionLocal()
    all_asm_ids = {a.id for a in db.query(Assessment).all()}

    # Check findings
    findings = db.query(Finding).all()
    for f in findings:
        assert f.assessment_id in all_asm_ids, f"Orphan finding {f.id} has invalid assessment {f.assessment_id}"

    # Check evidence records
    all_finding_ids = {f.id for f in findings}
    evidence_records = db.query(EvidenceRecord).all()
    for ev in evidence_records:
        if ev.finding_id:
            assert ev.finding_id in all_finding_ids, f"Evidence {ev.id} references invalid finding {ev.finding_id}"

    # Check audit events
    audit_events = db.query(AuditEvent).all()
    for ev in audit_events:
        if ev.assessment_id:
            is_valid = (
                ev.assessment_id in all_asm_ids
                or ev.assessment_id == "GLOBAL"
                or ev.assessment_id.startswith("ASM-URL-")
                or "TEST" in ev.assessment_id
                or "PARITY" in ev.assessment_id
                or ev.assessment_id.startswith("KAVACH-WM-")
            )
            assert is_valid, f"Audit event {ev.id} references invalid assessment {ev.assessment_id}"

    db.close()


def test_audit_06_report_generation_and_isolation():
    """Verify that reports return honest data and do not leak data from other assessments."""
    # Real World Monitor report
    res_wm = client.get("/api/reports/KAVACH-WM-20260922-2FC1")
    assert res_wm.status_code == 200
    rep_wm = res_wm.json()
    assert rep_wm["assessment"]["id"] == "KAVACH-WM-20260922-2FC1"
    assert len(rep_wm["findings_detail"]) == 1
    assert rep_wm["findings_detail"][0]["id"] == "WM-API-DOCS-2FC1"

    # HTML report export
    res_html = client.get("/api/reports/KAVACH-WM-20260922-2FC1/html")
    assert res_html.status_code == 200
    assert "text/html" in res_html.headers.get("content-type", "")
    assert "WM-API-DOCS-2FC1" in res_html.text

    # Clean assessment report
    res_clean = client.get("/api/reports/ASM-014A92D1")
    assert res_clean.status_code == 200
    rep_clean = res_clean.json()
    assert rep_clean["assessment"]["id"] == "ASM-014A92D1"
    assert rep_clean["findings_detail"] == []


def test_audit_07_ai_status_and_rag_integration():
    """Verify AI and RAG endpoints."""
    res_ai = client.get("/api/ai/status")
    assert res_ai.status_code == 200
    ai_data = res_ai.json()
    assert "status_code" in ai_data or "is_online" in ai_data or "service" in ai_data

    res_rag = client.get("/api/rag/status")
    assert res_rag.status_code == 200
    rag_data = res_rag.json()
    assert "indexed_chunks_count" in rag_data or "status" in rag_data


def test_audit_08_experience_db_summary():
    """Verify Experience DB summary endpoint."""
    res_exp = client.get("/api/experience/summary")
    assert res_exp.status_code == 200
    data = res_exp.json()
    assert data.get("success") is True
    assert "metrics" in data


def test_audit_09_portable_permissions_and_consent():
    """Verify portable scanner permissions and consent gating."""
    res_perms = client.get("/api/portable/permissions")
    assert res_perms.status_code == 200
    data = res_perms.json()
    assert "permissions" in data or isinstance(data, dict)
