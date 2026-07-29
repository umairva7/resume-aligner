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

        template_path = getattr(settings, 'DOCX_TEMPLATE_PATH', None)
        
        has_template = False
        if template_path and template_path.exists():
            try:
                doc = docx.Document(str(template_path))
                # Clear existing content from the template (retain styles, headers, footers)
                for paragraph in doc.paragraphs:
                    p = paragraph._element
                    p.getparent().remove(p)
                    p._p = p._element = None
                for table in doc.tables:
                    t = table._element
                    t.getparent().remove(t)
                    t._tbl = t._element = None
                has_template = True
            except Exception:
                doc = docx.Document()
        else:
            doc = docx.Document()

        if not has_template:
            # Set 0.5 inch margins for default blank doc
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
                p = self._add_styled_paragraph(doc, 'Heading 1')
                if not has_template:
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(6)
                self._add_formatted_runs(p, text, is_heading=True, level=1, has_template=has_template)
            elif line_str.startswith("## "):
                text = line_str.lstrip("#").strip()
                p = self._add_styled_paragraph(doc, 'Heading 2')
                if not has_template:
                    p.paragraph_format.space_before = Pt(12)
                    p.paragraph_format.space_after = Pt(4)
                self._add_formatted_runs(p, text, is_heading=True, level=2, has_template=has_template)
            elif line_str.startswith("### "):
                text = line_str.lstrip("#").strip()
                p = self._add_styled_paragraph(doc, 'Heading 3')
                if not has_template:
                    p.paragraph_format.space_before = Pt(6)
                    p.paragraph_format.space_after = Pt(2)
                self._add_formatted_runs(p, text, is_heading=True, level=3, has_template=has_template)
            elif line_str.startswith("- ") or line_str.startswith("* "):
                text = line_str[2:].strip()
                p = self._add_styled_paragraph(doc, 'List Bullet')
                if not has_template:
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(3)
                self._add_formatted_runs(p, text, has_template=has_template)
            else:
                p = self._add_styled_paragraph(doc, 'Normal')
                if not has_template:
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(4)
                self._add_formatted_runs(p, line_str, has_template=has_template)

        doc.save(str(output_path))
        return output_path

    def _add_styled_paragraph(self, doc, style_name):
        try:
            return doc.add_paragraph(style=style_name)
        except KeyError:
            return doc.add_paragraph()

    def _add_formatted_runs(self, paragraph, text: str, is_heading: bool = False, level: int = 0, has_template: bool = False):
        """Parse basic **bold** tags and add formatted runs to docx paragraph."""
        tokens = re.split(r'(\*\*.*?\*\*)', text)
        for token in tokens:
            if not token:
                continue
            
            is_bold = False
            run_text = token
            if token.startswith("**") and token.endswith("**"):
                is_bold = True
                run_text = token[2:-2]
                
            run = paragraph.add_run(run_text)
            
            if is_bold:
                run.bold = True
                
            if not has_template:
                # Apply hardcoded styles if no template is used
                run.font.name = 'Calibri'
                if is_heading:
                    run.bold = True
                    if level == 1:
                        run.font.size = Pt(18)
                        run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
                    elif level == 2:
                        run.font.size = Pt(13)
                        run.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
                    elif level == 3:
                        run.font.size = Pt(11)
                        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
                else:
                    run.font.size = Pt(10)
                    run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
