from pydantic_settings import BaseSettings, SettingsConfigDict
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
    DOCX_TEMPLATE_PATH: Path = BASE_DIR / "uploads" / "umair_backend_v2.docx"

    # LLM Configuration
    LLM_PROVIDER: str = "mock"  # Options: "mock", "ollama", "groq", "huggingface", "gemini"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    HF_API_KEY: str = ""
    HF_MODEL: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Auth Configuration
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    SESSION_SECRET: str = "super-secret-key-change-in-production"
    FRONTEND_URL: str = "http://localhost:8000"
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"
    ALLOWED_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"
    SECURE_COOKIES: bool = False

    # Security & Storage Limits
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB
    MAX_JOB_DESCRIPTION_CHARS: int = 25000
    MAX_RESUME_TEXT_CHARS: int = 30000
    LLM_TIMEOUT_SECONDS: float = 30.0

    # Daily Feature Rate Limits
    DAILY_MATCH_LIMIT: int = 5
    DAILY_TAILOR_LIMIT: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
