from pathlib import Path
from fastapi import UploadFile
import shutil
from app.core.config import settings
from app.utils.file_helpers import generate_unique_filename

class StorageService:
    """OOP Service for managing local file persistence."""

    def __init__(self):
        self.base_dir = settings.BASE_RESUME_DIR
        self.tailored_dir = settings.TAILORED_RESUME_DIR
        self._ensure_dirs()

    def _ensure_dirs(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.tailored_dir.mkdir(parents=True, exist_ok=True)

    def save_base_resume(self, upload_file: UploadFile) -> tuple[str, Path]:
        filename = generate_unique_filename(upload_file.filename or "resume.pdf")
        destination = self.base_dir / filename
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return filename, destination

    def save_tailored_resume(self, content: str, original_filename: str) -> tuple[str, Path]:
        filename = f"tailored_{generate_unique_filename(original_filename)}.txt"
        destination = self.tailored_dir / filename
        destination.write_text(content, encoding="utf-8")
        return filename, destination
