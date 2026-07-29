from typing import Generator
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.resume_repository import ResumeRepository
from app.services.parser_service import ResumeParserService
from app.services.storage_service import StorageService
from app.services.llm_service import BaseLLMProvider, OllamaLLMProvider, MockLLMProvider, GeminiLLMProvider
from app.services.tailor_service import ResumeTailorService

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_resume_repository(db: Session = None) -> ResumeRepository:
    if db is None:
        db = next(get_db())
    return ResumeRepository(db)

def get_parser_service() -> ResumeParserService:
    return ResumeParserService()

def get_storage_service() -> StorageService:
    return StorageService()

def get_llm_provider() -> BaseLLMProvider:
    provider_type = settings.LLM_PROVIDER.lower()
    if provider_type == "mock":
        return MockLLMProvider()
    elif provider_type == "gemini":
        return GeminiLLMProvider()
    elif provider_type == "ollama":
        return OllamaLLMProvider()
    else:
        # Default fallback to Mock if invalid or unknown provider configured
        return MockLLMProvider()

def get_tailor_service(
    llm: BaseLLMProvider = None,
    repo: ResumeRepository = None
) -> ResumeTailorService:
    if llm is None:
        llm = get_llm_provider()
    if repo is None:
        repo = get_resume_repository()
    return ResumeTailorService(llm_provider=llm, repository=repo)
