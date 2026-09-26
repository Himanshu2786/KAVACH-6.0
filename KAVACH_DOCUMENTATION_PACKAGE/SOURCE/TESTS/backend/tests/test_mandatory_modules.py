"""
Unit tests for KAVACH Mandatory Modules:
- Team Desk (Module 8)
- Experience DB (Module 7)
- Test Center (Module 9)
- Audit Trail (Module 10)
"""

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import Base, engine, SessionLocal, migrate_schema
from backend.app.data.seed_data import seed_database

client = TestClient(app)

def setup_module():
    Base.metadata.create_all(bind=engine)
    migrate_schema(engine)
    db = SessionLocal()
    seed_database(db)
    db.close()

def test_team_desk_members():
    res = client.get("/api/team/members")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["team_members"]) >= 5
    roles = [m["role"] for m in data["team_members"]]
    assert any("Triage" in r for r in roles)

def test_team_desk_assignments_and_workflow():
    res = client.get("/api/team/assignments")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["assignments"]) > 0

    first_finding_id = data["assignments"][0]["finding_id"]
    
    # Assign finding
    assign_res = client.post("/api/team/assign", json={
        "finding_id": first_finding_id,
        "assigned_to": "Lead SecOps Engineer",
        "triage_status": "IN_PROGRESS",
        "notes": "Assigned for manual header validation"
    })
    assert assign_res.status_code == 200
    assign_data = assign_res.json()
    assert assign_data["success"] is True
    assert assign_data["finding"]["assigned_to"] == "Lead SecOps Engineer"
    assert assign_data["finding"]["triage_status"] == "IN_PROGRESS"

    # Add note
    note_res = client.post("/api/team/notes", json={
        "finding_id": first_finding_id,
        "notes": "Verified probe results locally"
    })
    assert note_res.status_code == 200
    note_data = note_res.json()
    assert note_data["success"] is True
    assert "Verified probe results locally" in note_data["team_notes"]

def test_experience_db():
    summary_res = client.get("/api/experience/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["success"] is True
    assert "metrics" in summary
    assert "total_assessments" in summary["metrics"]

    reverif_res = client.get("/api/experience/re-verifications")
    assert reverif_res.status_code == 200
    assert reverif_res.json()["success"] is True

    fp_res = client.get("/api/experience/false-positives")
    assert fp_res.status_code == 200
    assert fp_res.json()["success"] is True

def test_test_center_suites_and_run():
    # List suites
    suites_res = client.get("/api/test-center/suites")
    assert suites_res.status_code == 200
    suites_data = suites_res.json()
    assert suites_data["success"] is True
    assert len(suites_data["suites"]) >= 4

    # Run synthetic config audit
    run_res = client.post("/api/test-center/run", json={
        "suite_id": "synthetic_config_audit",
        "assessment_id": "TEST-SUITE-RUN"
    })
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["success"] is True
    assert run_data["suite_id"] == "synthetic_config_audit"
    assert "diff_report" in run_data
    assert len(run_data["diff_report"]) >= 4
    assert run_data["passed_checks"] >= 3
    assert "sha256_hash" in run_data["evidence"]
    assert len(run_data["evidence"]["sha256_hash"]) == 64

def test_audit_trail_filtering():
    # Check general audit trail
    audit_res = client.get("/api/system/audit?limit=20")
    assert audit_res.status_code == 200
    events = audit_res.json()
    assert isinstance(events, list)
    assert len(events) > 0

    # Filter by module TEST_CENTER
    filtered_res = client.get("/api/system/audit?module=TEST_CENTER")
    assert filtered_res.status_code == 200
    filtered_events = filtered_res.json()
    for ev in filtered_events:
        assert ev["module"] == "TEST_CENTER"
