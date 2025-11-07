from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
import os

from app.database import db
from app.auth import login_required


dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def _date_str(d):
    if isinstance(d, datetime):
        return d.strftime('%Y-%m-%d')
    return str(d)


def _daterange(start_date, end_date):
    cur = start_date
    while cur <= end_date:
        yield cur
        cur += timedelta(days=1)


@dashboard_bp.route('/')
@login_required
def index():
    active_jobs = db.get_active_jobs()
    tasks = db.get_batchable_tasks()
    return render_template('dashboard/index.html', active_jobs=active_jobs, tasks=tasks)


@dashboard_bp.route('/api/metrics')
@login_required
def metrics():
    task = request.args.get('task')
    start = request.args.get('start_date')
    end = request.args.get('end_date')

    if not task:
        return jsonify({'success': False, 'message': 'Parameter task wajib.'}), 400

    job = db.get_job_by_name(task)
    if not start and job:
        start = job.get('start_date')
    if not end and job:
        end = job.get('end_date')

    logs = db.get_logs_for_task(task, start, end)
    total_logs = len(logs)

    # Build per-day counts and coverage set
    per_day = defaultdict(int)
    covered = set()
    last_download_at = None
    first_data_date = None
    last_data_date = None

    for l in logs:
        d = l.get('data_tanggal') or l.get('tanggal_download')
        try:
            day = datetime.fromisoformat(d).date()
        except Exception:
            try:
                day = datetime.strptime(d, '%Y-%m-%d').date()
            except Exception:
                continue
        per_day[_date_str(day)] += 1
        covered.add(_date_str(day))
        # last download timestamp
        tdl = l.get('tanggal_download')
        try:
            ts = datetime.fromisoformat(tdl)
        except Exception:
            try:
                ts = datetime.strptime(tdl, '%Y-%m-%d %H:%M:%S')
            except Exception:
                ts = None
        if ts and (last_download_at is None or ts > last_download_at):
            last_download_at = ts
        # data range
        if first_data_date is None or _date_str(day) < first_data_date:
            first_data_date = _date_str(day)
        if last_data_date is None or _date_str(day) > last_data_date:
            last_data_date = _date_str(day)

    # Expected range from job if provided
    expected_days = []
    missing = []
    coverage_pct = None
    if start and end:
        try:
            sd = datetime.fromisoformat(start).date()
            ed = datetime.fromisoformat(end).date()
            expected_days = [_date_str(d) for d in _daterange(sd, ed)]
            missing = [d for d in expected_days if d not in covered]
            if expected_days:
                coverage_pct = round(100.0 * (len(expected_days) - len(missing)) / len(expected_days), 2)
        except Exception:
            expected_days = []

    series = sorted([{ 'date': k, 'count': v } for k, v in per_day.items()], key=lambda x: x['date'])

    return jsonify({
        'success': True,
        'task': task,
        'total_logs': total_logs,
        'first_data_date': first_data_date,
        'last_data_date': last_data_date,
        'last_download_at': last_download_at.isoformat() if last_download_at else None,
        'coverage_pct': coverage_pct,
        'expected_days': len(expected_days),
        'missing_dates': missing[:50],
        'timeseries': series
    })
