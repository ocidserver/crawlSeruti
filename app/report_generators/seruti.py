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
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except Exception as e:
            raise RuntimeError(f"reportlab belum terpasang: {e}")
        out_path = os.path.join(output_dir, f"{base}.pdf")
        c = canvas.Canvas(out_path, pagesize=A4)
        width, height = A4
        y = height - 50
        lines = [
            'LAPORAN SERUTI',
            f"File sumber: {os.path.basename(batch_file_path)}",
            f"Total baris: {stats['total_rows']}",
            f"Kolom: {', '.join(stats['columns'])}",
            ''
        ]
        if per_date is not None:
            lines.append('Distribusi per data_tanggal:')
            for k, v in per_date.items():
                lines.append(f'  - {k}: {v}')
        for line in lines:
            c.drawString(40, y, line)
            y -= 18
            if y < 60:
                c.showPage(); y = height - 50
        c.save()
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
