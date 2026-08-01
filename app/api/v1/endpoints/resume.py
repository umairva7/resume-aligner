from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.core.config import settings
from app.core.logging import logger
from app.db import models
from app.schemas.resume import BaseResumeResponse, BaseResumeDetailResponse
from app.utils.file_helpers import is_allowed_file

router = APIRouter()

@router.post("/upload", response_model=BaseResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_base_resume(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    storage_service = Depends(deps.get_storage_service),
    parser_service = Depends(deps.get_parser_service)
):
    """Upload, validate, and parse candidate base resume."""
    if not file.filename or not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload PDF, DOCX, or TXT."
        )

    # Validate File Size Limit
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    # Save to disk
    filename, saved_path = storage_service.save_base_resume(file)

    # Parse text
    try:
        extracted_text = parser_service.parse_file(saved_path)
    except Exception as e:
        logger.error("Text parsing failed for %s: %s", filename, str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to extract text from resume file."
        )

    if len(extracted_text.strip()) < 20:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Resume text contains insufficient information. Please upload a clear document."
        )

    # Save record to database
    repo = deps.get_resume_repository(db)
    resume = repo.create(
        filename=filename,
        file_path=str(saved_path),
        extracted_text=extracted_text,
        user_id=current_user.id
    )

    logger.info("Base resume uploaded successfully for user_id=%s, resume_id=%s", current_user.id, resume.id)
    return resume


@router.get("/active", response_model=BaseResumeDetailResponse)
def get_active_resume(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Retrieve the currently active base resume."""
    repo = deps.get_resume_repository(db)
    resume = repo.get_active_resume(user_id=current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active base resume found. Please upload one first."
        )
    return resume

@router.delete("/active", status_code=status.HTTP_204_NO_CONTENT)
def delete_active_resume(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Delete the currently active base resume."""
    repo = deps.get_resume_repository(db)
    resume = repo.get_active_resume(user_id=current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active base resume found."
        )
    
    # We should delete the record
    db.delete(resume)
    db.commit()
    return None
