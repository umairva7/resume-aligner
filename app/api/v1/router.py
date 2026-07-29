from fastapi import APIRouter
from app.api.v1.endpoints import resume, tailor, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(resume.router, prefix="/resume", tags=["Base Resume"])
api_router.include_router(tailor.router, prefix="/tailor", tags=["Resume Tailoring"])
