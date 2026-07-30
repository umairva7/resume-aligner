from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.resume import TailorResumeRequest, TailoredResumeResponse, MatchAnalysisRequest, MatchAnalysisResponse
from app.db import models
from app.db.models import TailoredResume, MatchAnalysis
from app.services.tailor_service import ResumeTailorService
from app.services.match_service import MatchAnalyzerService
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/analyze-match", response_model=MatchAnalysisResponse)
async def analyze_resume_match(
    payload: MatchAnalysisRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    match_service: MatchAnalyzerService = Depends(deps.get_match_service)
):
    """Analyze match score, skills overlap/missing, and recommendations for active base resume."""
    repo = deps.get_resume_repository(db)
    active_resume = repo.get_active_resume(user_id=current_user.id)
    if not active_resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active base resume found. Upload a resume first."
        )

    target_job_title = payload.job_title or "Target Position"
    
    try:
        analysis_result = await match_service.analyze_match(
            resume_id=active_resume.id,
            job_title=target_job_title,
            job_description=payload.job_description
        )
        return analysis_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Match Analysis failed: {str(e)}"
        )


@router.post("/align", response_model=TailoredResumeResponse)
async def align_resume(
    payload: TailorResumeRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    tailor_service: ResumeTailorService = Depends(deps.get_tailor_service)
):
    """Tailor base resume against target job description using configured LLM Provider."""
    repo = deps.get_resume_repository(db)
    active_resume = repo.get_active_resume(user_id=current_user.id)
    if not active_resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active base resume found. Upload a resume first."
        )

    # 1. Cleanup old records (6 hours expiration)
    six_hours_ago = datetime.utcnow() - timedelta(hours=6)
    db.query(TailoredResume).filter(
        TailoredResume.base_resume_id == active_resume.id,
        TailoredResume.created_at < six_hours_ago
    ).delete()
    db.commit()

    # 2. Check Daily Limit (Max 3 per day)
    start_of_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    daily_count = db.query(TailoredResume).filter(
        TailoredResume.base_resume_id == active_resume.id,
        TailoredResume.created_at >= start_of_today
    ).count()

    if daily_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily limit reached. You can only tailor 3 resumes per day to save storage."
        )

    target_job_title = payload.job_title or "Target Position"
    existing_tailored = db.query(TailoredResume).filter(
        TailoredResume.base_resume_id == active_resume.id,
        TailoredResume.job_title == target_job_title,
        TailoredResume.job_description_text == payload.job_description
    ).order_by(TailoredResume.created_at.desc()).first()

    if existing_tailored:
        return existing_tailored

    try:
        tailored_text = await tailor_service.tailor_resume(
            resume_id=active_resume.id,
            job_title=target_job_title,
            job_description=payload.job_description,
            linkedin_url=payload.linkedin_url,
            github_url=payload.github_url,
            portfolio_url=payload.portfolio_url
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM Tailoring failed: {str(e)}"
        )

    tailored_record = active_resume.tailored_versions[-1]
    return tailored_record


@router.get("/download-pdf/{tailored_id}")
def download_tailored_pdf(
    tailored_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    pdf_service = Depends(deps.get_pdf_service)
):
    """Generate and return ATS-friendly PDF file for a tailored resume."""
    tailored_record = db.query(TailoredResume).filter(TailoredResume.id == tailored_id).first()
    if not tailored_record or tailored_record.base_resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tailored resume record not found."
        )

    try:
        pdf_path = pdf_service.create_ats_pdf(
            markdown_text=tailored_record.tailored_text,
            filename_prefix=f"Tailored_{tailored_record.job_title or 'Resume'}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF Generation failed: {str(e)}"
        )

    clean_filename = f"ATS_Tailored_Resume_{tailored_record.job_title or 'Target'}.pdf".replace(" ", "_")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=clean_filename,
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'}
    )


@router.get("/download-docx/{tailored_id}")
def download_tailored_docx(
    tailored_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    docx_service = Depends(deps.get_docx_service)
):
    """Generate and return ATS-friendly Word DOCX file for a tailored resume."""
    tailored_record = db.query(TailoredResume).filter(TailoredResume.id == tailored_id).first()
    if not tailored_record or tailored_record.base_resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tailored resume record not found."
        )

    try:
        docx_path = docx_service.create_ats_docx(
            markdown_text=tailored_record.tailored_text,
            filename_prefix=f"Tailored_{tailored_record.job_title or 'Resume'}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DOCX Generation failed: {str(e)}"
        )

    clean_filename = f"ATS_Tailored_Resume_{tailored_record.job_title or 'Target'}.docx".replace(" ", "_")

    return FileResponse(
        path=str(docx_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=clean_filename,
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'}
    )

@router.get("/history", response_model=List[TailoredResumeResponse])
def get_tailoring_history(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Retrieve up to the last 3 tailored resumes generated for the active base resume."""
    repo = deps.get_resume_repository(db)
    active_resume = repo.get_active_resume(user_id=current_user.id)
    if not active_resume:
        return []

    six_hours_ago = datetime.utcnow() - timedelta(hours=6)
    db.query(TailoredResume).filter(
        TailoredResume.base_resume_id == active_resume.id,
        TailoredResume.created_at < six_hours_ago
    ).delete()
    db.commit()

    history = db.query(TailoredResume).filter(
        TailoredResume.base_resume_id == active_resume.id
    ).order_by(TailoredResume.created_at.desc()).limit(3).all()
    
    return history
