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
    linkedin_url: str
    github_url: str
    portfolio_url: Optional[str] = None


class TailoredResumeResponse(BaseModel):
    id: int
    base_resume_id: int
    job_title: Optional[str]
    tailored_text: str
    before_score: Optional[int]
    after_score: Optional[int]
    analysis_note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Match Analyzer Schemas ---
class MatchAnalysisRequest(BaseModel):
    job_title: Optional[str] = "Target Role"
    job_description: str


class MatchAnalysisResponse(BaseModel):
    id: Optional[int] = None
    status: str = "success"
    match_score: int
    skills_matched: List[str]
    skills_missing: List[str]
    keywords_found: int
    keywords_total: int
    recommendations: List[str]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
