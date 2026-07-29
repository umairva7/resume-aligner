from pathlib import Path
import pypdf
import docx
from app.utils.text_helpers import clean_extracted_text

class ResumeParserService:
    """OOP Service for extracting clean text from PDF, DOCX, and TXT files."""
    
    def parse_file(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            text = self._parse_pdf(file_path)
        elif suffix == ".docx":
            text = self._parse_docx(file_path)
        elif suffix == ".txt":
            text = self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {suffix}")
        
        return clean_extracted_text(text)

    def _parse_pdf(self, file_path: Path) -> str:
        text = ""
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text

    def _parse_docx(self, file_path: Path) -> str:
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    def _parse_txt(self, file_path: Path) -> str:
        return file_path.read_text(encoding="utf-8", errors="ignore")
