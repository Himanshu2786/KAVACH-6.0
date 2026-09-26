from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from backend.app.core.database import engine, Base, SessionLocal, migrate_schema
from backend.app.data.seed_data import seed_database
from backend.app.api.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables and migrate columns if needed
    Base.metadata.create_all(bind=engine)
    migrate_schema(engine)
    # Seed initial demo data and knowledge base
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="KAVACH — AI-Assisted, Evidence-Driven Security Assessment Platform. Core Principle: AI Hypothesizes. Evidence Confirms.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for structured consistent error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "details": type(exc).__name__
            }
        }
    )

@app.get("/api/health")
def root_health_check():
    return {
        "status": "online",
        "platform": settings.PROJECT_NAME,
        "tagline": "AI Hypothesizes. Evidence Confirms.",
        "version": settings.VERSION,
        "demo_mode": settings.DEMO_MODE
    }

# Include all API routes under /api
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static frontend if dist folder exists (for portable standalone execution)
import sys
import os
from fastapi.staticfiles import StaticFiles

def get_frontend_dist_dir():
    # 1. Check PyInstaller bundle dir
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dist = os.path.join(sys._MEIPASS, "frontend", "dist")
        if os.path.exists(bundle_dist):
            return bundle_dist
    # 2. Check relative to backend/app/main.py
    rel_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
    if os.path.exists(rel_dist):
        return rel_dist
    # 3. Check current working directory
    cwd_dist = os.path.join(os.getcwd(), "frontend", "dist")
    if os.path.exists(cwd_dist):
        return cwd_dist
    return None

frontend_dist = get_frontend_dist_dir()
if frontend_dist:
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static_frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
