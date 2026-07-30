from app.services.llm_service import BaseLLMProvider
from app.repositories.resume_repository import ResumeRepository

SYSTEM_PROMPT = """You are an expert resume tailoring specialist and career coach.
Your task is to take a candidate's base resume and a specific job description, and adapt the resume to align with the target role.

STRICT RULES:
1. Maintain absolute truthfulness: DO NOT invent fake experiences, positions, or fake certifications.
2. Rephrase bullet points to emphasize relevant skills, technologies, and achievements mentioned in the target job description.
3. Optimize formatting, section headers, and keyword alignment for Applicant Tracking Systems (ATS).
4. You MUST output ONLY a valid JSON object with exactly these keys:
   - "tailored_resume_markdown": The complete, beautifully structured tailored resume in Markdown format.
   - "before_score": An integer (0-100) estimating how well the ORIGINAL resume matched the job description.
   - "after_score": An integer (0-100) estimating how well the TAILORED resume matches the job description.
   - "analysis_note": A helpful note (string) directed to the user. For example, if the resume is very different from the job, note how their transferable skills (like problem-solving) apply. Leave empty if no note is needed.
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

        import json
        import re
        
        # Try to extract JSON block if the LLM wrapped it in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
            
        try:
            parsed_data = json.loads(response_text)
            tailored_text = parsed_data.get("tailored_resume_markdown", "")
            before_score = parsed_data.get("before_score")
            after_score = parsed_data.get("after_score")
            analysis_note = parsed_data.get("analysis_note")
        except json.JSONDecodeError:
            # Fallback if LLM failed to output JSON
            tailored_text = response_text
            before_score = None
            after_score = None
            analysis_note = None

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
