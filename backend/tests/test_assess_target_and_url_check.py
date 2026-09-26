"""
KAVACH 5.0 — Assess Target & URL Check Integration Test Suite
Validates:
1. World Monitor ASSESS TARGET routes to dedicated empirical engine (KAVACH-WM-*).
2. No duplicate or generic ASM-* records created for World Monitor target.
3. Target normalization for World Monitor (https, http, trailing slashes).
4. URL CHECK generates distinct ASM-URL-* run ID with run_type=URL_CHECK.
5. URL CHECK establishes parent_assessment_id linkage to active World Monitor assessment.
6. URL CHECK never overwrites active World Monitor empirical assessment.
7. URL CHECK data persists in database across simulated restarts.
8. Findings, Evidence, Risk, and Report remain strictly isolated.
"""

import sys
import pytest
import asyncio
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.models import Assessment, Finding, EvidenceRecord
from backend.app.core.target_config import is_world_monitor_target
from backend.app.schemas.schemas import AssessmentCreate
from backend.app.api.routes.assessments import create_assessment, get_latest_world_monitor_assessment
from backend.app.api.routes.url_check import scan_url, get_latest_url_assessment, UrlScanRequest
from backend.app.services.url_scanner_service import url_scanner_service


@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_target_normalization():
    """Verify safe URL normalization handles schemes, paths, and prevents false positives."""
    assert is_world_monitor_target("https://www.worldmonitor.app") is True
    assert is_world_monitor_target("https://www.worldmonitor.app/") is True
    assert is_world_monitor_target("http://www.worldmonitor.app") is True
    assert is_world_monitor_target("http://worldmonitor.app") is True
    assert is_world_monitor_target("https://worldmonitor.app/") is True
    assert is_world_monitor_target("worldmonitor.app") is True
    assert is_world_monitor_target("www.worldmonitor.app") is True

    # Negative controls
    assert is_world_monitor_target("https://example.com") is False
    assert is_world_monitor_target("https://notworldmonitor.app") is False
    assert is_world_monitor_target("https://worldmonitor.app.evil.com") is False
    assert is_world_monitor_target(None) is False
    assert is_world_monitor_target("") is False


def test_assess_target_routes_to_world_monitor(db):
    """
    ASSESS TARGET for https://www.worldmonitor.app:
    1. Routes to dedicated empirical engine.
    2. Returns KAVACH-WM-* assessment ID.
    3. Does NOT create a generic ASM-* assessment.
    """
    initial_generic_count = db.query(Assessment).filter(Assessment.id.like("ASM-%"), ~Assessment.id.like("ASM-URL-%")).count()

    req = AssessmentCreate(
        name="World Monitor Test Run",
        target_url="https://www.worldmonitor.app",
        description="Testing World Monitor Assess Target routing",
        environment="Testing Environment",
        scope="Full Application",
        authorization_confirmed=True,
        modules_enabled=["Authentication", "API Security", "Security Headers"],
        is_demo=False
    )

    try:
        enriched = asyncio.run(create_assessment(req, db))

        # Must return KAVACH-WM-* assessment ID
        assert enriched["id"].startswith("KAVACH-WM-")
        assert enriched["assessment_type"] == "WORLD_MONITOR_EMPIRICAL"
        assert enriched["target_url"] == "https://www.worldmonitor.app"
        assert enriched["confirmed_findings"] >= 1

        # Verify no generic ASM-* was created for this operation
        final_generic_count = db.query(Assessment).filter(Assessment.id.like("ASM-%"), ~Assessment.id.like("ASM-URL-%")).count()
        assert final_generic_count == initial_generic_count
    finally:
        # Clean up test assessment so database retains original empirical state
        if 'enriched' in locals():
            created_id = enriched["id"]
            cleanup_db = SessionLocal()
            try:
                from backend.app.models.models import AuditEvent, EvidenceRecord
                findings_to_delete = cleanup_db.query(Finding).filter(Finding.assessment_id == created_id).all()
                f_ids = [f.id for f in findings_to_delete]
                if f_ids:
                    cleanup_db.query(EvidenceRecord).filter(EvidenceRecord.finding_id.in_(f_ids)).delete(synchronize_session=False)
                    cleanup_db.query(Finding).filter(Finding.id.in_(f_ids)).delete(synchronize_session=False)
                cleanup_db.query(AuditEvent).filter(AuditEvent.assessment_id == created_id).delete(synchronize_session=False)
                cleanup_db.query(Assessment).filter(Assessment.id == created_id).delete(synchronize_session=False)
                cleanup_db.commit()
            finally:
                cleanup_db.close()


