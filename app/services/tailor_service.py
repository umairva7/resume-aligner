from app.services.llm_service import BaseLLMProvider
from app.repositories.resume_repository import ResumeRepository

SYSTEM_PROMPT = """You are an expert resume tailoring specialist and career coach.
Your task is to take a candidate's base resume and a specific job description, and adapt the resume to align with the target role.

STRICT RULES:
1. Maintain absolute truthfulness: DO NOT invent fake experiences, positions, or fake certifications.
2. Rephrase bullet points to emphasize relevant skills, technologies, and achievements mentioned in the target job description.
3. Optimize formatting, section headers, and keyword alignment for Applicant Tracking Systems (ATS).
4. You MUST format your response EXACTLY as follows, using these exact delimiters:

===RESUME===
# [Candidate Full Name]
[Contact Info line separated by | (e.g. Location | Email | Phone | LinkedIn)]

## PROFESSIONAL SUMMARY
[Summary paragraph]

## PROFESSIONAL EXPERIENCE
### [Job Title]
**[Company Name]** | [Dates]
- [Bullet points...]

===METRICS===
BEFORE_SCORE: [Integer 0-100]
AFTER_SCORE: [Integer 0-100]
NOTE: [Your helpful analysis note here, or leave blank if none]
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
        response_text = await self.llm_provider.generate_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt
        )

        import re
        
        parts = response_text.split("===METRICS===")
        resume_part = parts[0].replace("===RESUME===", "").strip()
        metrics_part = parts[1].strip() if len(parts) > 1 else ""
        
        tailored_text = resume_part
        before_score, after_score, analysis_note = None, None, None
        
        if metrics_part:
            b_match = re.search(r'BEFORE_SCORE:\s*(\d+)', metrics_part)
            a_match = re.search(r'AFTER_SCORE:\s*(\d+)', metrics_part)
            n_match = re.search(r'NOTE:\s*(.*)', metrics_part, re.DOTALL | re.IGNORECASE)
            
            if b_match: before_score = int(b_match.group(1))
            if a_match: after_score = int(a_match.group(1))
            if n_match: analysis_note = n_match.group(1).strip()

        # Save tailored record in DB
        self.repository.save_tailored_version(
            base_resume_id=resume.id,
            job_title=job_title,
            job_description_text=job_description,
            tailored_text=tailored_text,
            before_score=before_score,
            after_score=after_score,
            analysis_note=analysis_note
        )

        return tailored_text
