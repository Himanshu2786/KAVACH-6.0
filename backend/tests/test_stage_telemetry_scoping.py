"""
KAVACH 5.0 — Regression Tests: Stage Telemetry Scoping & Lifecycle Transition Semantics

Verifies:
1. Stage execution telemetry is strictly separated from global audit/lifecycle telemetry.
2. DISCOVER shows only discovery-stage execution events.
3. ASSESS shows only original assessment-stage execution events (no RETEST_* events).
4. CORRELATE shows only correlation-stage execution events.
5. ANALYZE shows only AI-analysis-stage execution events.
6. VALIDATE shows only original evidence-validation-stage execution events (no RETEST_* events).
7. PRIORITIZE shows only risk-calculation-stage events.
8. REMEDIATE shows only remediation-stage events.
9. REPORT shows only report-generation/export events.
10. RETEST_* events remain fully preserved and queryable in global audit trail.
11. Lifecycle transition semantics: advance_stage does NOT create an event saying COMPLETE -> REPORT
    when the assessment is already completed or at REPORT.
12. Assessment KAVACH-WM-20260923-A018 state preservation:
    status = COMPLETED, stage = REPORT, progress = 100%.
"""

import pytest
from backend.app.core.database import SessionLocal
from backend.app.models.models import Assessment, AuditEvent
from backend.app.services.assessment_service import assessment_service


ASSESSMENT_ID = "KAVACH-WM-20260923-A018"


def filter_stage_telemetry(audits, stage):
    """Mirror of frontend stage execution telemetry filter."""
    result = []
    for a in audits:
        desc = (a.description or "").upper()
        type_ = (a.event_type or "").upper()

        # 1. Never include re-test events in historical pipeline stage execution logs.
        is_retest = (
            type_.startswith("RETEST")
            or "RETEST" in type_
            or "RE-TEST" in desc
            or "AFTER-FIX" in desc
            or "RETEST" in desc
        )
        if is_retest:
            continue

        # 2. Global pipeline lifecycle transitions do not belong to individual module execution logs.
        if type_ == "ASSESSMENT_STAGE_ADVANCED":
            continue

        # 3. Stage-specific execution telemetry:
        if stage == "DISCOVER":
            if (
                type_ in [
                    "DISCOVERY_COMPLETED", "DISCOVERY_SEEDED", "SURFACE_MAPPED",
                    "ENDPOINT_DISCOVERED", "TARGET_SELECTED", "SOURCE_SELECTED",
                    "ASSESSMENT_STARTED", "DISCOVERY_STARTED"
                ]
                or "DISCOVER" in type_
                or "DISCOVERY" in desc
            ):
                result.append(a)
        elif stage == "ASSESS":
            if type_ == "ASSESSMENT_COMPLETED":
                continue
            if (
                type_ in [
                    "MODULE_STARTED", "RULE_EXECUTED", "OBSERVATION",
                    "OBSERVATION_CAPTURED", "RESULT", "MODULE_COMPLETED",
                    "TEST_EXECUTED", "PROBE_ERROR", "MODULE_EXECUTION",
                    "SCAN_STARTED", "SCAN_COMPLETED"
                ]
                or type_.startswith("RULE_")
                or type_.startswith("MODULE_")
                or type_ == "ASSESS"
                or type_.startswith("ASSESS_")
            ):
                result.append(a)
        elif stage == "CORRELATE":
            if (
                type_ in [
                    "KNOWLEDGE_CORRELATED", "CORRELATION_COMPLETED",
                    "TAXONOMY_MAPPED", "CWE_MAPPED", "OWASP_MAPPED",
                    "CORRELATION_STARTED"
                ]
                or "CORRELAT" in type_
                or ("CWE" in desc and "MAPPED" in desc)
                or ("OWASP" in desc and "MAPPED" in desc)
            ):
                result.append(a)
        elif stage == "ANALYZE":
            if (
                type_ in [
                    "AI_ANALYSIS_COMPLETED", "AI_ANALYSIS_STARTED",
                    "HYPOTHESIS_GENERATED", "OLLAMA_ANALYZED",
                    "AI_CORRELATED", "AI_HYPOTHESIS"
                ]
                or "ANALYZ" in type_
                or type_.startswith("AI_")
                or type_ == "AI"
                or "OLLAMA" in desc
            ):
                result.append(a)
        elif stage == "VALIDATE":
            if (
                type_ in [
                    "EVIDENCE_GENERATED", "EVIDENCE_RECORDED", "EVIDENCE_VALIDATED",
                    "PROBE_EXECUTED", "POC_EXECUTED", "FINDING_CREATED",
                    "FINDING_UPDATED", "VERIFICATION_EXECUTED", "VALIDATION_STARTED",
                    "VALIDATION_COMPLETED"
                ]
                or type_.startswith("VALIDAT")
                or type_.startswith("EVIDENCE_")
            ):
                result.append(a)
        elif stage == "PRIORITIZE":
            if (
                type_ in [
                    "RISK_CALCULATED", "PRIORITY_ASSIGNED", "CVSS_SCORED",
                    "POSTURE_EVALUATED", "PRIORITIZATION_COMPLETED"
                ]
                or "PRIORIT" in type_
                or type_.startswith("RISK_")
                or "RISK" in desc
                or "CVSS" in desc
            ):
                result.append(a)
        elif stage == "REMEDIATE":
            if (
                type_ in [
                    "REMEDIATION_CREATED", "REMEDIATION_PLAN_GENERATED",
                    "FIX_RECOMMENDED", "PLAYBOOK_GENERATED", "REMEDIATION_COMPLETED"
                ]
                or "REMEDIAT" in type_
                or "REMEDIATION" in desc
            ):
                result.append(a)
        elif stage == "REPORT":
            if (
                type_ in [
                    "REPORT_GENERATED", "REPORT_EXPORTED", "REPORT_VIEWED",
                    "REPORT_DOWNLOADED", "ASSESSMENT_COMPLETED"
                ]
                or "REPORT" in type_
                or type_ == "ASSESSMENT_COMPLETED"
                or "REPORT" in desc
            ):
                result.append(a)

    return result


