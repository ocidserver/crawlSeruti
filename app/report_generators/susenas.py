"""Susenas report generator
Basic aggregated metrics placeholder.
"""
from datetime import datetime
import os
import pandas as pd
from typing import Tuple, Dict


def generate(batch_file_path: str, output_dir: str, output_format: str = 'xlsx') -> Tuple[str, Dict]:
    if not os.path.exists(batch_file_path):
        raise FileNotFoundError(batch_file_path)
    df = _read(batch_file_path)
    stats = {
        'total_rows': len(df),
        'columns': list(df.columns),
        'generated_at': datetime.now().isoformat()
    }
    # Example: distinct source_file count
    distinct_sources = df['source_file'].nunique() if 'source_file' in df.columns else None
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    base = f"report_susenas_{ts}"
    if output_format == 'xlsx':
        out_path = os.path.join(output_dir, f"{base}.xlsx")
        with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
            summary_rows = [
                ['Generated At', stats['generated_at']],
                ['Total Rows', stats['total_rows']],
                ['Columns', ', '.join(stats['columns'])],
            ]
            if distinct_sources is not None:
                summary_rows.append(['Distinct source_file', distinct_sources])
            pd.DataFrame(summary_rows, columns=['Key','Value']).to_excel(writer, index=False, sheet_name='Summary')
        return out_path, stats
    elif output_format == 'pdf':
        # Enhanced PDF layout using ReportLab Platypus (tables, headers, page numbers)
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
        except Exception as e:
            raise RuntimeError(f"reportlab belum terpasang: {e}")

        out_path = os.path.join(output_dir, f"{base}.pdf")

        doc = SimpleDocTemplate(
            out_path,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=54,
            bottomMargin=54,
        )
        styles = getSampleStyleSheet()
        story = []

        title = Paragraph("<b>LAPORAN SUSENAS</b>", styles['Title'])
        meta = [
            ["File sumber", os.path.basename(batch_file_path)],
            ["Generated At", stats['generated_at']],
            ["Total baris", stats['total_rows']],
            ["Kolom", ', '.join(stats['columns'])],
        ]
        if distinct_sources is not None:
            meta.append(["Distinct source_file", str(distinct_sources)])

        story.append(title)
        story.append(Spacer(1, 6))

        meta_tbl = Table(meta, colWidths=[140, 340])
        meta_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ('TEXTCOLOR', (0,0), (0,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(meta_tbl)

        def _add_page_number(canvas, doc_):
            canvas.saveState()
            page_num_text = f"Halaman {doc_.page}"
            canvas.setFont('Helvetica', 8)
            canvas.drawRightString(A4[0]-36, 20, page_num_text)
            canvas.restoreState()

        doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
        return out_path, stats
    else:
        out_path = os.path.join(output_dir, f"{base}.txt")
        report_lines = [
            'LAPORAN SUSENAS',
            f'File sumber: {os.path.basename(batch_file_path)}',
            f"Total baris: {stats['total_rows']}",
            f"Kolom: {', '.join(stats['columns'])}",
        ]
        if distinct_sources is not None:
            report_lines.append(f'Distinct source_file: {distinct_sources}')
        txt = '\n'.join(report_lines)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(txt)
        return out_path, stats


def _read(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.csv':
        return pd.read_csv(path)
    return pd.read_excel(path)
