import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import Base, engine, SessionLocal, migrate_schema
from backend.app.data.seed_data import seed_database
from backend.app.models.models import User, Assessment

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def init_test_environment():
    Base.metadata.create_all(bind=engine)
    migrate_schema(engine)
    db = SessionLocal()
    seed_database(db)
    db.close()
    yield

def test_production_seed_accounts_exist():
    """Verify standard team and admin accounts are provisioned."""
    db = SessionLocal()
    users = db.query(User).all()
    user_ids = [u.id for u in users]
    db.close()

    assert "ADMIN001" in user_ids
    assert "TEAM001" in user_ids
    assert "TEAM002" in user_ids
    assert "TEAM003" in user_ids
    assert "TEAM004" in user_ids

def test_login_success_admin():
    admin_pw = os.getenv("KAVACH_ADMIN_PASSWORD", "Kavach@Admin2026!")
    res = client.post("/api/auth/login", json={
        "username": "ADMIN001",
        "password": admin_pw
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["id"] == "ADMIN001"
    assert data["user"]["role"] == "admin"

def test_login_success_team_member():
    team_pw = os.getenv("KAVACH_TEAM_PASSWORD", "Kavach@Team2026!")
    res = client.post("/api/auth/login", json={
        "username": "TEAM001",
        "password": team_pw
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["id"] == "TEAM001"
    assert data["user"]["role"] == "team_member"

def test_login_failure_invalid_password():
    res = client.post("/api/auth/login", json={
        "username": "ADMIN001",
        "password": "WrongPassword123!"
    })
    assert res.status_code == 401
    assert "Incorrect" in res.json()["detail"] or "Invalid" in res.json()["detail"]

def test_login_failure_unknown_user():
    res = client.post("/api/auth/login", json={
        "username": "NON_EXISTENT_USER",
        "password": "Password123!"
    })
    assert res.status_code == 401

def test_auth_me_endpoint():
    admin_pw = os.getenv("KAVACH_ADMIN_PASSWORD", "Kavach@Admin2026!")
    login_res = client.post("/api/auth/login", json={
        "username": "ADMIN001",
        "password": admin_pw
    })
    token = login_res.json()["access_token"]

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()["user"]
    assert me_data["id"] == "ADMIN001"
    assert me_data["role"] == "admin"

def test_role_authorization_admin_users_list():
    admin_pw = os.getenv("KAVACH_ADMIN_PASSWORD", "Kavach@Admin2026!")
    team_pw = os.getenv("KAVACH_TEAM_PASSWORD", "Kavach@Team2026!")

    # Admin should be allowed to view users
    admin_login = client.post("/api/auth/login", json={"username": "ADMIN001", "password": admin_pw})
    admin_token = admin_login.json()["access_token"]
    admin_res = client.get("/api/auth/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_res.status_code == 200
    assert len(admin_res.json()["users"]) >= 5

    # Team member should be blocked (403 Forbidden)
    team_login = client.post("/api/auth/login", json={"username": "TEAM001", "password": team_pw})
    team_token = team_login.json()["access_token"]
    team_res = client.get("/api/auth/users", headers={"Authorization": f"Bearer {team_token}"})
    assert team_res.status_code == 403

def test_cross_user_data_isolation():
    team_pw = os.getenv("KAVACH_TEAM_PASSWORD", "Kavach@Team2026!")
    admin_pw = os.getenv("KAVACH_ADMIN_PASSWORD", "Kavach@Admin2026!")

    # 1. TEAM001 logs in and creates an assessment
    t1_login = client.post("/api/auth/login", json={"username": "TEAM001", "password": team_pw})
    t1_token = t1_login.json()["access_token"]

    t1_create = client.post("/api/assessments", json={
        "name": "TEAM001 Private Assessment",
        "target_url": "https://team001-target.internal",
        "description": "Assessment owned by Team 001",
        "environment": "Staging",
        "scope": "Target Domain Surface",
        "authorization_confirmed": True,
        "modules_enabled": ["API Security"]
    }, headers={"Authorization": f"Bearer {t1_token}"})
    assert t1_create.status_code == 200
    t1_asm_id = t1_create.json()["id"]

    # 2. TEAM002 logs in and lists assessments
    t2_login = client.post("/api/auth/login", json={"username": "TEAM002", "password": team_pw})
    t2_token = t2_login.json()["access_token"]
    t2_list = client.get("/api/assessments", headers={"Authorization": f"Bearer {t2_token}"})
    assert t2_list.status_code == 200
    t2_ids = [a["id"] for a in t2_list.json()]
    # TEAM002 should NOT see TEAM001's private assessment
    assert t1_asm_id not in t2_ids

    # 3. ADMIN001 logs in and lists assessments -> ADMIN sees all assessments
    admin_login = client.post("/api/auth/login", json={"username": "ADMIN001", "password": admin_pw})
    admin_token = admin_login.json()["access_token"]
    admin_list = client.get("/api/assessments", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_list.status_code == 200
    admin_ids = [a["id"] for a in admin_list.json()]
    assert t1_asm_id in admin_ids
