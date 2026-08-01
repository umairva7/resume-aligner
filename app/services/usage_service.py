from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import MatchAnalysis, TailoredResume, Resume
from app.core.config import settings

class UsageLimitService:
    """Service to track and compute daily feature rate limits and reset countdowns."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_usage_status(self, user_id: int) -> Dict[str, Any]:
        start_of_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        next_reset = start_of_today + timedelta(days=1)
        reset_in_seconds = max(0, int((next_reset - datetime.utcnow()).total_seconds()))

        # Match Analysis count today
        match_used = (
            self.db.query(MatchAnalysis)
            .join(Resume, MatchAnalysis.base_resume_id == Resume.id)
            .filter(Resume.user_id == user_id, MatchAnalysis.created_at >= start_of_today)
            .count()
        )

        # Tailored Resume count today
        tailor_used = (
            self.db.query(TailoredResume)
            .join(Resume, TailoredResume.base_resume_id == Resume.id)
            .filter(Resume.user_id == user_id, TailoredResume.created_at >= start_of_today)
            .count()
        )

        match_limit = settings.DAILY_MATCH_LIMIT
        tailor_limit = settings.DAILY_TAILOR_LIMIT

        return {
            "reset_at": next_reset.isoformat() + "Z",
            "reset_in_seconds": reset_in_seconds,
            "match": {
                "limit": match_limit,
                "used": match_used,
                "remaining": max(0, match_limit - match_used)
            },
            "tailor": {
                "limit": tailor_limit,
                "used": tailor_used,
                "remaining": max(0, tailor_limit - tailor_used)
            }
        }

    def check_and_increment_match(self, user_id: int):
        status = self.get_user_usage_status(user_id)
        if status["match"]["remaining"] <= 0:
            reset_hours = status["reset_in_seconds"] // 3600
            reset_mins = (status["reset_in_seconds"] % 3600) // 60
            raise ValueError(
                f"Daily limit reached for Match Analyzer ({status['match']['limit']}/{status['match']['limit']} used). "
                f"Resets in {reset_hours}h {reset_mins}m."
            )

    def check_and_increment_tailor(self, user_id: int):
        status = self.get_user_usage_status(user_id)
        if status["tailor"]["remaining"] <= 0:
            reset_hours = status["reset_in_seconds"] // 3600
            reset_mins = (status["reset_in_seconds"] % 3600) // 60
            raise ValueError(
                f"Daily limit reached for Resume Tailor ({status['tailor']['limit']}/{status['tailor']['limit']} used). "
                f"Resets in {reset_hours}h {reset_mins}m."
            )
