from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.config import settings
from app.core.logging import logger
from app.db.session import engine
from app.db import models
from app.api import deps
from app.schemas.resume import MatchAnalysisRequest, MatchAnalysisResponse
from app.api.v1.router import api_router

# Initialize database tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise AI Resume Alignment & ATS Optimization Engine",
    version="2.5.0",
    openapi_url="/api/v1/openapi.json"
)

# Parse configured CORS origins cleanly
allowed_origins_list = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
if not allowed_origins_list:
    allowed_origins_list = [settings.FRONTEND_URL, "http://localhost:8000"]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global Exception Handler to prevent stack traces leaking to production users
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled Exception on %s %s: %s", request.method, request.url.path, str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": "Internal server error. Please try again later.",
            "error_code": "INTERNAL_SERVER_ERROR",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )

# Root Health Route for Uptime Monitors (Pingdom/UptimeRobot/Sentry)
@app.get("/health", tags=["System Health"])
async def root_health_check(db: Session = Depends(deps.get_db)):
    """Convenience top-level health check endpoint."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# Root endpoint for direct POST /analyze-match as requested in deliverables
@app.post("/analyze-match", response_model=MatchAnalysisResponse, tags=["Match Analyzer"])
async def analyze_match_root(
    payload: MatchAnalysisRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    match_service = Depends(deps.get_match_service)
):
    repo = deps.get_resume_repository(db)
    active_resume = repo.get_active_resume(user_id=current_user.id)
    if not active_resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active base resume found. Upload a resume first."
        )

    target_job_title = payload.job_title or "Target Position"
    try:
        return await match_service.analyze_match(
            resume_id=active_resume.id,
            job_title=target_job_title,
            job_description=payload.job_description
        )
    except Exception as e:
        logger.error("Root analyze match error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Match Analysis failed. Please verify job description input."
        )

# Include API endpoints
app.include_router(api_router, prefix="/api/v1")

# Mount Static Frontend
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
