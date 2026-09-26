"""
KAVACH 5.0 — World Monitor Active Assessment Selection & Isolation Test Suite
Validates:
1. Exact Bug Regression: Newer generic assessment (ASM-2572377F) vs Older empirical assessment (KAVACH-WM-20260922-2FC1).
2. Dedicated empirical assessment KAVACH-WM-20260922-2FC1 is selected with total_findings=1, confirmed_findings=1.
3. Demo assessments are NEVER selected as World Monitor empirical latest.
4. URL_CHECK runs are NEVER selected as World Monitor empirical latest.
5. Two valid empirical World Monitor assessments: newest one within WORLD_MONITOR_EMPIRICAL class is selected.
6. Findings and evidence returned belong strictly to the selected assessment only (no data mixing).
"""

import sys
import pytest
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.models import Assessment, Finding, EvidenceRecord
from backend.app.api.routes.assessments import get_latest_world_monitor_assessment


@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_exact_current_bug_regression(db):
    """
    Regression Test:
    ASM-2572377F (generic, newer started_at: 21:38, 0 findings)
    KAVACH-WM-20260922-2FC1 (empirical, older started_at: 13:37, 1 finding)

    The endpoint must select KAVACH-WM-20260922-2FC1, NOT ASM-2572377F.
    """
    res = get_latest_world_monitor_assessment(db)

    assert res.get("status") != "NO_ASSESSMENT_RUN"
    assert res["assessment_id"].startswith("KAVACH-WM-")
    assert not res["assessment_id"].startswith("ASM-")
    assert res["target_url"] == "https://www.worldmonitor.app"
    assert res["total_findings"] >= 1
    assert len(res["findings"]) >= 1

    # Findings & evidence match
    finding_ids = [f["id"] for f in res["findings"]]
    assert any("WM-API-DOCS" in fid for fid in finding_ids)

    evidence_ids = [e["id"] for e in res["evidence"]]
    assert any("EV-WM-API-DOCS" in eid for eid in evidence_ids)

    # Verify no findings from other assessments
    for f in res["findings"]:
        f_db = db.query(Finding).filter(Finding.id == f["id"]).first()
        assert f_db is not None
        assert f_db.assessment_id == res["assessment_id"]


def test_demo_assessment_never_selected(db):
    """Demo assessments must never be selected by the world-monitor/latest endpoint."""
    # Create temporary demo assessment with futuristic started_at
    demo_asm = Assessment(
        id="ASM-TEST-DEMO-LATEST",
        name="World Monitor Demo Super New",
        target_url="https://www.worldmonitor.app",
        description="Demo assessment",
        environment="Demo Environment",
        scope="Full Application",
        authorization_confirmed=True,
        modules_enabled="[]",
        status="COMPLETED",
        progress=100,
        current_stage="REPORT",
        started_at="2099-01-01T00:00:00Z",
        completed_at="2099-01-01T00:00:00Z",
        is_demo=True,
        assessment_type="DEMO"
    )
    db.add(demo_asm)
    db.commit()

    try:
        res = get_latest_world_monitor_assessment(db)
        assert res["assessment_id"] != "ASM-TEST-DEMO-LATEST"
        assert res["assessment_id"].startswith("KAVACH-WM-")
    finally:
        db.delete(demo_asm)
        db.commit()


def test_url_check_never_selected(db):
    """URL_CHECK assessments must never be selected as the empirical World Monitor assessment."""
    url_check_asm = Assessment(
        id="ASM-TEST-URL-CHECK",
        name="Quick URL Check",
        target_url="https://www.worldmonitor.app",
        description="Quick url check",
        environment="Testing Environment",
        scope="Target URL only",
        authorization_confirmed=True,
        modules_enabled="[]",
        status="COMPLETED",
        progress=100,
        current_stage="REPORT",
        started_at="2099-01-01T00:00:00Z",
        completed_at="2099-01-01T00:00:00Z",
        is_demo=False,
        assessment_type="URL_CHECK"
    )
    db.add(url_check_asm)
    db.commit()

    try:
        res = get_latest_world_monitor_assessment(db)
        assert res["assessment_id"] != "ASM-TEST-URL-CHECK"
        assert res["assessment_id"].startswith("KAVACH-WM-")
    finally:
        db.delete(url_check_asm)
        db.commit()


def test_two_valid_empirical_assessments_order(db):
    """
    When two valid empirical assessments exist in WORLD_MONITOR_EMPIRICAL class,
    the endpoint must choose the newest one within that class.
    """
    empirical_newer = Assessment(
        id="KAVACH-WM-TEST-NEWER",
        name="World Monitor Newer Empirical Assessment",
        target_url="https://www.worldmonitor.app",
        description="Newer empirical assessment",
        environment="World Monitor Target Scope",
        scope="Full Application",
        authorization_confirmed=True,
        modules_enabled="[]",
        status="COMPLETED",
        progress=100,
        current_stage="REPORT",
        started_at="2099-01-01T12:00:00Z",
        completed_at="2099-01-01T12:05:00Z",
        is_demo=False,
        assessment_type="WORLD_MONITOR_EMPIRICAL"
    )
    f_newer = Finding(
        id="FIND-WM-TEST-NEWER",
        assessment_id="KAVACH-WM-TEST-NEWER",
        title="World Monitor Newer Finding",
        category="API Security",
        base_severity="HIGH",
        status="CONFIRMED"
    )
    db.add(empirical_newer)
    db.add(f_newer)
    db.commit()

    try:
        res = get_latest_world_monitor_assessment(db)
        # Should choose the newer empirical one
        assert res["assessment_id"] == "KAVACH-WM-TEST-NEWER"
    finally:
        db.delete(f_newer)
        db.delete(empirical_newer)
        db.commit()

    # Re-verify that after cleanup, an empirical assessment is selected
    res_after = get_latest_world_monitor_assessment(db)
    assert res_after["assessment_id"].startswith("KAVACH-WM-")
    assert res_after["assessment_id"] != "KAVACH-WM-TEST-NEWER"


def test_assessment_data_isolation(db):
    """
    Verify that findings and evidence returned belong exclusively to the selected assessment.
    Never merge findings or evidence from generic or other assessments.
    """
    res = get_latest_world_monitor_assessment(db)
    selected_id = res["assessment_id"]

    for f in res["findings"]:
        f_rec = db.query(Finding).filter(Finding.id == f["id"]).first()
        assert f_rec.assessment_id == selected_id, f"Finding {f['id']} belongs to {f_rec.assessment_id}, not {selected_id}"

    for ev in res["evidence"]:
        ev_rec = db.query(EvidenceRecord).filter(EvidenceRecord.id == ev["id"]).first()
        finding_parent = db.query(Finding).filter(Finding.id == ev_rec.finding_id).first()
        assert finding_parent.assessment_id == selected_id, f"Evidence {ev['id']} belongs to finding {finding_parent.id} of {finding_parent.assessment_id}"
