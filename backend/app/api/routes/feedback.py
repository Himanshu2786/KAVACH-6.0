"""
KAVACH 6.0 - User Feedback Submission API Routes
Enables teammates to submit constructive experience ratings, confusion points, and suggestions.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.auth import get_current_active_user
from backend.app.models.models import User, UserFeedback, UserActivity

router = APIRouter(prefix="/feedback", tags=["Feedback System"])

class SubmitFeedbackRequest(BaseModel):
    rating: int = Field(5, ge=1, le=5)
    assessment_id: Optional[str] = None
    what_worked: Optional[str] = ""
    what_confusing: Optional[str] = ""
    what_slow: Optional[str] = ""
    bug_description: Optional[str] = ""
    suggestions: Optional[str] = ""

@router.post("/submit")
def submit_feedback(
    req: SubmitFeedbackRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit teammate feedback linked to the authenticated user ID."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    fb = UserFeedback(
        id=f"FB-{uuid.uuid4().hex[:12]}",
        user_id=current_user.user_id,
        assessment_id=req.assessment_id,
        rating=req.rating,
        what_worked=req.what_worked or "",
        what_confusing=req.what_confusing or "",
        what_slow=req.what_slow or "",
        bug_description=req.bug_description or "",
        suggestions=req.suggestions or "",
        created_at=now_str
    )
    db.add(fb)
    
    # Record feedback submission activity
    act = UserActivity(
        id=f"ACT-{uuid.uuid4().hex[:12]}",
        user_id=current_user.user_id,
        event_type="FEEDBACK_SUBMITTED",
        timestamp=now_str,
        assessment_id=req.assessment_id,
        module="FEEDBACK",
        status="SUCCESS"
    )
    db.add(act)
    db.commit()
    
    return {
        "success": True,
        "message": "Thank you! Your feedback has been recorded.",
        "feedback_id": fb.id
    }
