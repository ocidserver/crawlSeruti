"""Seruti report generator
Builds a simple aggregated analysis from batch data (CSV/XLSX)
"""
from datetime import datetime
import os
import pandas as pd
from typing import Tuple, Dict


def generate(batch_file_path: str, output_dir: str, output_format: str = 'xlsx') -> Tuple[str, Dict]:
    if not os.path.exists(batch_file_path):
        raise FileNotFoundError(batch_file_path)
    df = _read(batch_file_path)
    # Basic stats example (customize later)
    stats = {
        'total_rows': len(df),
        'columns': list(df.columns),
        'generated_at': datetime.now().isoformat()
    }
    # Example: count by data_tanggal
    if 'data_tanggal' in df.columns:
        per_date = df['data_tanggal'].value_counts().sort_index()
    else:
        per_date = None
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    base = f"report_seruti_{ts}"

    if output_format == 'xlsx':
        out_path = os.path.join(output_dir, f"{base}.xlsx")
        with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_rows = [
                ['Generated At', stats['generated_at']],
                ['Total Rows', stats['total_rows']],
                ['Columns', ', '.join(stats['columns'])],
            ]
            pd.DataFrame(summary_rows, columns=['Key','Value']).to_excel(writer, index=False, sheet_name='Summary')
            # Per-date distribution if available
            if per_date is not None:
                pd.DataFrame({'data_tanggal': per_date.index, 'count': per_date.values}).to_excel(writer, index=False, sheet_name='PerDate')
        return out_path, stats
    elif output_format == 'pdf':
        # Enhanced PDF layout using ReportLab Platypus (tables, headers, page numbers)
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
        except Exception as e:
            raise RuntimeError(f"reportlab belum terpasang: {e}")

        out_path = os.path.join(output_dir, f"{base}.pdf")

        # Document setup
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

        # Header
        title = Paragraph("<b>LAPORAN SERUTI</b>", styles['Title'])
        meta = [
            ["File sumber", os.path.basename(batch_file_path)],
            ["Generated At", stats['generated_at']],
            ["Total baris", stats['total_rows']],
            ["Kolom", ', '.join(stats['columns'])],
        ]
        story.append(title)
        story.append(Spacer(1, 6))

        meta_tbl = Table(meta, colWidths=[120, 360])
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

        # Per-date distribution
        if per_date is not None:
            story.append(Paragraph("<b>Distribusi per data_tanggal</b>", styles['Heading3']))
            data = [["data_tanggal", "count"]]
            for k, v in per_date.items():
                data.append([str(k), int(v)])
            tbl = Table(data, colWidths=[200, 80])
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
            ]))
            story.append(tbl)

        # Footer with page numbers
        def _add_page_number(canvas, doc_):
            canvas.saveState()
            page_num_text = f"Halaman {doc_.page}"
            canvas.setFont('Helvetica', 8)
            canvas.drawRightString(A4[0]-36, 20, page_num_text)
            canvas.restoreState()

        doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
        return out_path, stats
    else:
        # fallback to txt
        out_path = os.path.join(output_dir, f"{base}.txt")
        report_lines = [
            'LAPORAN SERUTI',
            f'File sumber: {os.path.basename(batch_file_path)}',
            f"Total baris: {stats['total_rows']}",
            f"Kolom: {', '.join(stats['columns'])}",
            ''
        ]
        if per_date is not None:
            report_lines.append('Distribusi per data_tanggal:')
            for k, v in per_date.items():
                report_lines.append(f'  - {k}: {v}')
        txt = '\n'.join(report_lines)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(txt)
        return out_path, stats


def _read(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.csv':
        return pd.read_csv(path)
    return pd.read_excel(path)
