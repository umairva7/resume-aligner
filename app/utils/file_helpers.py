import re
import uuid
from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def is_allowed_file(filename: str) -> bool:
    """Check if uploaded file extension is supported."""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename: str) -> str:
    """Generate a safe, unique filename preventing overwrite collisions."""
    ext = Path(original_filename).suffix.lower()
    clean_stem = re.sub(r'[^a-zA-Z0-9_-]', '_', Path(original_filename).stem)
    unique_id = uuid.uuid4().hex[:8]
    return f"{clean_stem}_{unique_id}{ext}"
