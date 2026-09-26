from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reporting Engine"])

@router.get("/{assessment_id}")
def get_report_json(assessment_id: str, db: Session = Depends(get_db)):
    try:
        return report_service.generate_report_data(db, assessment_id)
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))

@router.get("/{assessment_id}/html", response_class=HTMLResponse)
def get_report_html(assessment_id: str, db: Session = Depends(get_db)):
    try:
        html_content = report_service.generate_html_report(db, assessment_id)
        return HTMLResponse(content=html_content, status_code=200)
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
