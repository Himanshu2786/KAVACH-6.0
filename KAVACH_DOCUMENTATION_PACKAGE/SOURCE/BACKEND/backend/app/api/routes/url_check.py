"""
KAVACH URL Security Assessment API Routes
Endpoints for:
- POST /api/url-check/scan
- GET /api/url-check/latest
- POST /api/url-check/re-verify
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.audit import log_audit_event
from backend.app.services.url_scanner_service import url_scanner_service

router = APIRouter(prefix="/url-check", tags=["URL Security Assessment"])


class UrlScanRequest(BaseModel):
    url: str = Field(..., json_schema_extra={"example": "https://example.com"})
    parent_assessment_id: Optional[str] = Field(default=None, description="Optional parent assessment ID")
    related_assessment_id: Optional[str] = Field(default=None, description="Optional related assessment ID")


@router.post("/scan")
async def scan_url(req: UrlScanRequest, db: Session = Depends(get_db)):
    """Executes safe, non-destructive web security checks against target URL."""
    from backend.app.core.target_config import is_world_monitor_target
    from backend.app.models.models import Assessment

    parent_id = req.parent_assessment_id or req.related_assessment_id
    if not parent_id and is_world_monitor_target(req.url):
        from backend.app.api.routes.assessments import get_latest_world_monitor_assessment
        wm_latest = get_latest_world_monitor_assessment(db)
        if wm_latest and wm_latest.get("status") != "NO_ASSESSMENT_RUN":
            parent_id = wm_latest.get("assessment_id")

    res = await url_scanner_service.assess_url(
        target_url=req.url,
        parent_assessment_id=parent_id,
        db=db
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Invalid URL"))

    run_id = res.get("run_id")
    # Log audit event with isolated run_id
    log_audit_event(
        db=db,
        event_type="URL_ASSESSMENT_COMPLETED",
        description=f"Assessed {req.url} [{res.get('assessment_status', 'COMPLETE')}]: score={res['security_score']}, findings={res['findings_count']} (Run: {run_id})",
        module="URL_ASSESSMENT",
        status="SUCCESS",
        assessment_id=run_id,
        metadata={
            "run_id": run_id,
            "target_url": req.url,
            "findings_count": res["findings_count"],
            "score": res["security_score"],
            "assessment_status": res.get("assessment_status"),
            "parent_assessment_id": parent_id
        }
    )

    return res


@router.get("/latest")
def get_latest_url_assessment(db: Session = Depends(get_db)):
    """Returns the latest URL assessment result, persisting across restarts."""
    return url_scanner_service.get_latest(db=db)


@router.post("/re-verify")
async def reverify_url(req: UrlScanRequest, db: Session = Depends(get_db)):
    """Re-checks the target URL to observe remediation differences."""
    res = await url_scanner_service.reverify_url(req.url, db=db)

    run_id = res.get("run_id")
    resolved_count = res.get("reverification", {}).get("resolved_count", 0)
    log_audit_event(
        db=db,
        event_type="URL_REVERIFICATION_COMPLETED",
        description=f"Re-verified {req.url}: resolved={resolved_count} findings (Run: {run_id})",
        module="URL_ASSESSMENT",
        status="SUCCESS",
        assessment_id=run_id,
        metadata={
            "run_id": run_id,
            "target_url": req.url,
            "resolved_count": resolved_count
        }
    )

    return res

