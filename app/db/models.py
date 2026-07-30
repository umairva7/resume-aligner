from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    google_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    picture: Mapped[str] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    resumes: Mapped[list["Resume"]] = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list["UserSession"]] = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    session_token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="sessions")

class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="resumes")
    tailored_versions: Mapped[list["TailoredResume"]] = relationship(
        "TailoredResume", back_populates="base_resume", cascade="all, delete-orphan"
    )
    match_analyses: Mapped[list["MatchAnalysis"]] = relationship(
        "MatchAnalysis", back_populates="base_resume", cascade="all, delete-orphan"
    )

class TailoredResume(Base):
    __tablename__ = "tailored_resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    base_resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_title: Mapped[str] = mapped_column(String(255), nullable=True)
    job_description_text: Mapped[str] = mapped_column(Text, nullable=False)
    tailored_text: Mapped[str] = mapped_column(Text, nullable=False)
    before_score: Mapped[int] = mapped_column(Integer, nullable=True)
    after_score: Mapped[int] = mapped_column(Integer, nullable=True)
    analysis_note: Mapped[str] = mapped_column(Text, nullable=True)
    file_path: Mapped[str] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    base_resume: Mapped["Resume"] = relationship("Resume", back_populates="tailored_versions")

class MatchAnalysis(Base):
    __tablename__ = "match_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    base_resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resumes.id"), nullable=False)
    resume_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    job_title: Mapped[str] = mapped_column(String(255), nullable=True)
    job_description_text: Mapped[str] = mapped_column(Text, nullable=False)
    match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    skills_matched: Mapped[str] = mapped_column(Text, nullable=True)  # Stored as JSON string
    skills_missing: Mapped[str] = mapped_column(Text, nullable=True)  # Stored as JSON string
    keywords_found: Mapped[int] = mapped_column(Integer, nullable=True)
    keywords_total: Mapped[int] = mapped_column(Integer, nullable=True)
    recommendations: Mapped[str] = mapped_column(Text, nullable=True)  # Stored as JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    base_resume: Mapped["Resume"] = relationship("Resume", back_populates="match_analyses")
