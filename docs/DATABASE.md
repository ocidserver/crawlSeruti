# Database Documentation

SQLite database schema and query guide for BPS Web Crawler System.

---

## Overview

**Database File:** `crawler.db`  
**Engine:** SQLite 3  
**ACID Compliance:** ✅ Yes  
**Transactions:** ✅ Supported  
**Indexes:** ✅ Optimized

---

## Tables

### 1. scheduled_jobs

Stores all scheduled crawler jobs (active and historical).

#### Schema

```sql
CREATE TABLE scheduled_jobs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    crawler_type TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    hour INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    max_retries INTEGER DEFAULT 3,
    retry_delay INTEGER DEFAULT 300,
    status TEXT DEFAULT 'active',
    created_at TEXT NOT NULL,
    last_run TEXT,
    last_message TEXT
);
```

#### Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique job ID (format: job_YYYYMMDDHHmmss) |
| name | TEXT | NOT NULL | Human-readable job name |
| crawler_type | TEXT | NOT NULL | Crawler type: 'seruti' or 'susenas' |
| start_date | TEXT | NOT NULL | Job start date (YYYY-MM-DD) |
| end_date | TEXT | NOT NULL | Job end date (YYYY-MM-DD) |
| hour | INTEGER | NOT NULL | Execution hour (0-23) |
| minute | INTEGER | NOT NULL | Execution minute (0-59) |
| max_retries | INTEGER | DEFAULT 3 | Maximum retry attempts |
| retry_delay | INTEGER | DEFAULT 300 | Delay between retries (seconds) |
| status | TEXT | DEFAULT 'active' | Job status (see statuses below) |
| created_at | TEXT | NOT NULL | Job creation timestamp |
| last_run | TEXT | NULL | Last execution timestamp |
| last_message | TEXT | NULL | Last execution message |

#### Status Values

| Status | Description |
|--------|-------------|
| active | Job is scheduled and running |
| success | Last run was successful |
| skipped | Last run was skipped (data exists) |
| failed | Job failed after max retries |
| retrying | Job is currently retrying |
| cancelled | Job was cancelled by user |
| completed | Job period has ended |

#### Indexes

```sql
CREATE INDEX idx_jobs_status ON scheduled_jobs(status);
```

#### Example Queries

**Get all active jobs:**
```sql
SELECT * FROM scheduled_jobs 
WHERE status = 'active' 
ORDER BY created_at DESC;
```

**Get jobs by crawler type:**
```sql
SELECT * FROM scheduled_jobs 
WHERE crawler_type = 'seruti' 
ORDER BY hour, minute;
```

**Get failed jobs:**
```sql
SELECT id, name, last_message 
FROM scheduled_jobs 
WHERE status = 'failed';
```

**Count jobs by status:**
```sql
SELECT status, COUNT(*) as count 
FROM scheduled_jobs 
GROUP BY status;
```

---

### 2. download_logs

Stores complete download history with task tracking.

#### Schema

```sql
CREATE TABLE download_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_file TEXT NOT NULL,
    tanggal_download TEXT NOT NULL,
    laman_web TEXT NOT NULL,
    data_tanggal TEXT,
    task_name TEXT DEFAULT 'Manual',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTO | Unique log ID |
| nama_file | TEXT | NOT NULL | Downloaded file name |
| tanggal_download | TEXT | NOT NULL | Download timestamp (YYYY-MM-DD HH:MM:SS) |
| laman_web | TEXT | NOT NULL | Crawler source (SerutiCrawler/SusenasCrawler) |
| data_tanggal | TEXT | NULL | Date of data in file (YYYY-MM-DD) |
| task_name | TEXT | DEFAULT 'Manual' | Task name or 'Manual' |
| created_at | TEXT | DEFAULT NOW | Record creation timestamp |

#### Indexes

```sql
CREATE INDEX idx_logs_laman ON download_logs(laman_web, data_tanggal);
CREATE INDEX idx_logs_date ON download_logs(tanggal_download);
```

#### Example Queries

**Get recent downloads:**
```sql
SELECT * FROM download_logs 
ORDER BY tanggal_download DESC 
LIMIT 10;
```

**Check if data exists:**
```sql
SELECT COUNT(*) as exists 
FROM download_logs 
WHERE laman_web = 'SerutiCrawler' 
  AND data_tanggal = '2025-11-07';
