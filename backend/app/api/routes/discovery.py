from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.schemas.schemas import DiscoveryItemResponse
from backend.app.services.discovery_service import discovery_service

router = APIRouter(prefix="/discovery", tags=["Discovery"])

@router.get("/{assessment_id}", response_model=List[DiscoveryItemResponse])
def get_discovery(assessment_id: str, db: Session = Depends(get_db)):
    return discovery_service.get_discovery_items(db, assessment_id)

@router.post("/{assessment_id}", response_model=DiscoveryItemResponse)
def add_discovery_item(
    assessment_id: str,
    item_type: str = Body(...),
    name: str = Body(...),
    method: str = Body(""),
    path: str = Body(""),
    details: str = Body(""),
    security_relevance: str = Body("MEDIUM"),
    db: Session = Depends(get_db)
):
    return discovery_service.add_item(
        db=db,
        assessment_id=assessment_id,
        item_type=item_type,
        name=name,
        method=method,
        path=path,
        details=details,
        security_relevance=security_relevance
    )
