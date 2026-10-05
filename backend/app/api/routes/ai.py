"""
KAVACH Local AI Explanation Engine API Routes
Exposes the 6 AI Explanation Functions and the 4-State AI Lifecycle:
  - 🟢 AI READY
  - 🟡 AI STARTING
  - 🟠 MODEL UNAVAILABLE
  - 🔴 AI OFFLINE
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.models import Finding, Assessment
from backend.app.services.ollama_service import ollama_service
from backend.app.services.ai_analysis_service import ai_analysis_service

router = APIRouter(prefix="/ai", tags=["Local AI Explanation Engine"])

class FindingExplanationRequest(BaseModel):
    finding_id: str

class ThreatAlertRequest(BaseModel):
    alert_text: str
    component: Optional[str] = "Application Gateway"
    severity: Optional[str] = "HIGH"

class AssessmentSummaryRequest(BaseModel):
    assessment_id: str

class AuditSummaryRequest(BaseModel):
    assessment_id: Optional[str] = None

@router.get("/status")
async def get_ai_status():
    """
    Returns real-time 4-state lifecycle status:
      - 🟢 AI READY
      - 🟡 AI STARTING
      - 🟠 MODEL UNAVAILABLE
      - 🔴 AI OFFLINE
    """
    health = await ollama_service.check_health()
    return {
        "success": True,
        "lifecycle_state": health["lifecycle_state"],
        "status_code": health["status_code"],
        "status_dot": health["status_dot"],
        "endpoint": health["base_url"],
        "selected_model": health["selected_model"],
        "available_models": health["available_models"],
        "has_configured_model": health["has_configured_model"],
        "response_time_ms": health["response_time_ms"],
        "ollama_binary": health["ollama_binary"],
        "message": health["message"]
    }

@router.post("/start")
def start_local_ai_service():
    """Attempts transparent local background startup of the Ollama service."""
    result = ollama_service.attempt_auto_start()
    return result

@router.post("/explain-finding")
async def explain_finding(req: FindingExplanationRequest, db: Session = Depends(get_db)):
    """AI Function 1: Standardized 7-section structured finding explanation."""
    finding = db.query(Finding).filter(Finding.id == req.finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail=f"Finding {req.finding_id} not found")

    evidence = finding.evidence_records[0] if finding.evidence_records else None
    explanation = await ai_analysis_service.explain_finding(finding, evidence)
    return {
        "success": True,
        "finding_id": finding.id,
        "ai_provider": explanation.get("ai_provider", "fallback"),
        "explanation": explanation
    }

@router.post("/explain-risk")
async def explain_risk(req: FindingExplanationRequest, db: Session = Depends(get_db)):
    """AI Function 2: Risk explanation (possible impact, affected component, reason for severity)."""
    finding = db.query(Finding).filter(Finding.id == req.finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail=f"Finding {req.finding_id} not found")

    risk_data = await ai_analysis_service.explain_risk(finding)
    return {
        "success": True,
        "ai_provider": risk_data.get("ai_provider", "fallback"),
        "risk_explanation": risk_data
    }

@router.post("/remediation-guide")
async def get_remediation_guide(req: FindingExplanationRequest, db: Session = Depends(get_db)):
    """AI Function 3: Step-by-step remediation, safe recommendations, how to verify."""
    finding = db.query(Finding).filter(Finding.id == req.finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail=f"Finding {req.finding_id} not found")

    guide = await ai_analysis_service.remediation_guide(finding)
    return {
        "success": True,
        "ai_provider": guide.get("ai_provider", "fallback"),
        "remediation_guide": guide
    }

@router.post("/assessment-summary")
async def get_assessment_summary(req: AssessmentSummaryRequest, db: Session = Depends(get_db)):
    """AI Function 4: Checks completed, findings, risk distribution, priority actions."""
    assessment = db.query(Assessment).filter(Assessment.id == req.assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail=f"Assessment {req.assessment_id} not found")

    findings = db.query(Finding).filter(Finding.assessment_id == req.assessment_id).all()
    summary = await ai_analysis_service.assessment_summary(assessment, findings)
    return {
        "success": True,
        "assessment_id": assessment.id,
        "ai_provider": summary.get("ai_provider", "fallback"),
        "summary": summary
    }

@router.post("/audit-summary")
async def get_audit_summary(req: AuditSummaryRequest, db: Session = Depends(get_db)):
    """AI Function 5: Assessment history, actions taken, re-verification results."""
    summary = await ai_analysis_service.audit_summary(db, req.assessment_id)
    return {
        "success": True,
        "ai_provider": summary.get("ai_provider", "fallback"),
        "audit_summary": summary
    }

@router.post("/threat-alert")
async def explain_threat_alert(req: ThreatAlertRequest):
    """AI Function 6: Plain-language translation of raw security alert indicators."""
    explanation = await ai_analysis_service.threat_alert_explanation(
        alert_text=req.alert_text,
        component=req.component or "Application Gateway",
        severity=req.severity or "HIGH"
    )
    return {
        "success": True,
        "ai_provider": explanation.get("ai_provider", "fallback"),
        "alert_explanation": explanation
    }

@router.post("/explain-5-points")
async def explain_5_points(req: FindingExplanationRequest, db: Session = Depends(get_db)):
    """
    Priority 7: Evidence Analyst 5-Point Explanation.
    Generates:
      1. simple explanation
      2. technical explanation
      3. impact explanation
      4. remediation explanation
      5. judge-friendly explanation
    Enforces strict truth hierarchy: REAL OBSERVATION > REAL SOURCE CODE > REAL TOOL OUTPUT > DETERMINISTIC DETECTION > AI INTERPRETATION
    Returns provenance ('AI-ASSISTED' or 'DETERMINISTIC') and strict 'Insufficient evidence.' guards.
    """
    finding = db.query(Finding).filter(Finding.id == req.finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail=f"Finding {req.finding_id} not found")

    evidence = finding.evidence_records[0] if finding.evidence_records else None
    result = await ai_analysis_service.generate_5_point_explanation(finding, evidence)
    return {
        "success": True,
        "finding_id": finding.id,
        "ai_provider": result.get("ai_provider", "fallback"),
        "data": result
    }

