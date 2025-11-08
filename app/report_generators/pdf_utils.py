"""Shared PDF utilities for report generators.
Provides a simple API to build PDFs with a title, metadata table, optional sections/tables, and page numbers.
"""
from typing import List, Sequence, Optional
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Flowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def build_pdf(
    out_path: str,
    title_text: str,
    meta_rows: Sequence[Sequence[str]],
    sections: Optional[List[Flowable]] = None,
) -> None:
    """Build a PDF document with a title, metadata table, and optional sections.

    - out_path: output file path
    - title_text: main title displayed at the top
    - meta_rows: sequence of [key, value] rows for a metadata table
    - sections: additional Flowables (Paragraph/Table/Spacer/etc.) to append after metadata
    """
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54,
    )
    styles = getSampleStyleSheet()

    story: List[Flowable] = []
    story.append(Paragraph(f"<b>{title_text}</b>", styles['Title']))
    story.append(Spacer(1, 6))

    meta_tbl = Table(list(meta_rows), colWidths=[140, 340])
    meta_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
        ('TEXTCOLOR', (0,0), (0,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 12))

    if sections:
        story.extend(sections)

    def _add_page_number(canvas, doc_):
        canvas.saveState()
        page_num_text = f"Halaman {doc_.page}"
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(A4[0]-36, 20, page_num_text)
        canvas.restoreState()

    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)


def make_table_with_header(headers: Sequence[str], rows: Sequence[Sequence[object]], col_widths=None) -> Table:
    data = [list(headers)] + [list(map(lambda v: str(v), r)) for r in rows]
    tbl = Table(data, col_widths)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,1), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    return tbl
