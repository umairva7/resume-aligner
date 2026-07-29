from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "Resume Aligner"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000

    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATABASE_URL: str = "sqlite:///./resume_aligner.db"

    # Storage Paths
    BASE_RESUME_DIR: Path = BASE_DIR / "uploads" / "base_resumes"
    TAILORED_RESUME_DIR: Path = BASE_DIR / "uploads" / "tailored_resumes"

    # LLM Configuration
    LLM_PROVIDER: str = "ollama"  # Options: "ollama", "mock", "gemini", "openai"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
