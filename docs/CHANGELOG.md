# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-11-07

### 🎉 Major Release - Job History, Download Log, UI Table, SQLite Migration

### Added

- **SQLite Database** - Migrated from JSON files to SQLite for better data integrity
  - `crawler.db` with `scheduled_jobs` and `download_logs` tables
  - ACID-compliant transactions
  - Automatic migration from existing JSON files
  - 10-60x performance improvement
- **Job History System**
  - Jobs tidak hilang setelah cancel/complete
  - Status tracking: active, success, failed, retrying, cancelled, completed
  - Archive inactive jobs instead of deleting
  - Complete audit trail
- **Enhanced Download Log**
  - Added `task_name` field to track manual vs scheduled downloads
  - Badge UI untuk visual distinction (Manual vs Scheduled)
  - Integration dengan job scheduler
- **Table UI Format**
  - Changed job list from card format to table format
  - 9 columns: Nama Job, Crawler, Status, Periode, Waktu, Next Run, Last Run, Message, Action
  - More compact and professional appearance
  - Better data scanning and comparison
- **Database Manager (`app/database.py`)**
  - Context manager untuk safe connections
  - CRUD operations untuk jobs dan logs
  - Automatic migration from JSON
  - Indexed queries for performance

### Changed

- **app/scheduler.py**
  - Replace JSON file operations with database calls
  - Job cancellation marks as cancelled instead of deleting
  - Get all jobs includes inactive jobs
  - Auto-migrate on first run
- **app/download_log.py**
  - Now wrapper around database operations
  - Backward compatible API
  - Support for task_name parameter
- **app/crawlers/base_crawler.py**
  - Added `task_name` parameter to constructor
  - Pass task name to download logger
- **app/templates/index.html**
  - Job list from card grid to table format
  - Enhanced download log table with icons
  - Better responsive design
- **app/routes.py**
  - `/api/downloads` now returns data from database
  - Includes task_name in response

### Fixed

- Job data loss saat system crash (now ACID-compliant)
- Performance issues dengan large JSON files
- File locking issues pada concurrent access
- Data corruption saat unexpected shutdown

### Performance

- Add job: 15-20ms → 1-2ms (10x faster)
- Update job: 15-20ms → 1-2ms (10x faster)
- Check duplicate: 30-50ms → 0.5ms (60x faster)
- Get logs (100): 15ms → 1ms (15x faster)

### Migration

- Automatic migration from `scheduler_jobs.json` to SQLite
- Automatic migration from `download_log.json` to SQLite
- Backup original JSON files as `.json.backup`
- Zero downtime migration

---

## [2.1.0] - 2025-11-08

### 📊 Dashboard & Reporting Enhancements

### Added

- **Extended Dashboard Metrics**: average/min/max file size & total download duration span.
- **Report Generation Modal**: Quick generate from dashboard if coverage penuh.
- **Multi-Format Reports**: Generators (Seruti & Susenas) now output XLSX / PDF / TXT.
- **Enhanced PDF Layout**: ReportLab Platypus (styled metadata table, page numbers, Seruti date distribution table).
- **Shared PDF Utilities**: `app/report_generators/pdf_utils.py` deduplicates layout code.

### Changed

- **Seruti & Susenas Generators**: Refactored PDF branch to use shared utilities; XLSX still includes Summary (+ PerDate sheet for Seruti when available).
- **README / Docs**: Updated with multi-format report info, dashboard modal, PDF troubleshooting.

### Fixed / Robustness

- Graceful date parsing for Seruti (`data_tanggal`) when available.
- Consistent Excel engine usage (`openpyxl`).

### Notes

- If PDF table tidak muncul, cek kolom sumber (Seruti: `data_tanggal`).
- Future: error rate metric & async report jobs.

---

## [1.5.0] - 2025-11-06

### 🚀 Susenas Crawler Implementation

### Added

- **Susenas Crawler** - Complete implementation
  - 7 progress reports download
  - SSO authentication via BPS
  - Batch file detection
  - Smart validation (skip duplicates)
