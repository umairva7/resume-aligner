from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.resume import TailorResumeRequest, TailoredResumeResponse

router = APIRouter()

@router.post("/align", response_model=TailoredResumeResponse)
async def align_resume(
    payload: TailorResumeRequest,
    db: Session = Depends(deps.get_db)
):
    """Tailor base resume against target job description using Ollama LLM."""
    repo = deps.get_resume_repository(db)
    active_resume = repo.get_active_resume()
    if not active_resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active base resume found. Upload a resume first."
        )

    llm = deps.get_llm_provider()
    tailor_service = deps.get_tailor_service(llm=llm, repo=repo)

    try:
        tailored_text = await tailor_service.tailor_resume(
            resume_id=active_resume.id,
            job_title=payload.job_title or "Target Position",
            job_description=payload.job_description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM Tailoring failed: {str(e)}"
        )

    # Get latest tailored record
    tailored_record = active_resume.tailored_versions[-1]
    return tailored_record
