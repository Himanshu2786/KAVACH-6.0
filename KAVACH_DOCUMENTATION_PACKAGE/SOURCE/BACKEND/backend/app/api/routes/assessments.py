import json
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from backend.app.core.database import get_db
from backend.app.schemas.schemas import AssessmentCreate, AssessmentResponse
from backend.app.services.assessment_service import assessment_service
from urllib.parse import urlparse
from backend.app.models.models import Assessment, Finding, EvidenceRecord
from backend.app.core.security import get_current_user_optional

def normalize_target_url(target_url: Optional[str]) -> str:
    if not target_url:
        return ""
    url = target_url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        path = parsed.path.rstrip("/")
        return f"{parsed.scheme.lower()}://{hostname}{path}"
    except Exception:
        return target_url.strip().lower()

def is_world_monitor_target(target_url: Optional[str]) -> bool:
    if not target_url:
        return False
    url = target_url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        return hostname in ("worldmonitor.app", "www.worldmonitor.app")
    except Exception:
        return False

router = APIRouter(prefix="/assessments", tags=["Assessments"])

def _enrich_assessment(asm: Assessment, db: Session) -> Dict[str, Any]:
    findings = db.query(Finding).filter(Finding.assessment_id == asm.id).all()
    total_findings = len(findings)
    confirmed_findings = sum(
        1 for f in findings
        if f.status in ("CONFIRMED", "STILL_OPEN", "VERIFIED")
        and getattr(f, "evidence_status", "") != "REQUIRES_SOURCE_VALIDATION"
    )
    try:
        modules = json.loads(asm.modules_enabled)
    except Exception:
        modules = []

    return {
        "id": asm.id,
        "name": asm.name,
        "target_url": asm.target_url,
        "description": asm.description,
        "environment": asm.environment,
        "scope": asm.scope,
        "authorization_confirmed": asm.authorization_confirmed,
        "modules_enabled": modules,
        "status": asm.status,
        "progress": asm.progress,
        "current_stage": asm.current_stage,
        "started_at": asm.started_at,
        "completed_at": asm.completed_at,
        "is_demo": asm.is_demo,
        "assessment_type": getattr(asm, "assessment_type", "GENERIC_ASSESSMENT") or "GENERIC_ASSESSMENT",
        "parent_assessment_id": getattr(asm, "parent_assessment_id", None),
        "owner_id": getattr(asm, "owner_id", None),
        "total_findings": total_findings,
        "confirmed_findings": confirmed_findings
    }

