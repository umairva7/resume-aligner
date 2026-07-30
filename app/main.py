from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import engine
from app.db import models
from app.api import deps
from app.schemas.resume import MatchAnalysisRequest, MatchAnalysisResponse
from app.api.v1.router import api_router

# Initialize database tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url="/api/v1/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Match Analysis failed: {str(e)}"
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
