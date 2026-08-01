from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import httpx

from app.api import deps
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(deps.get_db)):
    """
    Production Health Check Endpoint.
    Monitors Database, Storage, and LLM Provider Connectivity.
    """
    health_status = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": "unknown",
        "storage": "unknown",
        "llm_provider": settings.LLM_PROVIDER
    }

    # 1. Check Database
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "healthy"
    except Exception as e:
        logger.error(f"Health Check Database Failure: {e}")
        health_status["database"] = "unhealthy"
        health_status["status"] = "degraded"

    # 2. Check Local File Storage Writeability
    try:
        base_dir_exists = settings.BASE_RESUME_DIR.exists()
        tailored_dir_exists = settings.TAILORED_RESUME_DIR.exists()
        if base_dir_exists and tailored_dir_exists:
            health_status["storage"] = "healthy"
        else:
            health_status["storage"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Health Check Storage Failure: {e}")
        health_status["storage"] = "unhealthy"
        health_status["status"] = "degraded"

    # 3. Check LLM Provider connectivity if Ollama
    if settings.LLM_PROVIDER.lower() == "ollama":
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags")
                if res.status_code == 200:
                    health_status["ollama_status"] = "healthy"
                else:
                    health_status["ollama_status"] = "unreachable"
        except Exception:
            health_status["ollama_status"] = "unreachable"

    return health_status
