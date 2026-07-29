from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.resume import BaseResumeResponse, BaseResumeDetailResponse
from app.utils.file_helpers import is_allowed_file

router = APIRouter()

@router.post("/upload", response_model=BaseResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_base_resume(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    storage_service = Depends(deps.get_storage_service),
    parser_service = Depends(deps.get_parser_service)
):
    """Upload and parse base resume."""
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload PDF, DOCX, or TXT."
        )

    # Save to disk
    filename, saved_path = storage_service.save_base_resume(file)

    # Parse text
    try:
        extracted_text = parser_service.parse_file(saved_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse resume text: {str(e)}"
        )

    # Save record to database
    repo = deps.get_resume_repository(db)
    resume = repo.create(
        filename=filename,
        file_path=str(saved_path),
        extracted_text=extracted_text
    )

    return resume


@router.get("/active", response_model=BaseResumeDetailResponse)
def get_active_resume(db: Session = Depends(deps.get_db)):
    """Retrieve the currently active base resume."""
    repo = deps.get_resume_repository(db)
    resume = repo.get_active_resume()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active base resume found. Please upload one first."
        )
    return resume
