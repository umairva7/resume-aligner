from abc import ABC, abstractmethod
import httpx
from app.core.config import settings

class BaseLLMProvider(ABC):
    """Abstract Strategy Class for LLM interaction."""
    
    @abstractmethod
    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        pass


class OllamaLLMProvider(BaseLLMProvider):
    """Ollama implementation of LLM provider."""
    
    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL, model: str = settings.OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_error()
            data = response.json()
            return data.get("response", "")


class MockLLMProvider(BaseLLMProvider):
    """Mock Provider for testing without installing Ollama or API keys."""
    
    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        return """# Tailored Resume (Mock Mode)

## Professional Summary
Results-driven Software Engineer with extensive experience in Python, FastAPI, and scalable system design. Proven track record of delivering high-performance backend systems and AI-integrated applications aligned with business goals.

## Core Technical Skills
- **Languages:** Python, JavaScript, SQL, HTML/CSS
- **Frameworks & Libraries:** FastAPI, SQLAlchemy, Pydantic, React
- **AI & LLM Integration:** Local LLM Workflows (Ollama), Prompt Engineering, RAG Architectures
- **Tools & DBs:** SQLite, PostgreSQL, Git, Docker, RESTful APIs

## Professional Experience

### Senior Software Engineer — Tech Solutions Inc.
*2022 — Present*
- Spearheaded the architectural migration of legacy backend APIs to FastAPI, reducing request latency by 40%.
- Integrated local AI models and vector retrieval strategies to optimize resume matching workflows.
- Mentored junior engineers and instituted OOP best practices across core codebase.

### Full Stack Developer — Innovative Apps
*2020 — 2022*
- Engineered responsive user interfaces and backend API routes serving 50k+ active users.
- Collaborated with product teams to design robust data repositories and relational database schemas.

## Education
- **B.S. in Computer Science** — University of Engineering & Technology

---
*Note: This is a generated mock response for offline testing. Configure Ollama or API keys in .env to run with real LLM inference.*
"""


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini API Provider."""
    
    def __init__(self, api_key: str = settings.GEMINI_API_KEY):
        self.api_key = api_key

    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment settings.")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\n{user_prompt}"}
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_error()
            data = response.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                return "Error processing response from Gemini API."
