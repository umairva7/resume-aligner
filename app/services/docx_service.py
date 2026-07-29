import re
from pathlib import Path
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from app.core.config import settings
from app.utils.file_helpers import generate_unique_filename

class DOCXGeneratorService:
    """
    OOP Service for compiling Markdown-formatted resumes into ATS-compliant Microsoft Word (.docx) files.
    """

    def create_ats_docx(self, markdown_text: str, filename_prefix: str = "tailored_resume") -> Path:
        output_filename = f"{generate_unique_filename(filename_prefix)}.docx"
        output_path = settings.TAILORED_RESUME_DIR / output_filename
        settings.TAILORED_RESUME_DIR.mkdir(parents=True, exist_ok=True)

        doc = docx.Document()

        # Set 0.5 inch margins
        for section in doc.sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.5)
            section.right_margin = Inches(0.5)

        lines = markdown_text.splitlines()

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            if line_str.startswith("# "):
                text = line_str.lstrip("#").strip()
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(6)
                run = p.add_run(text)
                run.bold = True
                run.font.name = 'Calibri'
                run.font.size = Pt(18)
                run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
            elif line_str.startswith("## "):
                text = line_str.lstrip("#").strip()
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(4)
                run = p.add_run(text)
                run.bold = True
                run.font.name = 'Calibri'
                run.font.size = Pt(13)
                run.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
            elif line_str.startswith("### "):
                text = line_str.lstrip("#").strip()
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(2)
                run = p.add_run(text)
                run.bold = True
                run.font.name = 'Calibri'
                run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            elif line_str.startswith("- ") or line_str.startswith("* "):
                text = line_str[2:].strip()
                p = doc.add_paragraph(style='List Bullet')
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(3)
                self._add_formatted_runs(p, text)
            else:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(4)
                self._add_formatted_runs(p, line_str)

        doc.save(str(output_path))
        return output_path

    def _add_formatted_runs(self, paragraph, text: str):
        """Parse basic **bold** tags and add formatted runs to docx paragraph."""
        tokens = re.split(r'(\*\*.*?\*\*)', text)
        for token in tokens:
            if not token:
                continue
            if token.startswith("**") and token.endswith("**"):
                bold_text = token[2:-2]
                run = paragraph.add_run(bold_text)
                run.bold = True
                run.font.name = 'Calibri'
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
            else:
                run = paragraph.add_run(token)
                run.font.name = 'Calibri'
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
