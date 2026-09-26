"""
KAVACH 5.0 — Forensic Export & Auditability API Routes (Priority 6)
Exposes endpoints for retrieving forensic reproducibility packages, HTML dossiers, and chained audit logs.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.core.database import get_db
from backend.app.services.forensic_export_service import forensic_export_service
from services.storage_service import storage

router = APIRouter(prefix="/forensic", tags=["Forensic & Auditability Package"])


class LogEventRequest(BaseModel):
    event_type: str
    action: str
    actor: Optional[str] = "Operator"
    assessment_id: Optional[str] = "GLOBAL"
    object_name: Optional[str] = "SYSTEM"
    result: Optional[str] = "SUCCESS"
    evidence_ref: Optional[str] = ""
    hash_val: Optional[str] = ""
    details: Optional[Dict[str, Any]] = None


@router.get("/export/{assessment_id}")
def get_forensic_package(
    assessment_id: str,
    actor: str = Query("Security Auditor", description="Reviewer/Evaluator identity"),
    db: Session = Depends(get_db)
):
    """
    Generates and returns the complete reproducible forensic package in JSON format.
    Includes SHA-256 hash manifest, 7 SIH categories, evidence, CVSS, and audit trail with credentials redacted.
    """
    try:
        return forensic_export_service.generate_forensic_package(
            assessment_id=assessment_id,
            db=db,
            actor=actor
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Failed to generate forensic package: {str(ex)}")


@router.get("/export/{assessment_id}/html", response_class=HTMLResponse)
def get_forensic_html_dossier(
    assessment_id: str,
    actor: str = Query("Security Auditor", description="Reviewer/Evaluator identity"),
    db: Session = Depends(get_db)
):
    """
    Generates a standalone, dark-mode, printable HTML forensic report.
    """
    try:
        pkg = forensic_export_service.generate_forensic_package(
            assessment_id=assessment_id,
            db=db,
            actor=actor
        )
        html_content = forensic_export_service.render_html_dossier(pkg)
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Failed to generate HTML dossier: {str(ex)}")


@router.get("/audit-trail/{assessment_id}")
def get_assessment_audit_trail(
    assessment_id: str,
    limit: int = Query(200, ge=1, le=1000)
):
    """
    Retrieves the cryptographically chained, tamper-evident audit log for an assessment.
    """
    events = storage.get_audit_events(assessment_id=assessment_id, limit=limit)
    return {
        "status": "SUCCESS",
        "assessment_id": assessment_id,
        "total_events": len(events),
        "events": events
    }


@router.post("/log-event")
def log_custom_audit_event(req: LogEventRequest):
    """
    Appends a new event into the immutable SHA-256 audit ledger.
    """
    event_id = storage.log_audit_event(
        event_type=req.event_type,
        action=req.action,
        actor=req.actor or "Operator",
        assessment_id=req.assessment_id,
        object_name=req.object_name,
        result=req.result or "SUCCESS",
        evidence_ref=req.evidence_ref,
        hash_val=req.hash_val,
        details=req.details
    )
    return {
        "status": "SUCCESS",
        "event_id": event_id,
        "message": f"Audit event {req.event_type} committed with SHA-256 chain integrity."
    }
