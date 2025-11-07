# 🤖 BPS Web Crawler - Multi Crawler System

Automated web crawler system untuk BPS dengan support multiple crawlers (Seruti & Susenas), scheduler, dan database management.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Selenium](https://img.shields.io/badge/Selenium-4.15+-orange.svg)](https://www.selenium.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue.svg)](https://www.sqlite.org/)

---

## 📋 Features

### 🎯 Core Features

- ✅ **Multi-Crawler Architecture** - Support Seruti & Susenas crawlers
- ✅ **SSO Authentication** - Auto login via BPS SSO (https://sso.bps.go.id)
- ✅ **Smart Download Detection** - Skip duplicate data berdasarkan tanggal
- ✅ **Task Scheduler** - Scheduled jobs dengan cron-like scheduling
- ✅ **SQLite Database** - ACID-compliant data storage
- ✅ **Headless Mode** - Background execution tanpa GUI

### 📊 Management Features

- ✅ **Job History** - Track semua jobs (active, completed, cancelled, failed)
- ✅ **Download Log** - Complete download tracking dengan task name
- ✅ **Retry Mechanism** - Auto-retry dengan configurable delay
- ✅ **Web Dashboard** - Modern UI dengan table format
- ✅ **Real-time Status** - Live job monitoring

### 🔒 Data & Security

- ✅ **Transaction Safety** - No data loss saat system crash
- ✅ **Data Validation** - Check duplicate sebelum download
- ✅ **Environment Variables** - Secure credential management
- ✅ **Backup System** - Auto backup saat migration

---

## 🚀 Quick Start

### 1. Setup Environment

```powershell
# Clone repository
git clone https://github.com/ocidserver/crawlSeruti.git
cd crawlSeruti

# Install dependencies (using venv)
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Configure

```powershell
# Copy environment file
Copy-Item .env.example .env

# Edit .env file
notepad .env
```

**Required Configuration:**

```env
# BPS SSO Credentials
USERNAME=your_username
PASSWORD=your_password

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
FLASK_PORT=5000
FLASK_DEBUG=True

# Download Settings
DOWNLOAD_PATH=downloads
HEADLESS_MODE=True
```

### 3. Run Application

```powershell
# Start Flask server
.venv\Scripts\python.exe run.py

# Access web interface
# Open browser: http://localhost:5000
```

---

## 📖 Documentation

### 📚 User Guides

- [Getting Started Guide](docs/GETTING_STARTED.md) - Panduan lengkap untuk pemula
- [Seruti Crawler Guide](docs/SERUTI_GUIDE.md) - Panduan crawler Seruti
- [Susenas Crawler Guide](docs/SUSENAS_GUIDE.md) - Panduan crawler Susenas
- [Scheduler Guide](docs/SCHEDULER_GUIDE.md) - Panduan task scheduler

### 🔧 Technical Docs

- [Architecture](docs/ARCHITECTURE.md) - System architecture & design
- [Database Schema](docs/DATABASE.md) - SQLite schema & queries
- [API Reference](docs/API.md) - REST API endpoints

### 📝 Change History

- [CHANGELOG.md](docs/CHANGELOG.md) - Complete version history
- [Migration Guide](docs/MIGRATION.md) - Upgrade instructions

---

## 🏗️ Architecture

```
crawlSeruti/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Configuration management
│   ├── database.py           # SQLite database manager
│   ├── scheduler.py          # APScheduler wrapper
│   ├── download_log.py       # Download tracking
│   ├── routes.py             # API endpoints
│   ├── crawlers/
│   │   ├── base_crawler.py   # Abstract base class
│   │   ├── seruti_crawler.py # Seruti implementation
│   │   └── susenas_crawler.py# Susenas implementation
│   └── templates/
│       └── index.html        # Web dashboard
├── docs/                     # Documentation
├── tests/                    # Test files
├── downloads/                # Downloaded files
├── crawler.db                # SQLite database
├── requirements.txt          # Python dependencies
└── run.py                    # Application entry point
```

---

## 🎮 Usage

### Web Dashboard

1. **Start Server**

   ```powershell
   .venv\Scripts\python.exe run.py
   ```

2. **Open Dashboard**

   - URL: http://localhost:5000
   - Select crawler: SERUTI atau SUSENAS
   - Configure schedule
   - Add job

3. **Monitor Jobs**
   - View active/inactive jobs in table format
   - Check status, next run, last run
   - Cancel jobs if needed
   - View download log

### Command Line

**Manual Crawl:**

```powershell
# Seruti crawler
.venv\Scripts\python.exe -c "from app.crawlers import get_crawler; from app.config import Config; crawler = get_crawler('seruti')(Config.USERNAME, Config.PASSWORD); print(crawler.run())"

# Susenas crawler
.venv\Scripts\python.exe -c "from app.crawlers import get_crawler; from app.config import Config; crawler = get_crawler('susenas')(Config.USERNAME, Config.PASSWORD); print(crawler.run())"
```

**Run Tests:**

```powershell
# Test Seruti
.venv\Scripts\python.exe tests\test_multi_crawler.py

# Test Susenas
.venv\Scripts\python.exe tests\test_susenas_crawl.py
```

---

## 📊 Crawlers

### 1. Seruti Crawler

- **Target:** https://olah.web.bps.go.id
- **Function:** Download Progres Triwulan
- **Authentication:** SSO BPS
- **Data Format:** Excel (.xlsx)
- **Performance:** ~57 seconds per download
- **Optimization:** 11.5% faster vs original

### 2. Susenas Crawler

- **Target:** https://webmonitoring.bps.go.id/sen
- **Function:** Download 7 progress reports
- **Reports:**
  1. Laporan Pencacahan
  2. Laporan Pemeriksaan (Edcod)
  3. Laporan Pengiriman ke Kabkot
  4. Laporan Penerimaan di Kabkot
  5. Laporan Penerimaan di IPDS
  6. Laporan Pengolahan Dokumen M
  7. Laporan Pengolahan Dokumen KP
- **Performance:** ~40 seconds for 7 files (headless)
- **Smart Validation:** Skip if data already exists (29 seconds)

---

## 🗄️ Database

### Tables

**scheduled_jobs:**

```sql
CREATE TABLE scheduled_jobs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    crawler_type TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    hour INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    status TEXT DEFAULT 'active',
    created_at TEXT NOT NULL,
    last_run TEXT,
    last_message TEXT
);
```

**download_logs:**

```sql
CREATE TABLE download_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_file TEXT NOT NULL,
    tanggal_download TEXT NOT NULL,
    laman_web TEXT NOT NULL,
    data_tanggal TEXT,
    task_name TEXT DEFAULT 'Manual'
);
```

---

## 🔧 Configuration

### Environment Variables

| Variable           | Description           | Default   |
| ------------------ | --------------------- | --------- |
| `USERNAME`         | BPS SSO username      | -         |
| `PASSWORD`         | BPS SSO password      | -         |
| `FLASK_SECRET_KEY` | Flask session key     | -         |
| `FLASK_PORT`       | Web server port       | 5000      |
| `FLASK_DEBUG`      | Debug mode            | False     |
| `DOWNLOAD_PATH`    | Download directory    | downloads |
| `HEADLESS_MODE`    | Browser headless mode | True      |

### Scheduler Configuration

| Parameter     | Description                     | Range      |
| ------------- | ------------------------------- | ---------- |
| `start_date`  | Job start date                  | YYYY-MM-DD |
| `end_date`    | Job end date                    | YYYY-MM-DD |
| `hour`        | Execution hour                  | 0-23       |
| `minute`      | Execution minute                | 0-59       |
| `max_retries` | Max retry attempts              | 0-10       |
| `retry_delay` | Delay between retries (seconds) | 60+        |

---

## 🧪 Testing

### Run All Tests

```powershell
# Test multi-crawler
.venv\Scripts\python.exe tests\test_multi_crawler.py

