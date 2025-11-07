"""Susenas report generator
Basic aggregated metrics placeholder.
"""
from datetime import datetime
import os
import pandas as pd


def generate(batch_file_path: str, output_dir: str):
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
    report_lines = [
        'LAPORAN SUSENAS',
        f'File sumber: {os.path.basename(batch_file_path)}',
        f"Total baris: {stats['total_rows']}",
        f"Kolom: {', '.join(stats['columns'])}",
        ''
    ]
    if distinct_sources is not None:
        report_lines.append(f'Distinct source_file: {distinct_sources}')
    txt = '\n'.join(report_lines)
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"report_susenas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(txt)
    return out_path, stats


def _read(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.csv':
        return pd.read_csv(path)
    return pd.read_excel(path)
