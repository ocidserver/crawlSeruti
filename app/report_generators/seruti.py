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
        # Enhanced PDF layout using shared utility
        try:
            from .pdf_utils import build_pdf, make_table_with_header
        except Exception as e:
            raise RuntimeError(f"reportlab utils missing or not installed: {e}")

        out_path = os.path.join(output_dir, f"{base}.pdf")
        meta = [
            ["File sumber", os.path.basename(batch_file_path)],
            ["Generated At", stats['generated_at']],
            ["Total baris", stats['total_rows']],
            ["Kolom", ', '.join(stats['columns'])],
        ]
        sections = []
        if per_date is not None:
            # Build a section table for date distribution
            headers = ["data_tanggal", "count"]
            rows = [(k, int(v)) for k, v in per_date.items()]
            sections.append(make_table_with_header(headers, rows, col_widths=[200, 80]))
        build_pdf(out_path, "LAPORAN SERUTI", meta, sections)
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
        # Try to parse common date column if present
        try:
            return pd.read_csv(path, parse_dates=['data_tanggal'])
        except Exception:
            return pd.read_csv(path)
    # Excel fallback
    try:
        return pd.read_excel(path, engine='openpyxl', parse_dates=['data_tanggal'])
    except Exception:
        return pd.read_excel(path, engine='openpyxl')