# Test Susenas crawler
.venv\Scripts\python.exe tests\test_susenas_crawl.py

# Test download detection
.venv\Scripts\python.exe tests\test_download_detection.py
```

### Test Results

- ✅ Seruti: Download successful (57s)
- ✅ Susenas: 7/7 files downloaded (40s)
- ✅ Smart validation: Skip duplicate (29s)
- ✅ Database: ACID transactions working
- ✅ UI: Table format responsive

---

## 🐛 Troubleshooting

### ChromeDriver Issues

```powershell
# Fix ChromeDriver path
.venv\Scripts\python.exe fix_chromedriver.py

# Clear cache
Remove-Item -Recurse -Force "$env:USERPROFILE\.wdm"
```

### Database Issues

```bash
# Check database
sqlite3 crawler.db ".tables"

# Backup database
sqlite3 crawler.db ".backup crawler_backup.db"

# Re-migrate from JSON
rm crawler.db
# Restore *.json.backup files
# Restart server (auto-migration)
```

### Server Not Starting

```powershell
# Check port availability
netstat -ano | findstr :5000

# Use different port
$env:FLASK_PORT="5001"
.venv\Scripts\python.exe run.py
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📜 License

This project is for internal BPS use only.

---

## 👥 Authors

- **IPDS-OCID Team** - BPS Provinsi Kepulauan Riau

---

## 🙏 Acknowledgments

- BPS IT Team untuk SSO infrastructure
- APScheduler untuk job scheduling
- Selenium WebDriver untuk browser automation
- Flask untuk web framework
- SQLite untuk embedded database

---

## 📞 Support

Untuk bantuan dan pertanyaan:

- Email: [your-email@bps.go.id]
- Issue Tracker: [GitHub Issues](https://github.com/ocidserver/crawlSeruti/issues)

---

**Last Updated:** November 2025  
**Version:** 2.0.0  
**Status:** Production Ready ✅
