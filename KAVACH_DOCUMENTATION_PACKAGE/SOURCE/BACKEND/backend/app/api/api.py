from fastapi import APIRouter
from backend.app.api.routes import (
    system,
    assessments,
    discovery,
    findings,
    knowledge,
    evidence,
    risk,
    remediation,
    reports,
    portable,
    team,
    experience,
    test_center,
    ai,
    rag,
    url_check,
    world_monitor,
    forensic,
    auth,
    activity,
    feedback,
    team_admin
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(system.router)
api_router.include_router(ai.router)
api_router.include_router(rag.router)
api_router.include_router(url_check.router)
api_router.include_router(world_monitor.router)
api_router.include_router(forensic.router)
api_router.include_router(assessments.router)
api_router.include_router(discovery.router)
api_router.include_router(findings.router)
api_router.include_router(knowledge.router)
api_router.include_router(evidence.router)
api_router.include_router(risk.router)
api_router.include_router(remediation.router)
api_router.include_router(reports.router)
api_router.include_router(portable.router)
api_router.include_router(team.router)
api_router.include_router(experience.router)
api_router.include_router(test_center.router)
api_router.include_router(activity.router)
api_router.include_router(feedback.router)
api_router.include_router(team_admin.router)
