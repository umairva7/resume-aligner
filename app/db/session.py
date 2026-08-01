from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings
import os

db_url = settings.DATABASE_URL

# Ensure relative SQLite URLs resolve properly to BASE_DIR or writeable location
if "sqlite" in db_url:
    if db_url.startswith("sqlite:///./"):
        db_file_name = db_url.replace("sqlite:///./", "")
        abs_db_path = settings.BASE_DIR / db_file_name
        db_url = f"sqlite:///{abs_db_path}"
    
    # Test if SQLite location is writeable; if not, fallback to ~/.resume_aligner/resume_aligner.db
    try:
        db_path = db_url.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path) or "."
        test_file = os.path.join(db_dir, ".db_write_test")
        with open(test_file, "w") as f:
            f.write("test")
        if os.path.exists(test_file):
            os.remove(test_file)
    except Exception:
        fallback_dir = os.path.expanduser("~/.resume_aligner")
        os.makedirs(fallback_dir, exist_ok=True)
        fallback_path = os.path.join(fallback_dir, "resume_aligner.db")
        db_url = f"sqlite:///{fallback_path}"

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
