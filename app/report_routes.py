from flask import Blueprint, render_template, request, jsonify, send_file
import os
from datetime import datetime, date, timedelta

from app.auth import login_required
from app.config import Config
from app.database import db
from app.report_generators import get_generator


report_bp = Blueprint('report', __name__, url_prefix='/report')


@report_bp.route('/')
@login_required
def index():
    # List tasks from logs
    tasks = db.get_batchable_tasks()
    # We'll compute eligibility client-side via API to avoid slow page loads
    history = db.list_report_history(limit=100)
    return render_template('report/index.html', tasks=tasks, history=history)


@report_bp.route('/eligibles')
@login_required
def eligibles():
    # Determine which tasks are fully complete based on scheduled job period
    tasks = db.get_batchable_tasks()
    eligible = []
    for t in tasks:
        name = t.get('task_name')
        job = db.get_job_by_name(name)
        if not job:
            continue
        # Compute coverage
        start = job.get('start_date')
        end = job.get('end_date')
        logs = db.get_logs_for_task(name, start, end)
        covered = set()
        for l in logs:
            d = l.get('data_tanggal') or l.get('tanggal_download')
            if not d:
                continue
            covered.add(str(d)[:10])
        try:
            sd = datetime.fromisoformat(start).date()
            ed = datetime.fromisoformat(end).date()
            days = 0
            cur = sd
            while cur <= ed:
                days += 1
                cur += timedelta(days=1)
            if days > 0 and len(covered) >= days:
                eligible.append({'task_name': name, 'start_date': start, 'end_date': end, 'days': days})
        except Exception:
            pass
    return jsonify({'success': True, 'eligible': eligible})


@report_bp.route('/run', methods=['POST'])
@login_required
def run():
    data = request.get_json(force=True)
    task_name = data.get('task_name')
    generator = (data.get('generator') or '').lower()
    output_format = (data.get('format') or 'xlsx').lower()
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not task_name or generator not in ('seruti','susenas'):
        return jsonify({'success': False, 'message': 'task_name & generator (seruti/susenas) wajib.'}), 400

    # Confirm eligibility
    job = db.get_job_by_name(task_name)
    if job and (not start_date or not end_date):
        start_date = start_date or job.get('start_date')
        end_date = end_date or job.get('end_date')

    logs = db.get_logs_for_task(task_name, start_date, end_date)
    # Use latest batch from history if available; else build a temporary batch file
    # For simplicity, re-use a recent batch if date range matches exactly
    batch_file_path = None
    for h in db.list_batch_history(limit=50):
        if h['task_name'] == task_name and h.get('start_date') == start_date and h.get('end_date') == end_date:
            if os.path.exists(h.get('file_path')):
                batch_file_path = h.get('file_path')
                break

    if not batch_file_path:
        # Create temp batch CSV from logs
        try:
            import pandas as pd
        except Exception as e:
            return jsonify({'success': False, 'message': f'Pandas diperlukan: {e}'}), 500
        from app.batch_routes import _read_table_file
        frames = []
        headers = None
        for log in logs:
            filename = log['nama_file']
            filepath = filename if os.path.isabs(filename) else os.path.join(Config.DOWNLOAD_PATH, filename)
            if not os.path.exists(filepath):
                continue
            df, err = _read_table_file(filepath)
            if err:
                continue
            if headers is None:
                headers = list(df.columns)
            else:
                for col in headers:
                    if col not in df.columns:
                        df[col] = None
                df = df[headers]
            df['data_tanggal'] = log.get('data_tanggal') or log.get('tanggal_download')
            df['source_file'] = filename
            frames.append(df)
        if not frames:
            return jsonify({'success': False, 'message': 'Tidak ada data untuk dibentuk report.'}), 404
        combined = pd.concat(frames, ignore_index=True)
        reports_dir = os.path.join(Config.DOWNLOAD_PATH, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        tmp_name = f"tmp_batch_{task_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        batch_file_path = os.path.join(reports_dir, tmp_name)
        combined.to_csv(batch_file_path, index=False, encoding='utf-8-sig')

    gen_fn = get_generator(generator)
    if not gen_fn:
        return jsonify({'success': False, 'message': 'Generator tidak ditemukan'}), 400

    reports_dir = os.path.join(Config.DOWNLOAD_PATH, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    try:
        out_path, stats = gen_fn(batch_file_path, reports_dir, output_format=output_format)
    except Exception as e:
        db.add_report_history(task_name, generator, start_date, end_date, 0, '', status='failed', note=str(e))
        return jsonify({'success': False, 'message': f'Gagal membuat report: {e}'}), 500

    rid = db.add_report_history(task_name, generator, start_date, end_date, stats.get('total_rows', 0), out_path, status='success')

    # Derive mimetype
    fname = os.path.basename(out_path).lower()
    if fname.endswith('.xlsx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif fname.endswith('.pdf'):
        mimetype = 'application/pdf'
    else:
        mimetype = 'text/plain; charset=utf-8'
    return send_file(out_path, as_attachment=True, download_name=os.path.basename(out_path), mimetype=mimetype)


@report_bp.route('/history')
@login_required
def history():
    history = db.list_report_history(limit=200)
    return render_template('report/history.html', history=history)


@report_bp.route('/history/<int:hid>/download')
@login_required
def download(hid):
    rec = db.get_report_history(hid)
    if not rec:
        return jsonify({'success': False, 'message': 'Riwayat tidak ditemukan'}), 404
    path = rec.get('file_path')
    if not path or not os.path.exists(path):
        return jsonify({'success': False, 'message': 'File tidak ditemukan'}), 404
    return send_file(path, as_attachment=True, download_name=os.path.basename(path))
