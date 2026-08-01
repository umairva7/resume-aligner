from typing import Generator, Optional
from fastapi import Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.config import settings
from app.db.session import SessionLocal
from app.db import models
from app.repositories.resume_repository import ResumeRepository
from app.services.parser_service import ResumeParserService
from app.services.storage_service import StorageService
from app.services.llm_service import BaseLLMProvider, OllamaLLMProvider, MockLLMProvider, GeminiLLMProvider, GroqLLMProvider, HuggingFaceLLMProvider
from app.services.tailor_service import ResumeTailorService
from app.services.match_service import MatchAnalyzerService

from app.services.pdf_service import PDFGeneratorService
from app.services.docx_service import DOCXGeneratorService

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_resume_repository(db: Session = Depends(get_db)) -> ResumeRepository:
    return ResumeRepository(db)

def get_parser_service() -> ResumeParserService:
    return ResumeParserService()

def get_storage_service() -> StorageService:
    return StorageService()

def get_pdf_service() -> PDFGeneratorService:
    return PDFGeneratorService()

def get_docx_service() -> DOCXGeneratorService:
    return DOCXGeneratorService()

def get_llm_provider() -> BaseLLMProvider:
    provider_type = settings.LLM_PROVIDER.lower()
    if provider_type in ["huggingface", "hf"]:
        return HuggingFaceLLMProvider()
    elif provider_type == "groq":
        return GroqLLMProvider()
    elif provider_type == "gemini":
        return GeminiLLMProvider()
    elif provider_type == "ollama":
        return OllamaLLMProvider()
    else:
        return MockLLMProvider()

def get_tailor_service(
    db: Session = Depends(get_db)
) -> ResumeTailorService:
    llm = get_llm_provider()
    repo = ResumeRepository(db)
    return ResumeTailorService(llm_provider=llm, repository=repo)

def get_match_service(
    db: Session = Depends(get_db)
) -> MatchAnalyzerService:
    llm = get_llm_provider()
    repo = ResumeRepository(db)
    return MatchAnalyzerService(llm_provider=llm, repository=repo)

from app.services.usage_service import UsageLimitService

def get_usage_service(
    db: Session = Depends(get_db)
) -> UsageLimitService:
    return UsageLimitService(db)

def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[models.User]:
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
        
    user_session = db.query(models.UserSession).filter(models.UserSession.session_token == session_token).first()
    if not user_session:
        return None
        
    if user_session.expires_at < datetime.utcnow():
        db.delete(user_session)
        db.commit()
        return None
        
    return user_session.user

def get_current_user(current_user: Optional[models.User] = Depends(get_current_user_optional)) -> models.User:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return current_user
