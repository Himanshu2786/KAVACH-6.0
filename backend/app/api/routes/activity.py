"""
KAVACH 6.0 - User Activity Recording API Routes
Allows clients to record privacy-conscious, deterministic user interaction events.
Ensures zero password, token, or secret persistence.
"""

import uuid
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.auth import get_current_active_user
from backend.app.core.security import sanitize_log_dict
from backend.app.models.models import User, UserActivity

router = APIRouter(prefix="/activity", tags=["Activity Tracking"])

class LogActivityRequest(BaseModel):
    event_type: str
    module: Optional[str] = "CORE"
    assessment_id: Optional[str] = None
    finding_id: Optional[str] = None
    evidence_id: Optional[str] = None
    status: Optional[str] = "SUCCESS"
    details: Optional[Dict[str, Any]] = None

@router.post("/log")
def log_user_activity(
    req: LogActivityRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record a deterministic activity event for the current authenticated user."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Strictly sanitize payload to eliminate passwords, tokens, and credentials
    cleaned_details = sanitize_log_dict(req.details or {})
    
    activity = UserActivity(
        id=f"ACT-{uuid.uuid4().hex[:12]}",
        user_id=current_user.user_id,
        event_type=req.event_type.strip().upper(),
        timestamp=now_str,
        assessment_id=req.assessment_id,
        finding_id=req.finding_id,
        evidence_id=req.evidence_id,
        module=req.module.strip().upper() if req.module else "CORE",
        details_json=json.dumps(cleaned_details),
        status=req.status.strip().upper() if req.status else "SUCCESS"
    )
    db.add(activity)
    db.commit()
    
    return {
        "success": True,
        "activity_id": activity.id,
        "event_type": activity.event_type
    }
