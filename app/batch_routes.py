"""
Batching routes for combining logs' downloaded files into a single dataset
"""
from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for
from io import BytesIO
import os
from datetime import datetime

from app.database import db
from app.config import Config
from app.auth import login_required

batch_bp = Blueprint('batch', __name__, url_prefix='/batch')


def _read_table_file(filepath):
    """Read CSV/XLSX/XLS into a pandas DataFrame; returns (df, error)"""
    try:
        import pandas as pd
    except Exception as e:
        return None, f"Pandas tidak terinstall: {e}. Tambahkan ke requirements dan install."

    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == '.csv':
            df = pd.read_csv(filepath)
        elif ext in ('.xlsx', '.xlsm', '.xltx', '.xltm', '.xls'):
            # Prefer openpyxl for xlsx
            engine = 'openpyxl' if ext != '.xls' else None
            df = pd.read_excel(filepath, engine=engine)
        else:
            return None, f"Format file tidak didukung: {ext} ({os.path.basename(filepath)})"
        return df, None
    except Exception as e:
        return None, f"Gagal membaca file {os.path.basename(filepath)}: {e}"


@batch_bp.route('/')
@login_required
def index():
    tasks = db.get_batchable_tasks()
    return render_template('batch/index.html', tasks=tasks)


@batch_bp.route('/tasks', methods=['GET'])
@login_required
def list_tasks():
    tasks = db.get_batchable_tasks()
    return jsonify({'success': True, 'tasks': tasks})


@batch_bp.route('/run', methods=['POST'])
@login_required
def run_batch():
    payload = request.get_json(force=True)
    task_name = payload.get('task_name')
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    output_format = (payload.get('format') or 'csv').lower()
    preview = bool(payload.get('preview', False))

    if not task_name:
        return jsonify({'success': False, 'message': 'task_name wajib diisi'}), 400

    logs = db.get_logs_for_task(task_name, start_date, end_date)
    if not logs:
        return jsonify({'success': False, 'message': 'Tidak ada log untuk kriteria ini'}), 404

    # Load and merge
    try:
        import pandas as pd
    except Exception as e:
        return jsonify({'success': False, 'message': f"Pandas diperlukan: {e}"}), 500

    frames = []
    headers = None
    for log in logs:
        filename = log['nama_file']
        filepath = filename
        if not os.path.isabs(filepath):
            filepath = os.path.join(Config.DOWNLOAD_PATH, filename)
        if not os.path.exists(filepath):
            # Skip missing files but record note
            continue

        df, err = _read_table_file(filepath)
        if err:
            # Skip problematic files but keep note
            continue

        # Normalize headers to first file's headers
        if headers is None:
            headers = list(df.columns)
        else:
            # Align columns; add missing, drop extras
            for col in headers:
                if col not in df.columns:
                    df[col] = None
            df = df[headers]

        # Add data_tanggal column from log
        df['data_tanggal'] = log.get('data_tanggal') or log.get('tanggal_download')
        # Also add source file if helpful
        df['source_file'] = filename

        frames.append(df)

    if not frames:
        return jsonify({'success': False, 'message': 'Semua file hilang/invalid untuk log yang dipilih'}), 404

    combined = pd.concat(frames, ignore_index=True)

    if preview:
        sample = combined.head(50)
        return jsonify({
            'success': True,
            'columns': list(sample.columns),
            'rows': sample.astype(str).values.tolist(),
            'total_rows': int(len(combined))
        })

    # Ensure batches directory exists under downloads
    batches_dir = os.path.join(Config.DOWNLOAD_PATH, 'batches')
    os.makedirs(batches_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_task = ''.join(c for c in task_name if c.isalnum() or c in ('-','_')).strip('_') or 'task'
    
    if output_format == 'xlsx':
        filename = f"batch_{safe_task}_{timestamp}.xlsx"
        out_path = os.path.join(batches_dir, filename)
        with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
            combined.to_excel(writer, index=False, sheet_name='BatchLog')
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        # default CSV
        filename = f"batch_{safe_task}_{timestamp}.csv"
        out_path = os.path.join(batches_dir, filename)
        combined.to_csv(out_path, index=False, encoding='utf-8-sig')
        mimetype = 'text/csv; charset=utf-8'

    # Record batch history
    hist_id = db.add_batch_history(
        task_name=task_name,
        start_date=start_date,
        end_date=end_date,
        output_format=output_format,
        total_rows=len(combined),
        columns=list(combined.columns),
        file_path=out_path,
        status='success'
    )

    # Return file for download
    return send_file(out_path, as_attachment=True, download_name=filename, mimetype=mimetype)


@batch_bp.route('/history')
@login_required
def history():
    records = db.list_batch_history(limit=200)
    return render_template('batch/history.html', records=records)


@batch_bp.route('/history/<int:history_id>/download')
@login_required
def download_history(history_id):
    rec = db.get_batch_history(history_id)
    if not rec:
        return jsonify({'success': False, 'message': 'Riwayat tidak ditemukan'}), 404
    path = rec.get('file_path')
    if not path or not os.path.exists(path):
        return jsonify({'success': False, 'message': 'File tidak ditemukan'}), 404
    filename = os.path.basename(path)
    # Simple mimetype heuristic
    if filename.lower().endswith('.xlsx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        mimetype = 'text/csv; charset=utf-8'
    return send_file(path, as_attachment=True, download_name=filename, mimetype=mimetype)
