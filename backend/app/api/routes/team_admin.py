"""
KAVACH 6.0 - Owner / Developer Administrative & Analytics API Routes
Provides team user creation, account activation/deactivation, password reset,
deterministic activity inspection, meaningful usage analytics, and feedback reviews.
Protected strictly by require_owner dependency.
"""

import uuid
import json
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.database import get_db
from backend.app.core.auth import require_owner
from backend.app.core.security import get_password_hash
from backend.app.models.models import User, UserSession, UserActivity, UserFeedback, Assessment

router = APIRouter(prefix="/admin", tags=["Owner Administration"])

class CreateUserRequest(BaseModel):
    user_id: str
    password: str
    full_name: Optional[str] = ""
    role: Optional[str] = "TEAM_USER"

class UpdateStatusRequest(BaseModel):
    is_active: bool

class ResetPasswordRequest(BaseModel):
    new_password: str

@router.get("/users")
def list_team_users(
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """List all team accounts with login timestamps and assessment metrics (No artificial user limit)."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    user_list = []
    
    for u in users:
        asm_count = db.query(Assessment).filter((Assessment.owner_id == u.user_id) | (Assessment.owner_id == u.id)).count()
        sess_count = db.query(UserSession).filter(UserSession.user_id == u.user_id).count()
        act_count = db.query(UserActivity).filter(UserActivity.user_id == u.user_id).count()
        
        user_list.append({
            "user_id": u.user_id,
            "role": u.role,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "created_at": u.created_at,
            "first_login_at": u.first_login_at,
            "last_login_at": u.last_login_at,
            "last_active_at": u.last_active_at,
            "assessments_count": asm_count,
            "sessions_count": sess_count,
            "activities_count": act_count
        })
        
    return {
        "success": True,
        "count": len(user_list),
        "users": user_list
    }

@router.post("/users")
def create_team_user(
    req: CreateUserRequest,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """Create a new team member account with designated USER ID and password."""
    clean_id = req.user_id.strip().upper()
    if not clean_id:
        raise HTTPException(status_code=400, detail="USER ID cannot be blank.")
    
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    
    existing = db.query(User).filter(User.user_id == clean_id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"User ID {clean_id} already exists.")
    
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    new_user = User(
        id=f"USR-{uuid.uuid4().hex[:12]}",
        user_id=clean_id,
        password_hash=get_password_hash(req.password),
        role=req.role if req.role in ("DEVELOPER_OWNER", "TEAM_USER") else "TEAM_USER",
        full_name=req.full_name or clean_id,
        is_active=True,
        created_at=now_str
    )
    db.add(new_user)
    
    # Audit log user creation
    admin_activity = UserActivity(
        id=f"ACT-{uuid.uuid4().hex[:12]}",
        user_id=owner.user_id,
        event_type="USER_CREATED",
        timestamp=now_str,
        module="ADMIN",
        details_json=json.dumps({"target_user_id": clean_id, "role": new_user.role}),
        status="SUCCESS"
    )
    db.add(admin_activity)
    db.commit()
    db.refresh(new_user)
    
    return {
        "success": True,
        "message": f"Teammate {clean_id} created successfully.",
        "user": {
            "user_id": new_user.user_id,
            "role": new_user.role,
            "full_name": new_user.full_name,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at
        }
    }

@router.post("/users/{user_id}/status")
def toggle_user_status(
    user_id: str,
    req: UpdateStatusRequest,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """Activate or deactivate a team member account."""
    clean_id = user_id.strip().upper()
    user = db.query(User).filter(User.user_id == clean_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {clean_id} not found.")
    
    if clean_id == owner.user_id and not req.is_active:
        raise HTTPException(status_code=400, detail="Owner account cannot be deactivated.")
    
    user.is_active = req.is_active
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Deactivate active sessions if account is disabled
    if not req.is_active:
        db.query(UserSession).filter(UserSession.user_id == clean_id).update({"is_active": False})
        
    admin_act = UserActivity(
        id=f"ACT-{uuid.uuid4().hex[:12]}",
        user_id=owner.user_id,
        event_type="USER_STATUS_UPDATED",
        timestamp=now_str,
        module="ADMIN",
        details_json=json.dumps({"target_user_id": clean_id, "new_active_status": req.is_active}),
        status="SUCCESS"
    )
    db.add(admin_act)
    db.commit()
    
    status_label = "activated" if req.is_active else "deactivated"
    return {
        "success": True,
        "message": f"User {clean_id} has been {status_label}.",
        "user_id": clean_id,
        "is_active": user.is_active
    }

@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: str,
    req: ResetPasswordRequest,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """Reset a teammate's password as the administrator/owner."""
    clean_id = user_id.strip().upper()
    user = db.query(User).filter(User.user_id == clean_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {clean_id} not found.")
    
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")
    
    user.password_hash = get_password_hash(req.new_password)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Deactivate old sessions to require fresh login
    db.query(UserSession).filter(UserSession.user_id == clean_id).update({"is_active": False})
    
    admin_act = UserActivity(
        id=f"ACT-{uuid.uuid4().hex[:12]}",
        user_id=owner.user_id,
        event_type="USER_PASSWORD_RESET",
        timestamp=now_str,
        module="ADMIN",
        details_json=json.dumps({"target_user_id": clean_id}),
        status="SUCCESS"
    )
    db.add(admin_act)
    db.commit()
    
    return {
        "success": True,
        "message": f"Password for {clean_id} successfully reset."
    }

@router.get("/activity")
def get_activity_log(
    user_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """Retrieve deterministic activity records with zero password/secret leakage."""
    query = db.query(UserActivity)
    if user_id:
        query = query.filter(UserActivity.user_id == user_id.strip().upper())
    if event_type:
        query = query.filter(UserActivity.event_type == event_type.strip().upper())
    if module:
        query = query.filter(UserActivity.module == module.strip().upper())
        
    records = query.order_by(UserActivity.timestamp.desc()).limit(limit).all()
    
    events = []
    for r in records:
        events.append({
            "id": r.id,
            "user_id": r.user_id,
            "session_id": r.session_id,
            "event_type": r.event_type,
            "timestamp": r.timestamp,
            "module": r.module,
            "assessment_id": r.assessment_id,
            "finding_id": r.finding_id,
            "status": r.status,
            "details": json.loads(r.details_json) if r.details_json else {}
        })
        
    return {
        "success": True,
        "count": len(events),
        "activities": events
    }

@router.get("/activity/summary")
def get_activity_summary(
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Deterministic usage classification per teammate:
    - LOGIN ONLY: Authenticated, but no module or assessment actions.
    - ACTIVE USE: Explored modules or viewed pages.
    - MEANINGFUL USE: Started assessments, reviewed evidence, executed AI/RAG analysis, re-tests, or exported reports.
    """
    users = db.query(User).all()
    user_summaries = []
    
    meaningful_event_types = {
        "ASSESSMENT_STARTED", "ASSESSMENT_COMPLETED", "EVIDENCE_VIEWED",
        "AI_ANALYSIS_EXECUTED", "RISK_VIEWED", "REMEDIATION_VIEWED",
        "RETEST_EXECUTED", "REPORT_VIEWED", "REPORT_EXPORTED", "JSON_EXPORTED"
    }
    
    for u in users:
        activities = db.query(UserActivity).filter(UserActivity.user_id == u.user_id).all()
        event_types = {a.event_type for a in activities}
        
        has_meaningful = bool(event_types.intersection(meaningful_event_types))
        has_active = any(et in ("PAGE_VIEWED", "MODULE_OPENED", "WORLD_MONITOR_VIEWED", "DISCOVERY_VIEWED") for et in event_types)
        has_login = "LOGIN" in event_types
        
        if has_meaningful:
            usage_category = "MEANINGFUL USE"
        elif has_active:
            usage_category = "ACTIVE USE"
        elif has_login or u.last_login_at:
            usage_category = "LOGIN ONLY"
        else:
            usage_category = "NEVER LOGGED IN"
            
        user_summaries.append({
            "user_id": u.user_id,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "last_login_at": u.last_login_at,
            "usage_category": usage_category,
            "total_events": len(activities),
            "meaningful_actions_count": sum(1 for a in activities if a.event_type in meaningful_event_types)
        })
        
    return {
        "success": True,
        "total_users": len(users),
        "summary": user_summaries
    }

@router.get("/feedback")
def get_feedback_records(
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """Retrieve all submitted feedback for system owner review."""
    feedbacks = db.query(UserFeedback).order_by(UserFeedback.created_at.desc()).all()
    fb_list = []
    
    for fb in feedbacks:
        fb_list.append({
            "id": fb.id,
            "user_id": fb.user_id,
            "assessment_id": fb.assessment_id,
            "rating": fb.rating,
            "what_worked": fb.what_worked,
            "what_confusing": fb.what_confusing,
            "what_slow": fb.what_slow,
            "bug_description": fb.bug_description,
            "suggestions": fb.suggestions,
            "created_at": fb.created_at
        })
        
    return {
        "success": True,
        "count": len(fb_list),
        "feedbacks": fb_list
    }