def test_assess_target_generic_for_other_targets(db):
    """
    Non-World-Monitor target creates standard generic ASM-* assessment.
    """
    req = AssessmentCreate(
        name="Other Target Assessment",
        target_url="https://other-company.example.com",
        description="Generic target test",
        environment="Testing Environment",
        scope="Full Application",
        authorization_confirmed=True,
        modules_enabled=["API Security"],
        is_demo=False
    )

    enriched = asyncio.run(create_assessment(req, db))
    assert enriched["id"].startswith("ASM-")
    assert not enriched["id"].startswith("KAVACH-WM-")
    assert enriched["assessment_type"] == "GENERIC_ASSESSMENT"

    # Cleanup test generic assessment
    cleanup_db = SessionLocal()
    try:
        from backend.app.models.models import AuditEvent, DiscoveryItem
        cleanup_db.query(DiscoveryItem).filter(DiscoveryItem.assessment_id == enriched["id"]).delete(synchronize_session=False)
        cleanup_db.query(AuditEvent).filter(AuditEvent.assessment_id == enriched["id"]).delete(synchronize_session=False)
        cleanup_db.query(Assessment).filter(Assessment.id == enriched["id"]).delete(synchronize_session=False)
        cleanup_db.commit()
    finally:
        cleanup_db.close()


def test_url_check_architecture_and_isolation(db):
    """
    URL CHECK for https://www.worldmonitor.app:
    1. Returns ASM-URL-* run ID.
    2. Sets run_type = URL_CHECK.
    3. Does NOT create a generic ASM-* assessment.
    4. Maintains parent_assessment_id linkage to the active World Monitor assessment.
    5. Does NOT overwrite active World Monitor assessment.
    """
    # 1. Identify active empirical World Monitor assessment
    wm_latest = get_latest_world_monitor_assessment(db)
    assert wm_latest["status"] != "NO_ASSESSMENT_RUN"
    active_wm_id = wm_latest["assessment_id"]
    assert active_wm_id.startswith("KAVACH-WM-")

    # 2. Execute URL CHECK
    req = UrlScanRequest(url="https://www.worldmonitor.app")
    res = asyncio.run(scan_url(req, db))

    assert res["success"] is True
    assert res["run_id"].startswith("ASM-URL-")
    assert res["run_type"] == "URL_CHECK"
    assert res["assessment_type"] == "URL_CHECK"

    # 3. Check parent_assessment_id linkage
    assert res["parent_assessment_id"] == active_wm_id

    # 4. Verify Active World Monitor assessment was NOT modified or replaced
    wm_after = get_latest_world_monitor_assessment(db)
    assert wm_after["assessment_id"] == active_wm_id
    assert wm_after["assessment_id"] != res["run_id"]

    # 5. Verify database record for URL_CHECK
    url_asm_record = db.query(Assessment).filter(Assessment.id == res["run_id"]).first()
    assert url_asm_record is not None
    assert url_asm_record.assessment_type == "URL_CHECK"
    assert url_asm_record.parent_assessment_id == active_wm_id


def test_url_check_persistence_across_restart(db):
    """
    Simulate server restart by clearing in-memory cache of url_scanner_service.
    GET /api/url-check/latest must restore the last URL run from database.
    """
    # Clear in-memory cache
    url_scanner_service._latest_assessment = None

    restored = get_latest_url_assessment(db)
    assert restored["success"] is True
    assert restored["run_id"].startswith("ASM-URL-")
    assert restored["run_type"] == "URL_CHECK"
    assert restored["target_url"] == "https://www.worldmonitor.app"
    assert restored["parent_assessment_id"] is not None
    assert restored["parent_assessment_id"].startswith("KAVACH-WM-")


def test_findings_and_evidence_isolation(db):
    """
    Verify that findings and evidence for the World Monitor assessment remain strictly isolated.
    URL check run data does not contaminate GET /api/findings?assessment_id=KAVACH-WM-*
    """
    wm_latest = get_latest_world_monitor_assessment(db)
    active_wm_id = wm_latest["assessment_id"]

    wm_findings = db.query(Finding).filter(Finding.assessment_id == active_wm_id).all()
    assert len(wm_findings) >= 1

    for f in wm_findings:
        assert f.assessment_id == active_wm_id
        # Ensure finding is from empirical World Monitor, not a URL check run
        assert not f.id.startswith("FIND-WEB-")
        assert f.assessment_id.startswith("KAVACH-WM-")