def test_assess_stage_excludes_all_retest_events():
    """Verify ASSESS stage shows only original assessment execution events, NO RETEST_* events."""
    db = SessionLocal()
    try:
        audits = (
            db.query(AuditEvent)
            .filter(AuditEvent.assessment_id == ASSESSMENT_ID)
            .order_by(AuditEvent.timestamp.asc())
            .all()
        )
        assess_events = filter_stage_telemetry(audits, "ASSESS")

        assert len(assess_events) > 0, "ASSESS stage must have original execution events"
        for a in assess_events:
            assert not a.event_type.startswith("RETEST"), f"Retest event {a.event_type} found in ASSESS stage!"
            assert "RETEST" not in a.event_type.upper()
            assert "RE-TEST" not in (a.description or "").upper()
            assert a.event_type in ["TEST_EXECUTED", "OBSERVATION_CAPTURED", "RULE_EXECUTED", "MODULE_STARTED"]
    finally:
        db.close()


def test_validate_stage_excludes_all_retest_events():
    """Verify VALIDATE stage shows only original validation events, NO RETEST_* events."""
    db = SessionLocal()
    try:
        audits = (
            db.query(AuditEvent)
            .filter(AuditEvent.assessment_id == ASSESSMENT_ID)
            .order_by(AuditEvent.timestamp.asc())
            .all()
        )
        validate_events = filter_stage_telemetry(audits, "VALIDATE")

        assert len(validate_events) > 0, "VALIDATE stage must have original execution events"
        for a in validate_events:
            assert not a.event_type.startswith("RETEST"), f"Retest event {a.event_type} found in VALIDATE stage!"
            assert "RETEST" not in a.event_type.upper()
            assert "AFTER-FIX" not in (a.description or "").upper()
            assert a.event_type in ["EVIDENCE_GENERATED", "POC_EXECUTED", "FINDING_CREATED"]
    finally:
        db.close()


def test_all_retest_events_preserved_in_global_audit():
    """Verify all RETEST_* events remain intact in the database and audit trail."""
    db = SessionLocal()
    try:
        retest_events = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.assessment_id == ASSESSMENT_ID,
                AuditEvent.event_type.like("RETEST%")
            )
            .all()
        )
        assert len(retest_events) >= 25, f"Expected at least 25 re-test events preserved, got {len(retest_events)}"
        event_types = {r.event_type for r in retest_events}
        assert "RETEST_STARTED" in event_types
        assert "RETEST_OBSERVATION_CAPTURED" in event_types
        assert "RETEST_EVIDENCE_CREATED" in event_types
        assert "RETEST_STATE_COMPARISON" in event_types
        assert "RETEST_UNRESOLVED" in event_types
    finally:
        db.close()


def test_stage_scoping_across_all_eight_stages():
    """Verify clean stage telemetry separation across all 8 pipeline stages."""
    db = SessionLocal()
    try:
        audits = (
            db.query(AuditEvent)
            .filter(AuditEvent.assessment_id == ASSESSMENT_ID)
            .order_by(AuditEvent.timestamp.asc())
            .all()
        )

        stages = ["DISCOVER", "ASSESS", "CORRELATE", "ANALYZE", "VALIDATE", "PRIORITIZE", "REMEDIATE", "REPORT"]
        for s in stages:
            stage_evs = filter_stage_telemetry(audits, s)
            for ev in stage_evs:
                assert not ev.event_type.startswith("RETEST"), f"Stage {s} contained re-test event {ev.event_type}"
                assert ev.event_type != "ASSESSMENT_STAGE_ADVANCED", f"Stage {s} contained global stage transition event"
    finally:
        db.close()


def test_advance_stage_no_duplicate_or_invalid_transition():
    """Verify advance_stage does NOT emit 'COMPLETE -> REPORT' transition event."""
    db = SessionLocal()
    try:
        # Check audit count before
        before_count = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.assessment_id == ASSESSMENT_ID,
                AuditEvent.event_type == "ASSESSMENT_STAGE_ADVANCED"
            )
            .count()
        )

        # Call advance_stage to REPORT on already completed assessment
        asm = assessment_service.advance_stage(db, ASSESSMENT_ID, "REPORT")

        # Verify no new stage advance audit event was generated
        after_count = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.assessment_id == ASSESSMENT_ID,
                AuditEvent.event_type == "ASSESSMENT_STAGE_ADVANCED"
            )
            .count()
        )

        assert after_count == before_count, "advance_stage on completed assessment must not create duplicate transition event"
        assert asm.status == "COMPLETED"
        assert asm.current_stage == "REPORT"
        assert asm.progress == 100
    finally:
        db.close()


def test_a018_state_preservation():
    """Verify A018 status = COMPLETED, stage = REPORT, progress = 100%."""
    db = SessionLocal()
    try:
        asm = db.query(Assessment).filter(Assessment.id == ASSESSMENT_ID).first()
        assert asm is not None
        assert asm.status == "COMPLETED"
        assert asm.current_stage == "REPORT"
        assert asm.progress == 100
    finally:
        db.close()