- **Reports Supported:**

  1. Laporan Pencacahan
  2. Laporan Pemeriksaan (Edcod)
  3. Laporan Pengiriman ke Kabkot
  4. Laporan Penerimaan di Kabkot
  5. Laporan Penerimaan di IPDS
  6. Laporan Pengolahan Dokumen M
  7. Laporan Pengolahan Dokumen KP

- **Multi-Crawler Architecture**
  - Abstract `BaseCrawler` class
  - Factory pattern dengan `get_crawler()`
  - Registry system untuk crawler types
  - Shared utilities dan template methods

### Changed

- **Scheduler** - Support multiple crawler types
  - `crawler_type` parameter in job config
  - UI crawler selection (SERUTI/SUSENAS)
  - Validation untuk crawler type
- **Download Detection** - Batch mode
  - Check files after all downloads complete
  - 5-minute time window
  - Filter temporary files (.crdownload, .tmp, .part)

### Performance

- Susenas: ~40 seconds for 7 files (headless mode)
- Smart validation: 29.29 seconds (skip download)
- Success rate: 100% (7/7 files)

---

## [1.4.0] - 2025-11-05

### 🔒 SSO Authentication & Performance Optimization

### Added

- **SSO Support** - BPS SSO integration
  - Auto-redirect handling
  - Session management
  - Cookie persistence
- **Smart Download Detection**

  - Check existing data by date
  - Skip duplicate downloads
  - Validation before download

- **Download Log System**
  - JSON-based logging
  - Fields: nama_file, tanggal_download, laman_web, data_tanggal
  - Duplicate checking
  - History tracking

### Changed

- **ChromeDriver Management**
  - Fixed path detection (win32/win64)
  - Auto-download compatible version
  - Cache cleaning mechanism
- **Performance Optimization**
  - Seruti: 64.87s → 57.43s (11.5% improvement)
  - Headless mode optimization
  - Reduced wait times
  - Efficient element detection

### Fixed

- ChromeDriver WinError 193 (architecture mismatch)
- Download detection false negatives
- File detection timing issues
- SSO redirect loops

---

## [1.3.0] - 2025-11-03

### 📅 Task Scheduler Implementation

### Added

- **APScheduler Integration**
  - Cron-like scheduling
  - Date range support (start_date, end_date)
  - Configurable execution time (hour, minute)
- **Retry Mechanism**
  - Max retries configuration
  - Retry delay setting
  - Exponential backoff
  - Status tracking
- **Job Management**
  - Add scheduled jobs
  - Remove/cancel jobs
  - List all jobs
  - Job details view
- **Unified Web Interface**
  - Scheduler UI in main dashboard
  - Job list with status
  - Real-time monitoring
  - Manual trigger option

### Changed

- **Routes Structure**
  - `/api/scheduler/job/add` - Add new job
  - `/api/scheduler/job/<id>` - Delete job
  - `/api/scheduler/jobs` - List all jobs
- **Configuration**
  - Job config stored in `scheduler_jobs.json`
  - Persistent across restarts
  - Auto-reload on startup

---

## [1.2.0] - 2025-11-01

### 🎨 UI Improvements & Dashboard

### Added

- **Modern Web Dashboard**
  - Bootstrap 5 design
  - Gradient theme (purple)
  - Responsive layout
  - Card-based UI
- **Download Manager**
  - List downloaded files
  - File size information
  - Download timestamps
  - File type icons
- **Real-time Status**
  - Job status indicators
  - Success/failure messages
  - Progress tracking
  - Last run information

### Changed

- Template layout improvements
- Better mobile responsiveness
- Enhanced user experience
- Clearer error messages

---

## [1.1.0] - 2025-10-28

### ⚡ Headless Mode & Automation

### Added

- **Headless Browser Mode**
  - Chrome headless support
  - Background execution
  - No GUI required
  - Server-friendly
- **Batch Scripts**
  - `start_crawler.bat` - Quick start
  - `run_auto_crawl.bat` - Auto mode
  - Windows Task Scheduler ready
