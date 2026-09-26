from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.schemas.schemas import (
    EvidenceCreate,
    EvidenceResponse,
    TerminalVerificationResponse,
    ReVerificationRequest,
    ReVerificationResponse
)
from backend.app.services.evidence_service import evidence_service
from backend.app.services.validation_service import validation_service
from backend.app.models.models import EvidenceRecord, Finding, Assessment

router = APIRouter(prefix="/evidence", tags=["Evidence & Validation Engine"])

@router.get("", response_model=List[EvidenceResponse])
def list_evidence(
    finding_id: Optional[str] = None,
    assessment_id: Optional[str] = None,
    is_demo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    if finding_id and assessment_id:
        # Cross-validation: finding must belong to the given assessment
        f = db.query(Finding).filter(Finding.id == finding_id, Finding.assessment_id == assessment_id).first()
        if not f:
            return []
        q = db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == finding_id)
        if is_demo is not None:
            q = q.filter(EvidenceRecord.is_demo == is_demo)
        return q.order_by(EvidenceRecord.timestamp.desc()).all()

    if finding_id:
        q = db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == finding_id)
        if is_demo is not None:
            q = q.filter(EvidenceRecord.is_demo == is_demo)
        return q.order_by(EvidenceRecord.timestamp.desc()).all()

    if assessment_id:
        findings = db.query(Finding.id).filter(Finding.assessment_id == assessment_id).all()
        finding_ids = [f[0] for f in findings]
        if not finding_ids:
            return []
        q = db.query(EvidenceRecord).filter(EvidenceRecord.finding_id.in_(finding_ids))
        if is_demo is not None:
            q = q.filter(EvidenceRecord.is_demo == is_demo)
        return q.order_by(EvidenceRecord.timestamp.desc()).all()

    if is_demo is True:
        return db.query(EvidenceRecord).filter(EvidenceRecord.is_demo == True).order_by(EvidenceRecord.timestamp.desc()).all()

    # Real user mode (default when is_demo is not explicitly True):
    return db.query(EvidenceRecord).filter(EvidenceRecord.is_demo == False).order_by(EvidenceRecord.timestamp.desc()).all()

@router.post("", response_model=EvidenceResponse)
def record_evidence(data: EvidenceCreate, db: Session = Depends(get_db)):
    evd = evidence_service.create_evidence(
        db=db,
        finding_id=data.finding_id,
        evidence_type=data.evidence_type,
        description=data.description,
        raw_data=data.raw_data,
        validation_result=data.validation_result,
        source=data.source,
        is_demo=data.is_demo,
        what_found=data.what_found or "",
        why_matters=data.why_matters or "",
        where_found=data.where_found or "",
        confidence_level=data.confidence_level or "HIGH",
        verification_command=data.verification_command or "",
        expected_output=data.expected_output or "",
        observed_output=data.observed_output or "",
        evidence_nature=data.evidence_nature or "REAL EVIDENCE"
    )
    # Re-evaluate finding status deterministically based on evidence
    validation_service.evaluate_finding_status(db, data.finding_id)
    return evd

@router.post("/probe", response_model=EvidenceResponse)
async def execute_validation_probe(
    finding_id: str = Body(..., embed=True),
    probe_type: str = Body("HTTP_PROBE", embed=True),
    is_demo: bool = Body(True, embed=True),
    db: Session = Depends(get_db)
):
    try:
        evd = await validation_service.execute_safe_probe(
            db=db,
            finding_id=finding_id,
            probe_type=probe_type,
            is_demo=is_demo
        )
        return evd
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))

@router.get("/{finding_id}/terminal", response_model=TerminalVerificationResponse)
def get_terminal_verification(finding_id: str, db: Session = Depends(get_db)):
    try:
        return validation_service.get_terminal_verification(db, finding_id)
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))

@router.post("/{finding_id}/re-verify", response_model=ReVerificationResponse)
def re_verify_finding(
    finding_id: str,
    payload: Optional[ReVerificationRequest] = None,
    db: Session = Depends(get_db)
):
    try:
        cmd = payload.command_executed if payload else ""
        out = payload.output_after if payload else ""
        status = payload.force_status if payload else None
        return validation_service.re_verify_finding(
            db=db,
            finding_id=finding_id,
            command_executed=cmd,
            output_after=out,
            force_status=status
        )
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