@router.post("", response_model=AssessmentResponse)
async def create_assessment(
    data: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    try:
        user_id = getattr(current_user, "id", None)
        # If target is World Monitor and not demo mode, route execution through dedicated empirical World Monitor engine
        if is_world_monitor_target(data.target_url) and not data.is_demo:
            from backend.app.services.world_monitor_assessment_engine import world_monitor_assessment_engine
            wm_res = await world_monitor_assessment_engine.run_assessment(
                target_url=data.target_url,
                mode="HYBRID",
                assessment_name=data.name or "World Monitor Security Assessment",
                db=db
            )
            wm_asm = assessment_service.get_by_id(db, wm_res["assessment_id"])
            if wm_asm:
                if user_id and not wm_asm.owner_id:
                    wm_asm.owner_id = user_id
                    db.commit()
                return _enrich_assessment(wm_asm, db)

        asm = assessment_service.create_assessment(db, data, owner_id=user_id)
        return _enrich_assessment(asm, db)
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.get("", response_model=List[AssessmentResponse])
def list_assessments(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    assessments = assessment_service.get_all(db, current_user=current_user)
    return [_enrich_assessment(a, db) for a in assessments]

@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    asm = assessment_service.get_by_id(db, assessment_id)
    if not asm:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if current_user and getattr(current_user, "role", "") not in ("admin", "DEVELOPER_OWNER", "ADMIN"):
        u_ids = {getattr(current_user, "id", None), getattr(current_user, "user_id", None), getattr(current_user, "username", None)} - {None, ""}
        if asm.owner_id and asm.owner_id not in u_ids and not asm.is_demo:
            raise HTTPException(status_code=403, detail="Access denied: You do not own this assessment")

    return _enrich_assessment(asm, db)

@router.post("/{assessment_id}/advance-stage", response_model=AssessmentResponse)
def advance_stage(assessment_id: str, stage: str = Body(..., embed=True), db: Session = Depends(get_db)):
    try:
        asm = assessment_service.advance_stage(db, assessment_id, stage)
        return _enrich_assessment(asm, db)
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.get("/{assessment_id}/posture")
def get_security_posture(assessment_id: str, db: Session = Depends(get_db)):
    asm = assessment_service.get_by_id(db, assessment_id)
    if not asm:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment_service.calculate_security_posture(db, assessment_id)


# ─────────────────────────────────────────────────────────────────────────────
# REAL WORLD MONITOR SECURITY ASSESSMENT (SIH PS 26163)
# ─────────────────────────────────────────────────────────────────────────────
from pydantic import BaseModel, Field

class WorldMonitorAssessmentRequest(BaseModel):
    target_url: Optional[str] = Field(default="https://www.worldmonitor.app", description="Authorized Target URL")
    source_path: Optional[str] = Field(default=None, description="Authorized Source Code Path")
    mode: str = Field(default="HYBRID", description="Assessment Mode: RUNTIME, SOURCE, HYBRID")
    assessment_name: str = Field(default="World Monitor Security Assessment")

@router.post("/world-monitor")
async def run_world_monitor_assessment(
    req: WorldMonitorAssessmentRequest,
    db: Session = Depends(get_db)
):
    """
    Executes a real empirical security assessment on the authorized World Monitor target.
    Zero synthetic or fabricated findings.
    """
    from backend.app.services.world_monitor_assessment_engine import world_monitor_assessment_engine
    result = await world_monitor_assessment_engine.run_assessment(
        target_url=req.target_url,
        source_path=req.source_path,
        mode=req.mode,
        assessment_name=req.assessment_name,
        db=db
    )
    return result

@router.get("/world-monitor/latest")
def get_latest_world_monitor_assessment(db: Session = Depends(get_db)):
    """
    Returns the latest real empirical World Monitor assessment and its associated evidence records.
    Filters specifically for dedicated empirical World Monitor assessments.
    Generic assessments (even if newer) and demo assessments are never selected.
    """
    candidates = (
        db.query(Assessment)
        .filter(
            Assessment.is_demo == False,
            Assessment.assessment_type == "WORLD_MONITOR_EMPIRICAL"
        )
        .order_by(Assessment.started_at.desc(), Assessment.completed_at.desc(), Assessment.id.desc())
        .all()
    )
    if not candidates:
        candidates = (
            db.query(Assessment)
            .filter(
                Assessment.is_demo == False,
                Assessment.id.like("KAVACH-WM-%")
            )
            .order_by(Assessment.started_at.desc(), Assessment.completed_at.desc(), Assessment.id.desc())
            .all()
        )
    # Prefer assessment targeting the real World Monitor target
    wm_target_candidates = [a for a in candidates if is_world_monitor_target(a.target_url)]
    candidates_with_findings = [a for a in wm_target_candidates if len(a.findings) > 0]
    if candidates_with_findings:
        asm = candidates_with_findings[0]
    elif wm_target_candidates:
        asm = wm_target_candidates[0]
    else:
        asm = candidates[0] if candidates else None

    if not asm:
        return {"status": "NO_ASSESSMENT_RUN", "message": "No real World Monitor assessment executed yet."}
    
    findings = db.query(Finding).filter(Finding.assessment_id == asm.id).all()
    if findings:
        evidence = db.query(EvidenceRecord).filter(EvidenceRecord.finding_id.in_([f.id for f in findings])).all()
    else:
        evidence = []
    
    return {
        "id": asm.id,
        "assessment_id": asm.id,
        "name": asm.name,
        "target_url": asm.target_url,
        "scope": asm.scope,
        "status": asm.status,
        "summary": asm.description,
        "started_at": asm.started_at,
        "completed_at": asm.completed_at,
        "total_findings": len(findings),
        "confirmed_findings": sum(
            1 for f in findings
            if f.status in ("CONFIRMED", "STILL_OPEN", "VERIFIED")
            and getattr(f, "evidence_status", "") != "REQUIRES_SOURCE_VALIDATION"
        ),
        "findings": [
            {
                "id": f.id,
                "title": f.title,
                "category": f.category,
                "severity": f.base_severity,
                "priority_score": f.priority_score,
                "cwe_id": f.cwe_id,
                "owasp_category": f.owasp_category,
                "affected_component": f.affected_component,
                "description": f.description,
                "status": f.status,
                "created_at": f.created_at
            }
            for f in findings
        ],
        "evidence": [
            {
                "id": ev.id,
                "finding_id": ev.finding_id,
                "test_name": ev.evidence_type,
                "provenance": ev.source,
                "target": ev.where_found,
                "raw_observation": ev.what_found,
                "verification_command": ev.verification_command,
                "expected_output": ev.expected_output,
                "observed_output": ev.observed_output,
                "validation_result": ev.validation_result,
                "hash": ev.integrity_hash,
                "timestamp": ev.timestamp
            }
            for ev in evidence
        ]
    }

