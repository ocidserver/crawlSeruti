"""Seruti report generator
Builds a simple aggregated analysis from batch data (CSV/XLSX)
"""
from datetime import datetime
import os
import pandas as pd


def generate(batch_file_path: str, output_dir: str):
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
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"report_seruti_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(txt)
    return out_path, stats


def _read(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.csv':
        return pd.read_csv(path)
    return pd.read_excel(path)
