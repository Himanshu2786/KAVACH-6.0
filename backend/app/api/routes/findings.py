import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.models import Finding, Assessment
from backend.app.schemas.schemas import FindingResponse, EvidenceResponse
from backend.app.services.ai_analysis_service import ai_analysis_service
from backend.app.services.knowledge_service import knowledge_service
from backend.app.services.cve_provenance_service import cve_provenance_service

router = APIRouter(prefix="/findings", tags=["Findings & AI Analysis"])

def _serialize_finding(f: Finding) -> dict:
    try:
        val_steps = json.loads(f.recommended_validation) if f.recommended_validation else []
    except Exception:
        val_steps = []

    try:
        rem_steps = json.loads(f.recommended_remediation) if f.recommended_remediation else []
    except Exception:
        rem_steps = []

    evd_sorted = sorted(f.evidence_records, key=lambda e: e.timestamp or "", reverse=True)
    evds = [
        EvidenceResponse(
            id=e.id,
            finding_id=e.finding_id,
            evidence_type=e.evidence_type,
            source=e.source,
            timestamp=e.timestamp,
            description=e.description,
            raw_data=e.raw_data,
            validation_result=e.validation_result,
            integrity_hash=e.integrity_hash,
            is_demo=e.is_demo,
            what_found=e.what_found,
            why_matters=e.why_matters,
            where_found=e.where_found,
            confidence_level=e.confidence_level,
            verification_command=e.verification_command,
            expected_output=e.expected_output,
            observed_output=e.observed_output,
            evidence_nature=e.evidence_nature,
            http_method=e.http_method,
            http_status=e.http_status,
            content_type=e.content_type,
            openapi_detected=e.openapi_detected,
            openapi_version=e.openapi_version,
            schema_title=e.schema_title,
            unauthenticated=e.unauthenticated,
            authorization_state=e.authorization_state,
        )
        for e in evd_sorted
    ]

    tax = knowledge_service.resolve_canonical_taxonomy(
        db=None,
        cwe_id=f.cwe_id,
        owasp_category=getattr(f, "canonical_owasp", None) or f.owasp_category or getattr(f, "owasp_id", None),
        category=f.category,
        title=f.title
    )

    cve_prov = cve_provenance_service.get_provenance_for_finding(f)
    p_score = f.priority_score if f.priority_score is not None else 5.0

    is_api_docs = (
        f.cwe_id == "CWE-200"
        or "WM-API-DOCS" in (f.id or "")
        or "api doc" in (f.title or "").lower()
        or "openapi" in (f.title or "").lower()
    )
    if is_api_docs:
        canonical = ai_analysis_service.get_canonical_api_docs_explanation()
        ai_summary = f.ai_summary or canonical["ai_summary"]
        ai_hypothesis = f.ai_hypothesis or canonical["ai_hypothesis"]
        ai_potential_impact = f.ai_potential_impact or canonical["possible_impact"]
        ai_reasoning_summary = f.ai_reasoning_summary or canonical["ai_reasoning_summary"]
        ai_confidence = f.ai_confidence or canonical["ai_confidence"]
        if not rem_steps:
            rem_steps = canonical["recommended_remediation"]
        if not val_steps:
            val_steps = canonical["recommended_validation"]
    else:
        ai_summary = f.ai_summary
        ai_hypothesis = f.ai_hypothesis
        ai_potential_impact = f.ai_potential_impact
        ai_reasoning_summary = f.ai_reasoning_summary
        ai_confidence = f.ai_confidence

    return {
        "id": f.id,
        "assessment_id": f.assessment_id,
        "title": f.title,
        "description": f.description,
        "category": f.category,
        "affected_component": f.affected_component,
        "base_severity": f.base_severity or getattr(f, "severity", None) or "MEDIUM",
        "priority": f.priority or f.base_severity or "MEDIUM",
        "priority_score": p_score,
        "priority_scale": "10.0",
        "priority_score_formatted": f"{p_score:.2f} / 10.0",
        "priority_explanation": f.priority_explanation,
        "status": f.status,
        "evidence_status": f.evidence_status or ("VERIFIED" if f.status == "CONFIRMED" else ("AVAILABLE" if f.evidence_records else "NONE")),
        "ai_analysis_status": f.ai_analysis_status or ("COMPLETED" if is_api_docs else "PENDING"),
        "ai_summary": ai_summary,
        "ai_hypothesis": ai_hypothesis,
        "ai_confidence": ai_confidence,
        "ai_reasoning_summary": ai_reasoning_summary,
        "ai_potential_impact": ai_potential_impact,
        "recommended_validation": val_steps,
        "recommended_remediation": rem_steps,
        "cwe_id": tax["cwe_id"],
        "owasp_category": tax["owasp_category"],
        "cve_id": cve_prov["cve_id"],
        "cve_status": cve_prov["cve_status"],
        "nvd_cvss": cve_prov["nvd_cvss"],
        "nvd_cvss_display": cve_prov["nvd_cvss_display"],
        "nvd_reference": cve_prov["nvd_reference"],
        "created_at": f.created_at or "",
        "updated_at": f.updated_at or "",
        "evidence_records": evds,
        "ai_provider": "ollama" if f.ai_analysis_status == "COMPLETED" else "fallback"
    }

@router.get("", response_model=List[FindingResponse])
def list_findings(
    assessment_id: Optional[str] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    is_demo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Finding)

    if assessment_id:
        # Rule 1: Exact assessment_id match. Never fall back.
        query = query.filter(Finding.assessment_id == assessment_id)
    else:
        # Rule 2: No assessment_id provided
        if is_demo is True:
            # Explicit demo mode
            demo_asm_ids = [a.id for a in db.query(Assessment.id).filter(Assessment.is_demo == True).all()]
            query = query.filter(Finding.assessment_id.in_(demo_asm_ids))
        elif is_demo is False:
            # Explicit real mode: return findings for active real assessment only
            active_real = (
                db.query(Assessment)
                .filter(Assessment.is_demo == False)
                .order_by(Assessment.started_at.desc(), Assessment.id.desc())
                .first()
            )
            if active_real:
                query = query.filter(Finding.assessment_id == active_real.id)
            else:
                return []
        else:
            # Real user mode (default when is_demo is not explicitly True):
            # Scope strictly to active real assessment. If no active real assessment exists, return []
            active_real = (
                db.query(Assessment)
                .filter(Assessment.is_demo == False)
                .order_by(Assessment.started_at.desc(), Assessment.id.desc())
                .first()
            )
            if active_real:
                query = query.filter(Finding.assessment_id == active_real.id)
            else:
                return []

    if category:
        query = query.filter(Finding.category == category)
    if severity:
        query = query.filter(Finding.base_severity == severity)
    if status:
        query = query.filter(Finding.status == status)

    findings = query.all()
    return [_serialize_finding(f) for f in findings]

@router.get("/{finding_id}", response_model=FindingResponse)
def get_finding(finding_id: str, db: Session = Depends(get_db)):
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return _serialize_finding(finding)

@router.post("/{finding_id}/analyze")
async def analyze_finding(finding_id: str, db: Session = Depends(get_db)):
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    result = await ai_analysis_service.analyze_finding(db, finding)
    return {
        "success": True,
        "ai_provider": result.get("ai_provider", "fallback"),
        "data": result,
        "updated_finding": _serialize_finding(finding)
    }
