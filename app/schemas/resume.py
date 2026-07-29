from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# --- Base Resume Schemas ---
class BaseResumeResponse(BaseModel):
    id: int
    filename: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BaseResumeDetailResponse(BaseResumeResponse):
    extracted_text: str


# --- Tailoring Schemas ---
class TailorResumeRequest(BaseModel):
    job_title: Optional[str] = "Target Role"
    job_description: str


class TailoredResumeResponse(BaseModel):
    id: int
    base_resume_id: int
    job_title: Optional[str]
    tailored_text: str
    created_at: datetime

    class Config:
        from_attributes = True
