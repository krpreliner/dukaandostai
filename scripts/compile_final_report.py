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
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

MD_PATH = "docs/DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.md"
DOCX_PATH = "docs/DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.docx"
PDF_PATH = "docs/DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.pdf"

# -------------------------------------------------------------
# Register TrueType Fonts with native Unicode Rupee (₹) support
# -------------------------------------------------------------
FONT_DIR = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont('Arial', os.path.join(FONT_DIR, 'arial.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(FONT_DIR, 'arialbd.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(FONT_DIR, 'ariali.ttf')))
pdfmetrics.registerFont(TTFont('Arial-BoldItalic', os.path.join(FONT_DIR, 'arialbi.ttf')))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Italic', boldItalic='Arial-BoldItalic')

pdfmetrics.registerFont(TTFont('Consolas', os.path.join(FONT_DIR, 'consola.ttf')))
pdfmetrics.registerFont(TTFont('Consolas-Bold', os.path.join(FONT_DIR, 'consolab.ttf')))
pdfmetrics.registerFontFamily('Consolas', normal='Consolas', bold='Consolas-Bold')

# -------------------------------------------------------------
# 1. Compile DOCX using python-docx
# -------------------------------------------------------------
def compile_docx(md_content):
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Document Title
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("DUKAANDOST AI 2.0")
    r_title.bold = True
    r_title.font.size = Pt(24)
    r_title.font.name = 'Arial'
    r_title.font.color.rgb = RGBColor(8, 145, 178) # Cyan
    
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Autonomous AI Retail Business Operating System • Final Technical Report")
    r_sub.font.size = Pt(13)
    r_sub.font.name = 'Arial'
    r_sub.font.color.rgb = RGBColor(14, 116, 144)
    
    doc.add_paragraph("─" * 60)

    lines = md_content.split('\n')
    in_table = False
    table_rows = []

    for line in lines:
        line_str = line.strip()
        if not line_str:
            if in_table and table_rows:
                render_docx_table(doc, table_rows)
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
            render_docx_table(doc, table_rows)
            in_table = False
            table_rows = []

        if line_str.startswith('# '):
            continue
        elif line_str.startswith('## '):
            h = doc.add_heading(level=1)
            r = h.add_run(line_str[3:])
            r.font.name = 'Arial'
            r.font.size = Pt(15)
            r.font.color.rgb = RGBColor(14, 116, 144)
        elif line_str.startswith('### '):
            h = doc.add_heading(level=2)
            r = h.add_run(line_str[4:])
            r.font.name = 'Arial'
            r.font.size = Pt(12)
            r.font.color.rgb = RGBColor(30, 41, 59)
        elif line_str.startswith('#### '):
            h = doc.add_heading(level=3)
            r = h.add_run(line_str[5:])
            r.font.name = 'Arial'
            r.font.size = Pt(10.5)
            r.font.color.rgb = RGBColor(51, 65, 85)
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
                            run.font.name = 'Arial'
                            run.font.color.rgb = RGBColor(14, 116, 144)

def parse_formatting_docx(paragraph, text):
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            r = paragraph.add_run(part[2:-2])
            r.bold = True
            r.font.name = 'Arial'
        elif part.startswith('*') and part.endswith('*'):
            r = paragraph.add_run(part[1:-1])
            r.italic = True
            r.font.name = 'Arial'
        elif part.startswith('`') and part.endswith('`'):
            r = paragraph.add_run(part[1:-1])
            r.font.name = 'Consolas'
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(180, 83, 9)
        else:
            r = paragraph.add_run(part)
            r.font.name = 'Arial'

