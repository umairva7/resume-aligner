import json
from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.db.models import Resume, TailoredResume, MatchAnalysis

class ResumeRepository(BaseRepository[Resume]):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, item_id: int, user_id: Optional[int] = None) -> Optional[Resume]:
        query = self.db.query(Resume).filter(Resume.id == item_id)
        if user_id:
            query = query.filter(Resume.user_id == user_id)
        return query.first()

    def get_active_resume(self, user_id: Optional[int] = None) -> Optional[Resume]:
        query = self.db.query(Resume).filter(Resume.is_active == True)
        if user_id:
            query = query.filter(Resume.user_id == user_id)
        return query.order_by(Resume.id.desc()).first()

    def get_all(self, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[Resume]:
        query = self.db.query(Resume)
        if user_id:
            query = query.filter(Resume.user_id == user_id)
        return query.offset(skip).limit(limit).all()

    def create(self, filename: str, file_path: str, extracted_text: str, user_id: Optional[int] = None) -> Resume:
        query = self.db.query(Resume)
        if user_id:
            query = query.filter(Resume.user_id == user_id)
        query.update({"is_active": False})
        
        resume = Resume(
            filename=filename,
            file_path=file_path,
            extracted_text=extracted_text,
            is_active=True,
            user_id=user_id
        )
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def delete(self, item_id: int, user_id: Optional[int] = None) -> bool:
        resume = self.get_by_id(item_id, user_id)
        if resume:
            self.db.delete(resume)
            self.db.commit()
            return True
        return False

    def save_tailored_version(
        self, base_resume_id: int, job_title: str, job_description_text: str, tailored_text: str, 
        before_score: Optional[int] = None, after_score: Optional[int] = None, analysis_note: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> TailoredResume:
        tailored = TailoredResume(
            base_resume_id=base_resume_id,
            job_title=job_title,
            job_description_text=job_description_text,
            tailored_text=tailored_text,
            before_score=before_score,
            after_score=after_score,
            analysis_note=analysis_note,
            file_path=file_path
        )
        self.db.add(tailored)
        self.db.commit()
        self.db.refresh(tailored)
        return tailored

    def get_cached_match_analysis(self, base_resume_id: int, job_description_text: str) -> Optional[MatchAnalysis]:
        return self.db.query(MatchAnalysis).filter(
            MatchAnalysis.base_resume_id == base_resume_id,
            MatchAnalysis.job_description_text == job_description_text
        ).order_by(MatchAnalysis.created_at.desc()).first()

    def save_match_analysis(
        self, base_resume_id: int, resume_hash: str, job_title: str, job_description_text: str,
        match_score: int, skills_matched: list, skills_missing: list,
        keywords_found: int, keywords_total: int, recommendations: list
    ) -> MatchAnalysis:
        analysis = MatchAnalysis(
            base_resume_id=base_resume_id,
            resume_hash=resume_hash,
            job_title=job_title,
            job_description_text=job_description_text,
            match_score=match_score,
            skills_matched=json.dumps(skills_matched),
            skills_missing=json.dumps(skills_missing),
            keywords_found=keywords_found,
            keywords_total=keywords_total,
            recommendations=json.dumps(recommendations)
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
