import pytest
import pytest_asyncio
from app.services.llm_service import MockLLMProvider
from app.services.match_service import MatchAnalyzerService
from app.repositories.resume_repository import ResumeRepository

@pytest.mark.asyncio
async def test_match_analyzer_service_caching(db_session):
    repo = ResumeRepository(db_session)
    resume = repo.create(
        filename="john_doe_resume.pdf",
        file_path="/uploads/john_doe_resume.pdf",
        extracted_text="Senior Python FastAPI Developer with 5 years experience building scalable backend APIs."
    )
    
    mock_llm = MockLLMProvider()
    match_service = MatchAnalyzerService(llm_provider=mock_llm, repository=repo)

    job_title = "Senior Python Engineer"
    job_description = "We are seeking a Senior Python Developer proficient in FastAPI, PostgreSQL, and cloud deployments."

    # 1. First run (Calls LLM, computes, caches result)
    result1 = await match_service.analyze_match(
        resume_id=resume.id,
        job_title=job_title,
        job_description=job_description
    )

    assert result1["status"] == "success"
    assert "match_score" in result1
    assert "skills_matched" in result1

    # 2. Second run (Hit cache instantly)
    result2 = await match_service.analyze_match(
        resume_id=resume.id,
        job_title=job_title,
        job_description=job_description
    )

    assert result2["id"] == result1["id"]
    assert result2["match_score"] == result1["match_score"]