```

**Get downloads by task:**
```sql
SELECT * FROM download_logs 
WHERE task_name = 'Daily Seruti Crawl' 
ORDER BY tanggal_download DESC;
```

**Get download statistics:**
```sql
SELECT 
    laman_web,
    COUNT(*) as total_downloads,
    MAX(tanggal_download) as last_download
FROM download_logs 
GROUP BY laman_web;
```

**Get downloads by date range:**
```sql
SELECT * FROM download_logs 
WHERE tanggal_download BETWEEN '2025-11-01' AND '2025-11-30'
ORDER BY tanggal_download DESC;
```

**Manual vs Scheduled downloads:**
```sql
SELECT 
    CASE WHEN task_name = 'Manual' THEN 'Manual' ELSE 'Scheduled' END as type,
    COUNT(*) as count
FROM download_logs 
GROUP BY type;
```

---

## Common Operations

### Insert New Job

```python
from app.database import db

job_data = {
    'id': 'job_20251108120000',
    'name': 'Daily Crawl',
    'crawler_type': 'seruti',
    'start_date': '2025-11-08',
    'end_date': '2025-12-31',
    'hour': 8,
    'minute': 0,
    'max_retries': 3,
    'retry_delay': 300,
    'status': 'active',
    'created_at': '2025-11-07 12:00:00'
}

db.add_job(job_data)
```

### Update Job Status

```python
from app.database import db

db.update_job_status(
    job_id='job_20251108120000',
    status='success',
    message='Downloaded successfully',
    last_run='2025-11-08 08:00:00'
)
```

### Add Download Log

```python
from app.database import db

log_id = db.add_download_log(
    nama_file='Progres_Triwulan_3_2025.xlsx',
    tanggal_download='2025-11-08 08:05:00',
    laman_web='SerutiCrawler',
    data_tanggal='2025-11-08',
    task_name='Daily Crawl'
)
```

### Check Duplicate

```python
from app.database import db

exists = db.check_download_exists(
    laman_web='SerutiCrawler',
    data_tanggal='2025-11-08'
)

if exists:
    print("Data already downloaded")
```

---

## Database Maintenance

### Backup Database

```bash
# Using SQLite command
sqlite3 crawler.db ".backup crawler_backup.db"

# Using PowerShell
Copy-Item crawler.db crawler_backup_$(Get-Date -Format 'yyyyMMdd').db
```

### Restore Database

```bash
# Restore from backup
Copy-Item crawler_backup.db crawler.db
```

### Vacuum Database

```sql
-- Optimize database size
VACUUM;
```

### Analyze Database

```sql
-- Update query optimizer statistics
ANALYZE;
```

### Check Integrity

```sql
-- Verify database integrity
PRAGMA integrity_check;
```

### Get Database Info

```sql
-- Database page count and size
SELECT page_count * page_size as size 
FROM pragma_page_count(), pragma_page_size();

-- Table sizes
SELECT name, 
       SUM(pgsize) as size_bytes,
       SUM(pgsize)/1024 as size_kb,
       SUM(pgsize)/1024/1024 as size_mb
FROM dbstat 
GROUP BY name 
ORDER BY size_bytes DESC;
```

---

## Performance Optimization

### Enable WAL Mode

```sql
-- Write-Ahead Logging for better concurrency
PRAGMA journal_mode=WAL;
```

### Set Cache Size

```sql
-- Set cache size (pages)
PRAGMA cache_size=10000;
```

### Foreign Keys

```sql
-- Enable foreign key constraints (if needed)
PRAGMA foreign_keys=ON;
```

---

## Migration

### From JSON to SQLite

Automatic migration on first run:

```python
from app.database import db

