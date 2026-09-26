"""
KAVACH 5.0 - Team Desk API Routes ("ASSIGN")
Handles security operations team collaboration, finding assignment, triage status tracking, and audit logging.
"""

import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.models import Finding, AuditEvent
from backend.app.core.time import ist_formatted

router = APIRouter(prefix="/team", tags=["Team Desk"])

TEAM_ROLES = [
    {"id": "secops_lead", "name": "Lead SecOps Engineer", "role": "Triage & Escalation", "initials": "SO"},
    {"id": "appsec_engineer", "name": "AppSec Specialist", "role": "Verification & Probing", "initials": "AS"},
    {"id": "dev_lead", "name": "Backend Development Lead", "role": "Code Remediation & Patching", "initials": "DL"},
    {"id": "compliance_officer", "name": "Compliance & Audit Officer", "role": "ISO/OWASP Verification", "initials": "CO"},
    {"id": "incident_responder", "name": "SOC Incident Responder", "role": "Active Monitoring", "initials": "IR"}
]

class AssignFindingRequest(BaseModel):
    finding_id: str
    assigned_to: str
    triage_status: Optional[str] = "ASSIGNED"
    notes: Optional[str] = None

class TeamNotesRequest(BaseModel):
    finding_id: str
    notes: str

@router.get("/members")
def get_team_members():
    """List available security operations team roles and personnel."""
    return {
        "success": True,
        "team_members": TEAM_ROLES
    }

@router.get("/assignments")
def get_team_assignments(db: Session = Depends(get_db)):
    """Retrieve all findings organized with their current assignment and triage state."""
    findings = db.query(Finding).all()
    assignments = []

    for f in findings:
        assignments.append({
            "finding_id": f.id,
            "assessment_id": f.assessment_id,
            "title": f.title,
            "category": f.category,
            "severity": f.base_severity,
            "status": f.status,
            "evidence_status": f.evidence_status,
            "assigned_to": getattr(f, "assigned_to", "Unassigned") or "Unassigned",
            "triage_status": getattr(f, "triage_status", "NEW") or "NEW",
            "team_notes": getattr(f, "team_notes", "") or "",
            "cwe_id": f.cwe_id,
            "owasp_category": f.owasp_category,
            "updated_at": f.updated_at or f.created_at
        })

    return {
        "success": True,
        "count": len(assignments),
        "assignments": assignments
    }

@router.post("/assign")
def assign_finding(req: AssignFindingRequest, db: Session = Depends(get_db)):
    """Assign a security defect to a team member and record the triage transition in Audit Trail."""
    finding = db.query(Finding).filter(Finding.id == req.finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail=f"Finding {req.finding_id} not found")

    finding.assigned_to = req.assigned_to
    if req.triage_status:
        finding.triage_status = req.triage_status
    if req.notes:
        existing_notes = finding.team_notes or ""
        timestamp = ist_formatted("%Y-%m-%d %H:%M:%S IST")
        finding.team_notes = f"[{timestamp} - {req.assigned_to}]: {req.notes}\n{existing_notes}".strip()

    # Log to Audit Trail
    audit_entry = AuditEvent(
        assessment_id=finding.assessment_id,
        finding_id=finding.id,
        module="TEAM_DESK",
        event_type="FINDING_ASSIGNED",
        status="SUCCESS",
        description=f"Finding '{finding.title}' assigned to {req.assigned_to} (Triage: {finding.triage_status}).",
        timestamp=ist_formatted("%Y-%m-%d %H:%M:%S IST"),
        metadata_json=json.dumps({
            "assigned_to": req.assigned_to,
            "triage_status": finding.triage_status,
            "finding_id": finding.id
        })
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(finding)

    return {
        "success": True,
        "message": f"Finding {finding.id} successfully assigned to {req.assigned_to}.",
        "finding": {
            "id": finding.id,
            "assigned_to": finding.assigned_to,
            "triage_status": finding.triage_status,
            "team_notes": finding.team_notes
        }
    }

@router.post("/notes")
def add_team_note(req: TeamNotesRequest, db: Session = Depends(get_db)):
    """Add a collaborative team audit note to a finding."""
    finding = db.query(Finding).filter(Finding.id == req.finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail=f"Finding {req.finding_id} not found")

    timestamp = ist_formatted("%Y-%m-%d %H:%M:%S IST")
    author = finding.assigned_to or "SecOps Analyst"
    formatted_note = f"[{timestamp} - {author}]: {req.notes}"
    existing = finding.team_notes or ""
    finding.team_notes = f"{formatted_note}\n{existing}".strip()

    # Log to Audit Trail
    audit_entry = AuditEvent(
        assessment_id=finding.assessment_id,
        finding_id=finding.id,
        module="TEAM_DESK",
        event_type="TEAM_NOTE_ADDED",
        status="SUCCESS",
        description=f"Collaboration note appended to finding {finding.id}.",
        timestamp=ist_formatted("%Y-%m-%d %H:%M:%S IST"),
        metadata_json=json.dumps({"author": author, "finding_id": finding.id})
    )
    db.add(audit_entry)
    db.commit()

    return {
        "success": True,
        "finding_id": finding.id,
        "team_notes": finding.team_notes
    }
