import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.models import KnowledgeRecord
from backend.app.schemas.schemas import KnowledgeResponse
from backend.app.services.knowledge_service import knowledge_service

router = APIRouter(prefix="/knowledge", tags=["Knowledge Correlation"])

def _serialize_knowledge(k: KnowledgeRecord) -> dict:
    try:
        rem = json.loads(k.remediation) if k.remediation else []
    except Exception:
        rem = []
    return {
        "id": k.id,
        "type": k.type,
        "title": k.title,
        "description": k.description,
        "related_owasp": k.related_owasp,
        "remediation": rem,
        "category": k.category
    }

@router.get("", response_model=List[KnowledgeResponse])
def get_all_knowledge(type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(KnowledgeRecord)
    if type:
        query = query.filter(KnowledgeRecord.type == type.upper())
    records = query.all()
    return [_serialize_knowledge(k) for k in records]

@router.get("/correlate")
def correlate_knowledge(
    category: str = "",
    title: str = "",
    cwe_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    corr = knowledge_service.correlate(db, category=category, title=title, cwe_id=cwe_id or "")
    return {
        "cwe": _serialize_knowledge(corr["cwe"]) if corr.get("cwe") else None,
        "owasp": _serialize_knowledge(corr["owasp"]) if corr.get("owasp") else None
    }

@router.get("/{knowledge_id}", response_model=KnowledgeResponse)
def get_knowledge_item(knowledge_id: str, db: Session = Depends(get_db)):
    record = knowledge_service.get_by_id(db, knowledge_id)
    if not record:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    return _serialize_knowledge(record)
