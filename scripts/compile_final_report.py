import os
import shutil
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

MD_PATH = "docs/DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.md"
DOCX_PATH = "docs/DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.docx"
PDF_PATH = "docs/DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.pdf"

# -------------------------------------------------------------
# 1. Compile DOCX using python-docx
# -------------------------------------------------------------
def compile_docx(md_content):
    doc = Document()
    
    # Page Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Document Title
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("DUKAANDOST AI 2.0")
    r_title.bold = True
    r_title.font.size = Pt(24)
    r_title.font.color.rgb = RGBColor(6, 182, 212) # Cyan
    
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Autonomous AI Retail Business Operating System • Final Technical Report")
    r_sub.font.size = Pt(14)
    r_sub.font.color.rgb = RGBColor(107, 114, 128)
    
    doc.add_paragraph("─" * 60)

    lines = md_content.split('\n')
    in_table = False
    table_rows = []

    for line in lines:
        line_str = line.strip()
        if not line_str:
            if in_table and table_rows:
                # render table
                render_docx_table(doc, table_rows)
                in_table = False
                table_rows = []
            continue

        if line_str.startswith('|') and line_str.endswith('|'):
            # Table row
            if '---' in line_str:
                continue
            cols = [c.strip() for c in line_str.split('|')[1:-1]]
            table_rows.append(cols)
            in_table = True
            continue
        elif in_table:
            render_docx_table(doc, table_rows)
            in_table = False
            table_rows = []

        if line_str.startswith('# '):
            continue # already added title
        elif line_str.startswith('## '):
            h = doc.add_heading(level=1)
            r = h.add_run(line_str[3:])
            r.font.size = Pt(16)
            r.font.color.rgb = RGBColor(14, 116, 144)
        elif line_str.startswith('### '):
            h = doc.add_heading(level=2)
            r = h.add_run(line_str[4:])
            r.font.size = Pt(13)
            r.font.color.rgb = RGBColor(31, 41, 55)
        elif line_str.startswith('#### '):
            h = doc.add_heading(level=3)
            r = h.add_run(line_str[5:])
            r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(55, 65, 81)
        elif line_str.startswith('- ') or line_str.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            parse_formatting_docx(p, line_str[2:])
        elif re.match(r'^\d+\.\s', line_str):
            p = doc.add_paragraph(style='List Number')
            content = re.sub(r'^\d+\.\s', '', line_str)
            parse_formatting_docx(p, content)
        else:
            p = doc.add_paragraph()
            parse_formatting_docx(p, line_str)

    if in_table and table_rows:
        render_docx_table(doc, table_rows)

    doc.save(DOCX_PATH)
    print(f"Generated DOCX: {DOCX_PATH}")

def render_docx_table(doc, rows):
    if not rows:
        return
    num_cols = len(rows[0])
    tbl = doc.add_table(rows=len(rows), cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row_data in enumerate(rows):
        for c_idx, cell_data in enumerate(row_data):
            if c_idx < num_cols:
                cell = tbl.cell(r_idx, c_idx)
                cell.text = cell_data
                if r_idx == 0:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.bold = True
                            run.font.color.rgb = RGBColor(14, 116, 144)

def parse_formatting_docx(paragraph, text):
    # simple bold/italic parser
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            r = paragraph.add_run(part[2:-2])
            r.bold = True
        elif part.startswith('*') and part.endswith('*'):
            r = paragraph.add_run(part[1:-1])
            r.italic = True
        elif part.startswith('`') and part.endswith('`'):
            r = paragraph.add_run(part[1:-1])
            r.font.name = 'Consolas'
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(180, 83, 9)
        else:
            paragraph.add_run(part)

# -------------------------------------------------------------
# 2. Compile PDF using ReportLab
# -------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "DukaanDost AI 2.0 — Final Engineering Technical Report")
            self.drawRightString(558, 750, "Eko AI Internship Review")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Confidential & Proprietary • Autonomous Kirana Growth Operating System")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()

def compile_pdf(md_content):
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0891B2"), # Cyan
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0E7490"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=15,
        spaceAfter=3
    )

    story = []

    # Title Banner
    story.append(Paragraph("DUKAANDOST AI 2.0", title_style))
    story.append(Paragraph("Autonomous AI Retail Business Operating System • Final Engineering Specification", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0891B2"), spaceAfter=15))

    lines = md_content.split('\n')
    in_table = False
    table_rows = []

    for line in lines:
        line_str = line.strip()
        if not line_str:
            if in_table and table_rows:
                story.append(build_pdf_table(table_rows))
                story.append(Spacer(1, 8))
                in_table = False
                table_rows = []
            continue

        if line_str.startswith('|') and line_str.endswith('|'):
            if '---' in line_str:
                continue
            cols = [c.strip() for c in line_str.split('|')[1:-1]]
            table_rows.append(cols)
            in_table = True
            continue
        elif in_table:
            story.append(build_pdf_table(table_rows))
            story.append(Spacer(1, 8))
            in_table = False
            table_rows = []

        if line_str.startswith('# '):
            continue
        elif line_str.startswith('## '):
            story.append(Paragraph(clean_md_tags(line_str[3:]), h1_style))
        elif line_str.startswith('### '):
            story.append(Paragraph(clean_md_tags(line_str[4:]), h2_style))
        elif line_str.startswith('- ') or line_str.startswith('* '):
            bullet_text = f"&bull; {clean_md_tags(line_str[2:])}"
            story.append(Paragraph(bullet_text, bullet_style))
        elif re.match(r'^\d+\.\s', line_str):
            clean_text = clean_md_tags(line_str)
            story.append(Paragraph(clean_text, bullet_style))
        else:
            story.append(Paragraph(clean_md_tags(line_str), body_style))

    if in_table and table_rows:
        story.append(build_pdf_table(table_rows))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {PDF_PATH}")

def build_pdf_table(rows):
    if not rows:
        return Spacer(1, 1)
    
    table_data = []
    p_style = ParagraphStyle('TableCell', fontName='Helvetica', fontSize=7.5, leading=10, textColor=colors.HexColor("#1E293B"))
    header_style = ParagraphStyle('TableHead', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)

    for r_idx, row in enumerate(rows):
        row_cells = []
        for cell_text in row:
            st = header_style if r_idx == 0 else p_style
            row_cells.append(Paragraph(clean_md_tags(cell_text), st))
        table_data.append(row_cells)

    col_widths = [504 / len(rows[0])] * len(rows[0])
    tbl = Table(table_data, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0E7490")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    return tbl

def clean_md_tags(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#B45309">\1</font>', text)
    text = text.replace('&', '&amp;') if '&amp;' not in text else text
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', text)
    return text

if __name__ == "__main__":
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    compile_docx(content)
    compile_pdf(content)
    
    # Also copy to frontend/public and root so user can easily download it
    shutil.copy(PDF_PATH, "frontend/public/DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.pdf")
    shutil.copy(PDF_PATH, "DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.pdf")
    print("Copied PDF to frontend/public and root workspace.")
