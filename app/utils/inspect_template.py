from pathlib import Path
import docx

doc_path = Path('/home/umairimran/OLD DISK/Projects/resume-aligner/uploads/umair_backend_v2.docx')
doc = docx.Document(str(doc_path))

out = []
out.append("=== SECTIONS & MARGINS ===")
for i, s in enumerate(doc.sections):
    out.append(f"Section {i+1}: Top={s.top_margin.inches}in, Bottom={s.bottom_margin.inches}in, Left={s.left_margin.inches}in, Right={s.right_margin.inches}in")

out.append("\n=== PARAGRAPHS DETAIL ===")
for i, p in enumerate(doc.paragraphs):
    if p.text.strip():
        runs = []
        for r in p.runs:
            color = r.font.color.rgb if r.font and r.font.color else None
            font_name = r.font.name if r.font else None
            font_size = r.font.size.pt if r.font and r.font.size else None
            runs.append(f"(text='{r.text}', font={font_name}, size={font_size}, bold={r.bold}, color={color})")
        out.append(f"P{i+1} [Style: {p.style.name}, Align: {p.alignment}]: {p.text}")
        out.append(f"   Runs: {', '.join(runs)}")

Path('/home/umairimran/OLD DISK/Projects/resume-aligner/template_analysis.txt').write_text("\n".join(out), encoding='utf-8')
print("Wrote template_analysis.txt")
