from app.services.llm_service import BaseLLMProvider
from app.repositories.resume_repository import ResumeRepository

SYSTEM_PROMPT = """You are an expert resume tailoring specialist and career coach.
Your task is to take a candidate's base resume and a specific job description, and adapt the resume to align with the target role.

STRICT RULES:
1. Maintain absolute truthfulness: DO NOT invent fake experiences, positions, or fake certifications.
2. Rephrase bullet points to emphasize relevant skills, technologies, and achievements mentioned in the target job description.
3. Optimize formatting, section headers, and keyword alignment for Applicant Tracking Systems (ATS).
4. Output the complete, beautifully structured tailored resume in Markdown format.
"""

class ResumeTailorService:
    """
    OOP Orchestrator Service combining Resume DB data, Prompt Engineering,
    and LLM Execution.
    """

    def __init__(self, llm_provider: BaseLLMProvider, repository: ResumeRepository):
        self.llm_provider = llm_provider
        self.repository = repository

    async def tailor_resume(self, resume_id: int, job_title: str, job_description: str) -> str:
        resume = self.repository.get_by_id(resume_id)
        if not resume:
            raise ValueError(f"Resume with ID {resume_id} not found.")

        user_prompt = f"""
TARGET JOB TITLE:
{job_title}

TARGET JOB DESCRIPTION:
{job_description}

CANDIDATE BASE RESUME:
{resume.extracted_text}

Please generate a tailored version of the candidate's resume that optimizes keywords and highlights matching experience for this position.
"""
        tailored_text = await self.llm_provider.generate_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt
        )

        # Save tailored record in DB
        self.repository.save_tailored_version(
            base_resume_id=resume.id,
            job_title=job_title,
            job_description_text=job_description,
            tailored_text=tailored_text
        )

        return tailored_text
