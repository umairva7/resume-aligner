from abc import ABC, abstractmethod
import httpx
from app.core.config import settings
from app.core.logging import logger

class BaseLLMProvider(ABC):
    """Abstract Strategy Class for LLM interaction."""
    
    @abstractmethod
    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        pass


class OllamaLLMProvider(BaseLLMProvider):
    """Ollama implementation of LLM provider for local deployment."""
    
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
        
        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.TimeoutException:
            logger.error("Ollama request timed out after %s seconds", settings.LLM_TIMEOUT_SECONDS)
            raise RuntimeError("Ollama service timed out. Please try again shortly.")
        except httpx.ConnectError:
            logger.error("Could not connect to Ollama instance at %s", self.base_url)
            raise RuntimeError("Ollama service is unreachable. Verify Ollama is running.")
        except Exception as e:
            logger.error("Unexpected error calling Ollama: %s", str(e))
            raise RuntimeError(f"Ollama generation failed: {str(e)}")


class HuggingFaceLLMProvider(BaseLLMProvider):
    """
    Hugging Face Serverless Inference API Provider.
    Uses free HF Access Token (hf_...) to run open-weights models like Llama 3 or Qwen 2.5.
    """
    
    def __init__(
        self,
        api_key: str = settings.HF_API_KEY,
        model: str = settings.HF_MODEL
    ):
        self.api_key = api_key
        self.model = model

    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            raise ValueError("HF_API_KEY is not set in environment settings.")
        
        url = "https://router.huggingface.co/hf-inference/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class GroqLLMProvider(BaseLLMProvider):
    """
    Groq API Provider (Runs Llama 3 in the cloud for free with sub-second latency).
    Perfect for portfolio deployment on Railway/Render.
    """
    
    def __init__(self, api_key: str = settings.GROQ_API_KEY, model: str = settings.GROQ_MODEL):
        self.api_key = api_key
        self.model = model

    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set in environment settings.")
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


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
            response.raise_for_status()
            data = response.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                return "Error processing response from Gemini API."


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

## Education
- **B.S. in Computer Science** — University of Engineering & Technology
"""
