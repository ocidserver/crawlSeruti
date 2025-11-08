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
- Eligible tasks: full coverage (semua hari dalam rentang tersedia di download log). Tombol cepat muncul di dashboard.
- Pilih task + generator:
  - Seruti
  - Susenas
- Format output yang didukung:
  - Excel (.xlsx): Sheet Summary + optional sheet distribusi tanggal
  - PDF (.pdf): Layout dengan judul, tabel metadata, halaman bernomor, dan (Seruti) tabel distribusi `data_tanggal` jika ada
  - Text (.txt): Ringkas (fallback)

Semua file disimpan di `downloads/reports/` dan direkam di `report_history`.

Dependensi PDF: `reportlab` (sudah ada di `requirements.txt`). Jika PDF kosong cek:
1. Data batch tidak kosong
2. Kolom tanggal ada (untuk tabel distribusi)
3. Virtualenv aktif & reportlab terpasang

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

- `ModuleNotFoundError: app` → jalankan perintah dari root project & aktivasi virtualenv.
- Coverage `null` → tanggal tidak cocok dengan rentang job (cek start/end job).
- Report tidak eligible → log harian belum lengkap (seed ulang / pastikan crawler berjalan setiap hari).
