from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.services.health_service import health_service
from backend.app.services.ollama_service import ollama_service
from backend.app.schemas.schemas import OllamaStatusResponse, ModelSelectionRequest, SystemStatusResponse, AuditEventResponse
from backend.app.models.models import AuditEvent
from typing import List, Optional

router = APIRouter(prefix="/system", tags=["System & AI Engine"])

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(db: Session = Depends(get_db)):
    return await health_service.get_system_status(db)

@router.get("/ollama", response_model=OllamaStatusResponse)
async def get_ollama_status():
    return await ollama_service.check_health()

@router.post("/ollama/select-model")
async def select_ollama_model(req: ModelSelectionRequest):
    ollama_service.set_model(req.model_name)
    return {"success": True, "selected_model": req.model_name}

@router.post("/ollama/timeout")
async def update_ollama_timeout(timeout_sec: float = Body(..., embed=True)):
    ollama_service.set_timeout(timeout_sec)
    return {"success": True, "timeout_seconds": timeout_sec}

@router.get("/audit", response_model=List[AuditEventResponse])
def get_audit_trail(
    assessment_id: Optional[str] = None,
    module: Optional[str] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(AuditEvent)
    if assessment_id:
        query = query.filter(AuditEvent.assessment_id == assessment_id)
    if module:
        query = query.filter(AuditEvent.module == module)
    if event_type:
        query = query.filter(AuditEvent.event_type == event_type)
    if status:
        query = query.filter(AuditEvent.status == status)
    return query.order_by(AuditEvent.id.desc()).limit(limit).all()

@router.get("/geolocate")
async def get_network_geolocation():
    """
    Returns approximate network/IP-derived geolocation when device GPS is unavailable or denied.
    Strictly adheres to KAVACH privacy rules (no personal street address or building details).
    """
    import httpx
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get("https://ipapi.co/json/")
            if resp.status_code == 200:
                data = resp.json()
                lat = data.get("latitude")
                lon = data.get("longitude")
                if lat is not None and lon is not None:
                    return {
                        "success": True,
                        "location_type": "APPROXIMATE_NETWORK_LOCATION",
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "country_name": data.get("country_name", "Unknown"),
                        "city": data.get("city", "Unknown")
                    }
    except Exception:
        pass

    return {
        "success": False,
        "location_type": "LOCATION_UNAVAILABLE",
        "latitude": None,
        "longitude": None,
        "error": "Network location unavailable"
    }