# Run migration
jobs_migrated, logs_migrated = db.migrate_from_json(
    jobs_json='scheduler_jobs.json',
    logs_json='download_log.json'
)

print(f"Migrated: {jobs_migrated} jobs, {logs_migrated} logs")
```

### Export to JSON

```python
import json
from app.database import db

# Export jobs
jobs = db.get_all_jobs()
with open('jobs_export.json', 'w') as f:
    json.dump(jobs, f, indent=2)

# Export logs
logs = db.get_all_download_logs(limit=10000)
with open('logs_export.json', 'w') as f:
    json.dump(logs, f, indent=2)
```

---

## Database Schema Diagram

```
┌─────────────────────────────┐
│      scheduled_jobs         │
├─────────────────────────────┤
│ id (PK)                     │
│ name                        │
│ crawler_type                │
│ start_date                  │
│ end_date                    │
│ hour                        │
│ minute                      │
│ max_retries                 │
│ retry_delay                 │
│ status                      │
│ created_at                  │
│ last_run                    │
│ last_message                │
└─────────────────────────────┘
         │
         │ (logical relation)
         │
         ▼
┌─────────────────────────────┐
│      download_logs          │
├─────────────────────────────┤
│ id (PK)                     │
│ nama_file                   │
│ tanggal_download            │
│ laman_web                   │
│ data_tanggal                │
│ task_name                   │◄── Links to job name
│ created_at                  │
└─────────────────────────────┘
```

---

## Best Practices

### 1. Use Transactions

```python
from app.database import db

with db.get_connection() as conn:
    cursor = conn.cursor()
    # Multiple operations
    cursor.execute("INSERT ...")
    cursor.execute("UPDATE ...")
    # Auto-commit on success, auto-rollback on error
```

### 2. Index Usage

```sql
-- Good: Uses index
SELECT * FROM scheduled_jobs WHERE status = 'active';

-- Good: Uses index
SELECT * FROM download_logs 
WHERE laman_web = 'SerutiCrawler' 
  AND data_tanggal = '2025-11-08';

-- Bad: Full table scan
SELECT * FROM scheduled_jobs WHERE name LIKE '%crawl%';
```

### 3. Limit Results

```sql
-- Always use LIMIT for large datasets
SELECT * FROM download_logs 
ORDER BY tanggal_download DESC 
LIMIT 100;
```

### 4. Regular Backups

```bash
# Daily backup script
$date = Get-Date -Format 'yyyyMMdd'
Copy-Item crawler.db "backups\crawler_$date.db"
```

### 5. Monitor Size

```sql
-- Check database size regularly
SELECT page_count * page_size / 1024 / 1024 as size_mb 
FROM pragma_page_count(), pragma_page_size();
```

---

## Troubleshooting

### Database Locked

**Problem:** `sqlite3.OperationalError: database is locked`

**Solution:**
```bash
# Stop all connections
# Wait a few seconds
# Restart server
```

### Corruption

**Problem:** Database corrupted

**Solution:**
```bash
# Check integrity
sqlite3 crawler.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
Copy-Item crawler_backup.db crawler.db
```

### Slow Queries

**Problem:** Queries taking too long

**Solution:**
```sql
-- Analyze query plan
EXPLAIN QUERY PLAN 
SELECT * FROM scheduled_jobs WHERE status = 'active';

-- Rebuild indexes
REINDEX;

-- Vacuum database
VACUUM;
```

---

## Tools

### SQLite Browser

**Download:** https://sqlitebrowser.org/

**Features:**
- Visual table browser
- Query editor
- Schema designer
- Data editor

### Command Line

```bash
# Open database
sqlite3 crawler.db

# List tables
.tables

# Show schema
.schema scheduled_jobs

# Export to CSV
.mode csv
.output jobs.csv
SELECT * FROM scheduled_jobs;
.output stdout

# Exit
.quit
```

---

## References

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Python sqlite3 Module](https://docs.python.org/3/library/sqlite3.html)
- [SQLite Performance Tips](https://www.sqlite.org/speed.html)
