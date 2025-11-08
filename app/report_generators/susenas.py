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
        # Enhanced PDF layout using shared utility
        try:
            from .pdf_utils import build_pdf
        except Exception as e:
            raise RuntimeError(f"reportlab utils missing or not installed: {e}")

        out_path = os.path.join(output_dir, f"{base}.pdf")
        meta = [
            ["File sumber", os.path.basename(batch_file_path)],
            ["Generated At", stats['generated_at']],
            ["Total baris", stats['total_rows']],
            ["Kolom", ', '.join(stats['columns'])],
        ]
        if distinct_sources is not None:
            meta.append(["Distinct source_file", str(distinct_sources)])

        build_pdf(out_path, "LAPORAN SUSENAS", meta, sections=None)
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
    # Excel: prefer openpyxl engine for .xlsx
    try:
        return pd.read_excel(path, engine='openpyxl')
    except Exception:
        return pd.read_excel(path)
