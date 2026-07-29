from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.db.models import Resume, TailoredResume

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
        # Deactivate previous resumes if single active resume policy
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
        self, base_resume_id: int, job_title: str, job_description_text: str, tailored_text: str, file_path: Optional[str] = None
    ) -> TailoredResume:
        tailored = TailoredResume(
            base_resume_id=base_resume_id,
            job_title=job_title,
            job_description_text=job_description_text,
            tailored_text=tailored_text,
            file_path=file_path
        )
        self.db.add(tailored)
        self.db.commit()
        self.db.refresh(tailored)
        return tailored
