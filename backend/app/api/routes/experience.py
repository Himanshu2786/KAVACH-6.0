"""
KAVACH 5.0 - Experience DB API Routes ("REMEMBER")
Aggregates historical assessment memory, confirmed findings, false positive lessons, and re-verification diffs.
"""

import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.models import Assessment, Finding, ReVerificationRecord, EvidenceRecord, AuditEvent
from backend.app.core.time import ist_formatted

router = APIRouter(prefix="/experience", tags=["Experience DB"])

class MarkFalsePositiveRequest(BaseModel):
    finding_id: str
    rationale: str

@router.get("/summary")
def get_experience_summary(db: Session = Depends(get_db)):
    """Aggregate historical memory of security assessments and defect resolutions."""
    total_assessments = db.query(Assessment).count()
    all_findings = db.query(Finding).all()
    re_verifications = db.query(ReVerificationRecord).all()

    confirmed_count = sum(1 for f in all_findings if f.status == "CONFIRMED")
    resolved_count = sum(1 for r in re_verifications if r.new_status == "RESOLVED")
    false_positive_count = sum(1 for f in all_findings if getattr(f, "triage_status", "") == "FALSE_POSITIVE" or f.status == "UNCONFIRMED")
    under_analysis_count = sum(1 for f in all_findings if f.status in ("POTENTIAL", "UNDER ANALYSIS", "VALIDATING"))

    return {
        "success": True,
        "metrics": {
            "total_assessments": total_assessments,
            "total_findings_cataloged": len(all_findings),
            "confirmed_flaws": confirmed_count,
            "resolved_re_verifications": resolved_count,
            "false_positives_prevented": false_positive_count,
            "under_analysis": under_analysis_count
        },
        "principle": "FIND -> OBSERVE -> PROVE -> ANALYZE -> UNDERSTAND -> ASSIGN -> FIX -> RE-VERIFY -> REMEMBER"
    }

@router.get("/re-verifications")
def get_reverification_history(db: Session = Depends(get_db)):
    """Return all differential re-verifications proving patch effectiveness."""
    records = db.query(ReVerificationRecord).order_by(ReVerificationRecord.timestamp.desc()).all()
    result = []
    for r in records:
        finding = db.query(Finding).filter(Finding.id == r.finding_id).first()
        result.append({
            "id": r.id,
            "finding_id": r.finding_id,
            "finding_title": finding.title if finding else "Unknown Finding",
            "category": finding.category if finding else "Unknown",
            "previous_status": r.previous_status,
            "new_status": r.new_status,
            "command_executed": r.command_executed,
            "output_before": r.output_before,
            "output_after": r.output_after,
            "summary": r.summary,
            "timestamp": r.timestamp
        })
    return {
        "success": True,
        "count": len(result),
        "re_verifications": result
    }

@router.get("/false-positives")
def get_false_positives_library(db: Session = Depends(get_db)):
    """Catalog of hypotheses proven false or marked non-applicable, preventing repeated misdiagnoses."""
    fps = db.query(Finding).filter(
        (Finding.triage_status == "FALSE_POSITIVE") | (Finding.status == "UNCONFIRMED")
    ).all()

    items = []
    for f in fps:
        items.append({
            "finding_id": f.id,
            "title": f.title,
            "category": f.category,
            "component": f.affected_component,
            "status": f.status,
            "triage_status": f.triage_status,
            "team_notes": f.team_notes,
            "why_disproved": f.team_notes or "Technical probe observed correct baseline security controls or authentication boundary enforcement."
        })
    return {
        "success": True,
        "count": len(items),
        "false_positives": items
    }

@router.post("/mark-false-positive")
def mark_false_positive(req: MarkFalsePositiveRequest, db: Session = Depends(get_db)):
    """Mark a finding as false positive and commit technical lesson to Experience DB."""
    finding = db.query(Finding).filter(Finding.id == req.finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail=f"Finding {req.finding_id} not found")

    finding.triage_status = "FALSE_POSITIVE"
    finding.status = "UNCONFIRMED"
    timestamp = ist_formatted("%Y-%m-%d %H:%M:%S IST")
    note = f"[{timestamp} - FALSE POSITIVE AUDIT]: {req.rationale}"
    existing = finding.team_notes or ""
    finding.team_notes = f"{note}\n{existing}".strip()

    # Log to Audit Trail
    audit_entry = AuditEvent(
        assessment_id=finding.assessment_id,
        finding_id=finding.id,
        module="EXPERIENCE_DB",
        event_type="FALSE_POSITIVE_RECORDED",
        status="SUCCESS",
        description=f"Finding {finding.id} marked as FALSE_POSITIVE. Stored in Experience DB: {req.rationale}",
        timestamp=ist_formatted("%Y-%m-%d %H:%M:%S IST"),
        metadata_json=json.dumps({"rationale": req.rationale, "finding_id": finding.id})
    )
    db.add(audit_entry)
    db.commit()

    return {
        "success": True,
        "message": f"Finding {finding.id} committed to False Positive Knowledge Bank.",
        "finding_id": finding.id
    }
