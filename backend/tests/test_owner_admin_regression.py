"""
KAVACH 6.0 — Developer / Owner Admin Regression Test Suite
Verifies:
1. OWNER sees Developer / Owner Admin (role validation)
2. TEAM_USER does not see Developer / Owner Admin (role validation)
3. OWNER can access Owner Admin endpoints
4. TEAM_USER receives authorization failure (403 Forbidden) on direct Owner Admin access
5. Team activity is persisted
6. Owner can filter activity by team member
7. Meaningful-use classification works (LOGIN ONLY, ACTIVE USE, MEANINGFUL USE)
8. Feedback appears in Feedback Review
9. Passwords/tokens/secrets never appear in activity logs
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import Base, engine, SessionLocal, migrate_schema
from backend.app.data.seed_data import seed_database
from backend.app.core.security import sanitize_log_dict
from backend.app.models.models import UserActivity, UserFeedback

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    migrate_schema(engine)
    db = SessionLocal()
    seed_database(db)
    db.close()
    yield

def get_tokens():
    admin_pw = os.getenv("KAVACH_ADMIN_PASSWORD", "Kavach@Admin2026!")
    team_pw = os.getenv("KAVACH_TEAM_PASSWORD", "Kavach@Team2026!")

    admin_login = client.post("/api/auth/login", json={"username": "ADMIN001", "password": admin_pw})
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]

    team_login = client.post("/api/auth/login", json={"username": "TEAM001", "password": team_pw})
    assert team_login.status_code == 200
    team_token = team_login.json()["access_token"]

    return admin_token, team_token

def test_1_owner_role_validation():
    """1. OWNER identity has proper role."""
    admin_token, _ = get_tokens()
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    user = res.json()["user"]
    assert user["id"] == "ADMIN001"
    assert user["role"].lower() in ("admin", "developer_owner")

def test_2_team_user_role_validation():
    """2. TEAM_USER identity does not have owner role."""
    _, team_token = get_tokens()
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {team_token}"})
    assert res.status_code == 200
    user = res.json()["user"]
    assert user["id"] == "TEAM001"
    assert user["role"].lower() not in ("admin", "developer_owner")

def test_3_owner_can_access_owner_admin():
    """3. OWNER can access Owner Admin endpoints."""
    admin_token, _ = get_tokens()
    headers = {"Authorization": f"Bearer {admin_token}"}

    users_res = client.get("/api/admin/users", headers=headers)
    assert users_res.status_code == 200
    assert len(users_res.json()["users"]) >= 5

    activity_res = client.get("/api/admin/activity", headers=headers)
    assert activity_res.status_code == 200
    assert "activities" in activity_res.json()

    summary_res = client.get("/api/admin/activity/summary", headers=headers)
    assert summary_res.status_code == 200
    assert "summary" in summary_res.json()

    feedback_res = client.get("/api/admin/feedback", headers=headers)
    assert feedback_res.status_code == 200
    assert "feedbacks" in feedback_res.json()

def test_4_team_user_receives_403_on_owner_admin():
    """4. TEAM_USER receives 403 Forbidden on direct Owner Admin access."""
    _, team_token = get_tokens()
    headers = {"Authorization": f"Bearer {team_token}"}

    users_res = client.get("/api/admin/users", headers=headers)
    assert users_res.status_code == 403

    activity_res = client.get("/api/admin/activity", headers=headers)
    assert activity_res.status_code == 403

    summary_res = client.get("/api/admin/activity/summary", headers=headers)
    assert summary_res.status_code == 403

    feedback_res = client.get("/api/admin/feedback", headers=headers)
    assert feedback_res.status_code == 403

def test_5_team_activity_persistence():
    """5. Team activity is persisted into the database."""
    _, team_token = get_tokens()
    headers = {"Authorization": f"Bearer {team_token}"}

    log_res = client.post("/api/activity/log", json={
        "event_type": "ASSESSMENT_VIEWED",
        "module": "COMMAND_CENTER",
        "assessment_id": "ASM-TEST-PERSIST-001",
        "status": "SUCCESS",
        "details": {"action": "viewed_command_center", "target": "https://test.local"}
    }, headers=headers)
    assert log_res.status_code == 200
    assert log_res.json()["success"] is True

    # Verify event is in database
    db = SessionLocal()
    event = db.query(UserActivity).filter(
        UserActivity.user_id == "TEAM001",
        UserActivity.event_type == "ASSESSMENT_VIEWED"
    ).first()
    assert event is not None
    assert event.assessment_id == "ASM-TEST-PERSIST-001"
    db.close()

def test_6_owner_filter_activity_by_team_member():
    """6. Owner can filter activity by team member."""
    admin_token, _ = get_tokens()
    headers = {"Authorization": f"Bearer {admin_token}"}

    res = client.get("/api/admin/activity?user_id=TEAM001", headers=headers)
    assert res.status_code == 200
    activities = res.json()["activities"]
    assert len(activities) > 0
    for ev in activities:
        assert ev["user_id"] == "TEAM001"

def test_7_meaningful_use_classification():
    """7. Meaningful-use classification deterministic evaluation."""
    admin_token, team_token = get_tokens()
    
    # Log meaningful activity for TEAM001
    client.post("/api/activity/log", json={
        "event_type": "EVIDENCE_VIEWED",
        "module": "EVIDENCE",
        "assessment_id": "ASM-TEST-PERSIST-001",
        "finding_id": "FIND-001",
        "status": "SUCCESS"
    }, headers={"Authorization": f"Bearer {team_token}"})

    # Summary check
    res = client.get("/api/admin/activity/summary", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    summary = res.json()["summary"]
    team001_summary = next((s for s in summary if s["user_id"] == "TEAM001"), None)
    assert team001_summary is not None
    assert team001_summary["usage_category"] == "MEANINGFUL USE"

def test_8_feedback_appears_in_feedback_review():
    """8. Feedback appears in Owner Feedback Review."""
    _, team_token = get_tokens()
    admin_token, _ = get_tokens()

    # Team submits feedback
    fb_res = client.post("/api/feedback/submit", json={
        "rating": 5,
        "what_worked": "Comprehensive reporting and live forensic hashing",
        "what_confusing": "None, smooth workflow",
        "what_slow": "Ollama local model startup",
        "bug_description": "",
        "suggestions": "Add multi-language export"
    }, headers={"Authorization": f"Bearer {team_token}"})
    assert fb_res.status_code == 200

    # Owner reviews feedback
    rev_res = client.get("/api/admin/feedback", headers={"Authorization": f"Bearer {admin_token}"})
    assert rev_res.status_code == 200
    feedbacks = rev_res.json()["feedbacks"]
    assert len(feedbacks) > 0
    found = any(f["what_worked"] == "Comprehensive reporting and live forensic hashing" for f in feedbacks)
    assert found is True

def test_9_passwords_secrets_never_appear_in_activity():
    """9. Passwords, tokens, and secrets are sanitized from activity logs."""
    dirty_data = {
        "user": "TEAM001",
        "password": "SuperSecretPassword123!",
        "access_token": "eyJh...sensitive_jwt_token",
        "api_key": "kavach_secret_key_999",
        "client_secret": "hidden_secret",
        "safe_field": "public_data"
    }

    clean_data = sanitize_log_dict(dirty_data)
    assert clean_data["password"] == "[REDACTED]"
    assert clean_data["access_token"] == "[REDACTED]"
    assert clean_data["api_key"] == "[REDACTED]"
    assert clean_data["client_secret"] == "[REDACTED]"
    assert clean_data["safe_field"] == "public_data"
