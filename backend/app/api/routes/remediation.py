from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.remediation_service import remediation_service
from backend.app.services.world_monitor_assessment_engine import world_monitor_assessment_engine
from services.storage_service import storage

router = APIRouter(prefix="/remediation", tags=["Remediation Engine"])


class VerificationRequest(BaseModel):
    finding_id: str
    assessment_id: Optional[str] = "ASM-LATEST"
    target: Optional[str] = None


class StatusTransitionRequest(BaseModel):
    finding_id: str
    new_status: str
    reason: Optional[str] = "Operator status update"
    actor: Optional[str] = "Security Lead"


@router.get("/{finding_id}")
def get_remediation_details(finding_id: str, db: Session = Depends(get_db)):
    try:
        return remediation_service.get_remediation_plan(db, finding_id)
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))


@router.post("/verify")
def verify_finding_remediation(req: VerificationRequest, db: Session = Depends(get_db)):
    """
    Executes empirical re-verification test:
    BEFORE → VULNERABILITY OBSERVED → REMEDIATION → AFTER → RE-RUN TEST → COMPARE → VERIFIED / NOT VERIFIED
    Records verification evidence and updates finding lifecycle status.
    """
    try:
        res = world_monitor_assessment_engine.verify_remediation(
            finding_id=req.finding_id,
            assessment_id=req.assessment_id or "ASM-LATEST",
            target=req.target,
            db=db
        )
        return {
            "status": "SUCCESS",
            "message": f"Verification completed. Verdict: {res['comparison_verdict']}",
            "data": res
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(ex)}")


@router.post("/status")
def transition_finding_status(req: StatusTransitionRequest):
    """
    Transitions finding status across:
    OPEN, REMEDIATION_RECOMMENDED, RETEST_REQUIRED, VERIFIED, NOT_VERIFIED.
    Appends an immutable audit event.
    """
    success = storage.update_finding_status(
        finding_id=req.finding_id,
        new_status=req.new_status,
        reason=req.reason or "Manual status transition",
        actor=req.actor or "Operator"
    )
    if not success:
        raise HTTPException(status_code=404, detail=f"Finding {req.finding_id} not found")
    
    return {
        "status": "SUCCESS",
        "finding_id": req.finding_id,
        "new_status": req.new_status,
        "message": f"Finding status transitioned to {req.new_status} with audit trail recorded."
    }