- **Configuration Options**
  - `HEADLESS_MODE` environment variable
  - Flexible browser options
  - Download path configuration

### Fixed

- Browser crash on server environments
- Download path issues
- Permission errors

---

## [1.0.0] - 2025-10-20

### 🎊 Initial Release

### Added

- **Core Features**
  - Selenium WebDriver integration
  - Flask web framework
  - Auto login functionality
  - File download automation
- **Seruti Crawler**
  - Login to olah.web.bps.go.id
  - Navigate to Progres page
  - Select Triwulan
  - Download Excel file
- **Configuration**
  - Environment variables (.env)
  - Configurable selectors
  - Target URL settings
- **Basic UI**
  - Simple web interface
  - Manual crawl trigger
  - Status display
- **Documentation**
  - README with setup instructions
  - Environment configuration guide
  - Usage examples

### Technical

- Python 3.8+
- Flask 3.0.0
- Selenium 4.15.2
- webdriver-manager 4.0.1
- APScheduler 3.10.4

---

## Version History Summary

| Version | Date       | Description                                 |
| ------- | ---------- | ------------------------------------------- |
| 2.0.0   | 2025-11-07 | SQLite migration, job history, table UI     |
| 1.5.0   | 2025-11-06 | Susenas crawler, multi-crawler architecture |
| 1.4.0   | 2025-11-05 | SSO support, performance optimization       |
| 1.3.0   | 2025-11-03 | Task scheduler implementation               |
| 1.2.0   | 2025-11-01 | UI improvements, dashboard                  |
| 1.1.0   | 2025-10-28 | Headless mode, automation                   |
| 1.0.0   | 2025-10-20 | Initial release                             |

---

## Upgrade Guide

### From 1.x to 2.0

**Automatic Migration:**

1. Backup existing data (optional):

   ```bash
   cp scheduler_jobs.json scheduler_jobs.json.manual_backup
   cp download_log.json download_log.json.manual_backup
   ```

2. Update code:

   ```bash
   git pull origin master
   ```

3. Install dependencies:

   ```bash
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. Start server (auto-migration):

   ```bash
   .venv\Scripts\python.exe run.py
   ```

5. Verify:
   - Check console for migration logs
   - JSON files should be renamed to `.backup`
   - Database `crawler.db` should be created
   - All jobs and logs should be migrated

**Manual Migration (if needed):**

```python
from app.database import db

# Force migration
jobs, logs = db.migrate_from_json(
    jobs_json='scheduler_jobs.json',
    logs_json='download_log.json'
)

print(f"Migrated: {jobs} jobs, {logs} logs")
```

---

## Breaking Changes

### Version 2.0.0

- ❌ JSON files no longer used for storage
- ❌ Direct manipulation of `scheduler_jobs.json` won't work
- ✅ All operations now through database API
- ✅ Backward compatible API (no code changes needed)

### Version 1.5.0

- ❌ Single crawler architecture removed
- ✅ Must specify `crawler_type` when adding jobs
- ✅ UI requires crawler selection

---

## Known Issues

### Version 2.0.0

- None reported

### Version 1.5.0

- Batch download may show warnings (non-critical)
- ChromeDriver cache issues on some systems (use fix script)

---

## Future Roadmap

### Version 2.1.0 (Planned)

- [ ] WAL mode for SQLite
- [ ] Connection pooling
- [ ] Full-text search
- [ ] Statistics dashboard
- [ ] Email notifications

### Version 2.2.0 (Planned)

- [ ] REST API documentation (Swagger)
- [ ] Docker support
- [ ] User authentication
- [ ] Role-based access control

### Version 3.0.0 (Planned)

- [ ] Distributed crawler support
- [ ] Queue-based job system
- [ ] Advanced scheduling (cron expressions)
- [ ] Plugin architecture

---

**Note:** Versions follow [Semantic Versioning](https://semver.org/):

- MAJOR version: incompatible API changes
- MINOR version: backward-compatible new features
- PATCH version: backward-compatible bug fixes
