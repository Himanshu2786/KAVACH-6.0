"""
KAVACH 5.0 — World Monitor API Routes
Endpoints for:
- GET /api/world-monitor/events
- POST /api/world-monitor/refresh
- POST /api/world-monitor/correlate
- GET /api/world-monitor/sources
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.audit import log_audit_event
from backend.app.services.world_monitor_service import world_monitor_service

router = APIRouter(prefix="/world-monitor", tags=["World Monitor Situational Awareness"])


class RefreshRequest(BaseModel):
    mode: Optional[str] = None  # "live", "demo", or None


class CorrelateRequest(BaseModel):
    target_url: Optional[str] = ""
    hostname: Optional[str] = ""
    findings: Optional[List[Dict[str, Any]]] = []


@router.get("/events")
def get_world_events(
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    time_range: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    mode: Optional[str] = Query(None)
):
    """Returns filtered situational awareness events from CISA, NVD, and authoritative security feeds."""
    return world_monitor_service.get_events(
        category=category,
        severity=severity,
        time_range=time_range,
        source=source,
        search=search,
        mode=mode
    )


@router.post("/refresh")
async def refresh_world_events(req: Optional[RefreshRequest] = None, db: Session = Depends(get_db)):
    """Synchronizes with live public feeds (CISA KEV) or resets to deterministic demo fixtures."""
    mode_arg = req.mode if req else None
    res = await world_monitor_service.refresh_feeds(force_mode=mode_arg)

    log_audit_event(
        db=db,
        event_type="WORLD_MONITOR_REFRESHED",
        description=f"World Monitor synchronized: mode={res['mode']}, events={res['events_count']}",
        module="WORLD_MONITOR",
        status="SUCCESS",
        metadata={"mode": res["mode"], "events_count": res["events_count"], "last_updated": res["last_updated"]}
    )

    return res


@router.post("/correlate")
def correlate_events(req: CorrelateRequest):
    """
    Correlates external World Monitor advisories against the target's verified findings
    to provide explainable context.
    """
    correlations = world_monitor_service.correlate_with_findings(
        target_info={"target_url": req.target_url, "hostname": req.hostname},
        local_findings=req.findings or []
    )
    return {
        "success": True,
        "count": len(correlations),
        "correlations": correlations
    }


@router.get("/sources")
def get_sources_status():
    """Returns the operational status of all external situational data source adapters."""
    return {
        "success": True,
        "last_updated": world_monitor_service._last_updated,
        "mode": "LIVE" if world_monitor_service._is_live_mode else "DEMO",
        "sources": world_monitor_service._source_statuses
    }


@router.get("/target")
def get_target_configuration():
    """Returns the centralized authorized target configuration for World Monitor."""
    from core.target_config import get_world_monitor_target
    return {
        "success": True,
        "target": get_world_monitor_target()
    }