# -------------------------------------------------------------
# 2. Compile PDF using ReportLab with NumberedCanvas & Arial
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
        # Native Arial font for headers & footers
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "DukaanDost AI 2.0 — Final Engineering Technical Report")
            self.drawRightString(558, 750, "Eko AI Technical Review")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer (All Pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Confidential & Proprietary • Sharma General Store, Ranchi")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()

def clean_md_tags(text):
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    code_spans = []
    def code_repl(m):
        code_spans.append(m.group(1))
        return f"___CODE_SPAN_{len(code_spans)-1}___"
    text = re.sub(r'`(.*?)`', code_repl, text)

    bold_spans = []
    def bold_repl(m):
        bold_spans.append(m.group(1))
        return f"___BOLD_SPAN_{len(bold_spans)-1}___"
    text = re.sub(r'\*\*(.*?)\*\*', bold_repl, text)

    italic_spans = []
    def italic_repl(m):
        italic_spans.append(m.group(1))
        return f"___ITALIC_SPAN_{len(italic_spans)-1}___"
    text = re.sub(r'\*(.*?)\*', italic_repl, text)

    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')

    for i, span in enumerate(italic_spans):
        span = span.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text = text.replace(f"___ITALIC_SPAN_{i}___", f"<i>{span}</i>")

    for i, span in enumerate(bold_spans):
        span = span.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text = text.replace(f"___BOLD_SPAN_{i}___", f"<b>{span}</b>")

    for i, span in enumerate(code_spans):
        span = span.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text = text.replace(f"___CODE_SPAN_{i}___", f'<font face="Consolas" color="#0369A1">{span}</font>')

    return text

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
    
    badge_style = ParagraphStyle(
        'DocBadge',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0891B2"),
        spaceAfter=10
    )

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0891B2"), # Cyan
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor("#0E7490"),
        spaceAfter=4
    )

    tagline_style = ParagraphStyle(
        'DocTagline',
        parent=styles['Normal'],
        fontName='Arial-Italic',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=13.5,
        leading=17.5,
        textColor=colors.HexColor("#0E7490"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Heading3_Custom',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=14,
        spaceAfter=3
    )

    caption_style = ParagraphStyle(
        'Caption_Custom',
        parent=styles['Normal'],
        fontName='Arial-Italic',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B"),
        alignment=1, # Center
        spaceAfter=8
    )

    story = []

    # Cover Page Elements
    story.append(Paragraph("EKO AI INTERNSHIP TECHNICAL EVALUATION • PRODUCTION SYSTEM SPECIFICATION", badge_style))
    story.append(Paragraph("DUKAANDOST AI 2.0", title_style))
    story.append(Paragraph("Autonomous AI Retail Business Operating System", subtitle_style))
    story.append(Paragraph('"Your Autonomous AI Business Partner That Doesn\'t Just Advise. It Takes Action."', tagline_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0891B2"), spaceAfter=15))

    lines = md_content.split('\n')
    in_table = False
    table_rows = []
    in_code_block = False
    code_lines = []

    # Diagram paths
    diagram_map = {
        "## 7. System Architecture": ("architecture/dukaandost_system_architecture.png", "Figure 1: DukaanDost AI 2.0 End-to-End System Architecture (Client, Gateway, Multi-Agent, AI Router, Persistence)"),
        "## 8. Six Specialized AI Agents": ("architecture/dukaandost_multi_agent_architecture.png", "Figure 2: Six-Agent LangGraph Multi-Agent Orchestration & Deterministic Financial Guardrails"),
        "## 9. LangGraph Workflow & State Persistence": ("architecture/dukaandost_langgraph_workflow.png", "Figure 3: LangGraph StateGraph Execution Lifecycle (Typed State, Nodes, Interrupt & Resume)"),
        "## 13. Failure Monitoring, Fault Isolation & Price Rectification": ("architecture/dukaandost_approval_recovery.png", "Figure 4: Safety Guardrails, Failure Isolation & Interactive Price Rectification Flow"),
        "## 20. Database Design & Relational Persistence": ("architecture/dukaandost_database_er.png", "Figure 5: Multi-Tenant Relational Database Schema & Audit Trail Structure")
    }

    is_cover_page = True

    for line in lines:
        line_str = line.strip()

        # Handle code blocks
        if line_str.startswith('```'):
            if in_code_block:
                # Flush code block
                code_text = "<br/>".join([clean_md_tags(cl) for cl in code_lines])
                code_p = Paragraph(f'<font face="Consolas" size="7.5">{code_text}</font>', body_style)
                code_tbl = Table([[code_p]], colWidths=[504])
                code_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(code_tbl)
                story.append(Spacer(1, 6))
                in_code_block = False
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(line)
            continue

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

        if line_str.startswith('---'):
            if is_cover_page:
                story.append(PageBreak())
                is_cover_page = False
            else:
                story.append(Spacer(1, 4))
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=10))
            continue

        if line_str.startswith('# '):
            continue
        elif line_str.startswith('## '):
            story.append(Paragraph(clean_md_tags(line_str[3:]), h1_style))
            # Check if this heading has an architecture diagram to insert
            for match_key, (diag_path, diag_caption) in diagram_map.items():
                if match_key in line_str and os.path.exists(diag_path):
                    story.append(Spacer(1, 6))
                    img = Image(diag_path, width=6.5*inch, height=4.2*inch)
                    story.append(KeepTogether([img, Spacer(1, 3), Paragraph(diag_caption, caption_style)]))
                    story.append(Spacer(1, 6))
                    break
        elif line_str.startswith('### '):
            story.append(Paragraph(clean_md_tags(line_str[4:]), h2_style))
        elif line_str.startswith('#### '):
            story.append(Paragraph(clean_md_tags(line_str[5:]), h3_style))
        elif line_str.startswith('- ') or line_str.startswith('* '):
            bullet_text = f"&bull; {clean_md_tags(line_str[2:])}"
            story.append(Paragraph(bullet_text, bullet_style))
        elif re.match(r'^\d+\.\s', line_str):
            clean_text = clean_md_tags(line_str)
            story.append(Paragraph(clean_text, bullet_style))
        elif line_str.startswith('$$') and line_str.endswith('$$'):
            # Mathematical display formula
            formula = line_str[2:-2].strip()
            p_math = Paragraph(f'<font face="Consolas" color="#0E7490"><b>{formula}</b></font>', body_style)
            story.append(p_math)
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
    p_style = ParagraphStyle('TableCell', fontName='Arial', fontSize=7.5, leading=10.5, textColor=colors.HexColor("#1E293B"))
    header_style = ParagraphStyle('TableHead', fontName='Arial-Bold', fontSize=8, leading=11, textColor=colors.white)

    for r_idx, row in enumerate(rows):
        row_cells = []
        for cell_text in row:
            st = header_style if r_idx == 0 else p_style
            row_cells.append(Paragraph(clean_md_tags(cell_text), st))
        table_data.append(row_cells)

    num_cols = len(rows[0])
    # Proportional column distribution
    col_widths = [504 / num_cols] * num_cols
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

if __name__ == "__main__":
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    compile_docx(content)
    compile_pdf(content)
    
    # Copy to frontend/public, workspace root, and Antigravity artifact directory
    shutil.copy(PDF_PATH, "frontend/public/DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.pdf")
    shutil.copy(PDF_PATH, "DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.pdf")
    
    artifact_target = r"C:\Users\krish\.gemini\antigravity\brain\81126b5f-b01e-4e9c-80fb-2d73dcad4b88\DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.pdf"
    try:
        shutil.copy(PDF_PATH, artifact_target)
        print("Copied PDF to Antigravity artifact directory.")
    except Exception as e:
        print(f"Artifact directory copy notice: {e}")

    print("Compilation and synchronization finished successfully.")
