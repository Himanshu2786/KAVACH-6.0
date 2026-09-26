from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.services.risk_service import risk_service
from backend.app.schemas.schemas import RiskPrioritizationItem

router = APIRouter(prefix="/risk", tags=["Risk Prioritization Engine"])

@router.get("/prioritization/{assessment_id}", response_model=List[RiskPrioritizationItem])
def get_risk_prioritization(assessment_id: str, db: Session = Depends(get_db)):
    return risk_service.prioritize_all_findings(db, assessment_id)
