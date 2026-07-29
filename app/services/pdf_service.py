import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from app.core.config import settings
from app.utils.file_helpers import generate_unique_filename

class PDFGeneratorService:
    """
    OOP Service for compiling Markdown-formatted resumes into ATS-compliant PDFs.
    Ensures clean single-column structure, standard fonts, parseable text streams,
    and professional typography.
    """

    def create_ats_pdf(self, markdown_text: str, filename_prefix: str = "tailored_resume") -> Path:
        output_filename = f"{generate_unique_filename(filename_prefix)}.pdf"
        output_path = settings.TAILORED_RESUME_DIR / output_filename
        settings.TAILORED_RESUME_DIR.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom ATS-Friendly Styles
        title_style = ParagraphStyle(
            'ATSTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=6
        )

        h2_style = ParagraphStyle(
            'ATSH2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#2563EB'),
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True
        )

        h3_style = ParagraphStyle(
            'ATSH3',
            parent=styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor('#0F172A'),
            spaceBefore=4,
            spaceAfter=2,
            keepWithNext=True
        )

        body_style = ParagraphStyle(
            'ATSBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor('#334155'),
            spaceAfter=4
        )

        bullet_style = ParagraphStyle(
            'ATSBullet',
            parent=body_style,
            leftIndent=14,
            firstLineIndent=-8,
            spaceAfter=3
        )

        story = []
        lines = markdown_text.splitlines()

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Convert markdown formatting (**bold**, *italic*) to HTML tags for ReportLab Paragraph
            line_html = self._convert_markdown_to_html(line_str)

            if line_str.startswith("# "):
                text = line_html.lstrip("#").strip()
                story.append(Paragraph(text, title_style))
                story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#CBD5E1"), spaceAfter=8))
            elif line_str.startswith("## "):
                text = line_html.lstrip("#").strip()
                story.append(Paragraph(text, h2_style))
                story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#E2E8F0"), spaceAfter=6))
            elif line_str.startswith("### "):
                text = line_html.lstrip("#").strip()
                story.append(Paragraph(text, h3_style))
            elif line_str.startswith("- ") or line_str.startswith("* "):
                text = line_html[2:].strip()
                story.append(Paragraph(f"• {text}", bullet_style))
            elif re.match(r'^\d+\.\s', line_str):
                text = re.sub(r'^\d+\.\s', '', line_html)
                story.append(Paragraph(text, bullet_style))
            else:
                story.append(Paragraph(line_html, body_style))

        doc.build(story)
        return output_path

    def _convert_markdown_to_html(self, text: str) -> str:
        """Helper to translate basic markdown syntax to ReportLab Paragraph markup."""
        # Convert **bold** to <b>bold</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Convert *italic* or _italic_ to <i>italic</i>
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.*?)_', r'<i>\1</i>', text)
        return text
