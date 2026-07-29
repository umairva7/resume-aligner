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
