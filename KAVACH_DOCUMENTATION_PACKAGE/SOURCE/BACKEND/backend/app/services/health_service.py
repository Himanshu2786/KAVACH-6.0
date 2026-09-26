from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.services.ollama_service import ollama_service
from backend.app.models.models import KnowledgeRecord, Assessment, Finding

class HealthService:
    async def get_system_status(self, db: Session) -> Dict[str, Any]:
        # 1. Ollama status
        ollama_info = await ollama_service.check_health()

        # 2. Database check
        db_status = "ONLINE"
        try:
            db.execute(text("SELECT 1"))
        except Exception:
            db_status = "DEGRADED"

        # 3. Knowledge engine check
        knowledge_count = db.query(KnowledgeRecord).count()
        knowledge_status = "READY" if knowledge_count > 0 else "INITIALIZING"

        # 4. Assessment & Findings counts
        active_assessments = db.query(Assessment).filter(Assessment.status == "RUNNING").count()
        total_findings = db.query(Finding).count()

        return {
            "frontend_status": "ONLINE",
            "backend_status": "ONLINE",
            "ollama_status": ollama_info.get("status", "offline").upper(),
            "ollama_model": ollama_info.get("selected_model", ""),
            "ollama_base_url": ollama_info.get("base_url", ""),
            "ollama_models_available": ollama_info.get("available_models", []),
            "ollama_response_time_ms": ollama_info.get("response_time_ms"),
            "database_status": db_status,
            "knowledge_engine": f"{knowledge_status} ({knowledge_count} records)",
            "assessment_engine": "READY",
            "validation_engine": "READY",
            "active_assessment_count": active_assessments,
            "total_findings_count": total_findings
        }

health_service = HealthService()
