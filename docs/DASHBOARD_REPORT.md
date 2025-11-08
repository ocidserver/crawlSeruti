# Live Dashboard & Report Generation

This guide covers the live dashboard (metrics & chart) and the final report generation based on batched logs.

## Live Dashboard

- URL: /dashboard
- Select a task (from download logs). Optionally set start/end dates.
- Metrics shown:
  - Total logs
  - Coverage % (days covered vs. expected)
  - Range data (first/last data date)
  - Last download timestamp
- A daily activity chart (downloads per day) is displayed.
- Extra metrics: average/min/max file size and total download duration (span) across selected range.
- Auto-refresh every 60 seconds.

API endpoint: `/dashboard/api/metrics?task=<TASK>&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

## Batching

- URL: /batch/
- Choose a task and date range, preview up to 50 rows, then download CSV/XLSX.
- Output stored under `downloads/batches/` and recorded in `batch_history`.

## Report Generation

- URL: /report/
- Eligible tasks are tasks with full coverage for their scheduled period.
- Choose a task and generator:
  - Seruti generator
  - Susenas generator
- Output formats:
  - Excel (.xlsx) [default]
  - PDF (.pdf)
  - Text (.txt)
    Saved under `downloads/reports/` and recorded in `report_history`.
    Note: PDF requires dependency `reportlab` (included in requirements.txt).

From Dashboard, if the task is eligible (full coverage), a “Generate Report” button appears for quick generation.

## Smoke Testing

1. Activate environment & seed synthetic data (7 days of logs for `SMOKE_SERUTI`):

```powershell
.venv\Scripts\python.exe scripts\smoke_seed.py
```

2. Run smoke test (unittest):

```powershell
.venv\Scripts\python.exe tests\test_dashboard_report_smoke.py
```

Expected:

- Dashboard metrics: `success=True`, `total_logs >= 7`, coverage percent not null.
- Report generation returns HTTP 200 with `Content-Disposition` containing `report_seruti_`.
- Report history page loads (status 200).

Artifacts created:

- Batch files (if manually run) in `downloads/batches/`
- Report files in `downloads/reports/`
- History records in tables `batch_history` and `report_history`.

Troubleshooting:

- If `ModuleNotFoundError: app`, ensure script is run from project root and virtualenv is activated.
- If coverage is `null`, verify date range parameters match the scheduled job period.
- If report not eligible, confirm seeded logs match every day in job range (run seed again).
