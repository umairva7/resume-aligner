from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.resume import TailorResumeRequest, TailoredResumeResponse
from app.db import models
from app.db.models import TailoredResume

router = APIRouter()

@router.post("/align", response_model=TailoredResumeResponse)
async def align_resume(
    payload: TailorResumeRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Tailor base resume against target job description using configured LLM Provider."""
    repo = deps.get_resume_repository(db)
    active_resume = repo.get_active_resume(user_id=current_user.id)
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
