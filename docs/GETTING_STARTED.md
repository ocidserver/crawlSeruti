# Getting Started Guide

Panduan lengkap untuk memulai menggunakan BPS Web Crawler System.

---

## 📋 Prerequisites

### System Requirements

- **OS:** Windows 10/11 (recommended) atau Linux
- **Python:** 3.8 atau lebih tinggi
- **RAM:** Minimum 4GB
- **Disk Space:** Minimum 500MB
- **Browser:** Google Chrome (latest version)

### Required Software

```powershell
# Check Python version
python --version
# Should show: Python 3.8.x or higher

# Check pip
python -m pip --version

# Check Chrome
# Buka Chrome → Help → About Google Chrome
```

---

## 🚀 Installation

### Step 1: Clone Repository

```powershell
# Clone dari GitHub
git clone https://github.com/ocidserver/crawlSeruti.git

# Masuk ke direktori
cd crawlSeruti
```

### Step 2: Create Virtual Environment

```powershell
# Create venv (jika belum ada)
python -m venv .venv

# Activate venv
.venv\Scripts\Activate.ps1

# Jika error "execution policy", jalankan:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected Packages:**

- Flask >= 3.0.0
- Selenium >= 4.15.2
- APScheduler >= 3.10.4
- webdriver-manager >= 4.0.1
- python-dotenv >= 1.0.0

---

## ⚙️ Configuration

### Step 1: Environment File

```powershell
# Copy example file
Copy-Item .env.example .env

# Edit dengan notepad
notepad .env
```

### Step 2: Configure Settings

**Minimum Required:**

```env
# BPS SSO Credentials
USERNAME=your_bps_username
PASSWORD=your_bps_password

# Flask Configuration
FLASK_SECRET_KEY=generate-random-string-here
FLASK_PORT=5000
FLASK_DEBUG=True

# Download Settings
DOWNLOAD_PATH=downloads
HEADLESS_MODE=True
```

**Generate Secret Key:**

```python
# Run in Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 3: Test Configuration

```powershell
# Test import
python -c "from app.config import Config; print('Config OK:', Config.USERNAME)"

# Should show your username
```

---

## 🎯 First Run

### Step 1: Start Server

```powershell
# Ensure venv is activated
.venv\Scripts\python.exe run.py
```

**Expected Output:**

```
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║           🤖 WEB CRAWLER - SERUTI                     ║
    ║           Automated Login & Download System           ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝

    Server running on: http://localhost:5000

    Press CTRL+C to quit

✅ Database initialized: crawler.db
```

### Step 2: Access Dashboard

1. Open browser
2. Navigate to: http://localhost:5000
3. You should see the crawler dashboard

### Step 3: First Crawl Test

**Manual Test:**

1. Select crawler: **SERUTI** atau **SUSENAS**
2. Click crawler card
3. Wait for completion
4. Check downloads folder

**Expected Result:**

- ✅ Browser opens (if not headless)
- ✅ Login successful
- ✅ File downloaded to `downloads/` folder
- ✅ Download logged in database

---

## 📊 Create First Scheduled Job

### Step 1: Configure Schedule

1. **Select Crawler Type:**

   - Click **SERUTI** card (blue) atau
   - Click **SUSENAS** card (cyan)

2. **Fill Form:**

   ```
   Nama Job: Daily Seruti Crawl
   Start Date: 2025-11-08
   End Date: 2025-12-31
   Jam: 08
   Menit: 00
   Max Retry: 3
   Delay Retry: 300 (seconds)
   ```

3. **Submit:**
   - Click **"Tambah Jadwal"** button

### Step 2: Verify Job

**Check Job List Table:**

- Should show new job with status: **Active**
- Next Run should show: `2025-11-08 08:00:00`
- Crawler badge: **SERUTI** or **SUSENAS**

### Step 3: Monitor Job

**Table Columns:**

1. **Nama Job** - Your job name
2. **Crawler** - SERUTI/SUSENAS badge
3. **Status** - Active (blue badge)
4. **Periode** - Date range
5. **Waktu** - Execution time
6. **Next Run** - Scheduled time
7. **Last Run** - Empty (first run)
8. **Message** - Empty (no runs yet)
9. **Action** - Cancel button

---

## 🧪 Testing

### Test 1: Manual Crawl

```powershell
# Test Seruti
.venv\Scripts\python.exe tests\test_multi_crawler.py

# Expected: SUCCESS message with file name
```

### Test 2: Susenas Crawl

```powershell
# Test Susenas (headless)
.venv\Scripts\python.exe tests\test_susenas_crawl.py

# Expected: 7/7 files downloaded
```

### Test 3: Database Check

```powershell
# Open database
sqlite3 crawler.db

# Check jobs
SELECT * FROM scheduled_jobs;

# Check logs
SELECT * FROM download_logs ORDER BY tanggal_download DESC LIMIT 5;

# Exit
.quit
```

---

## 📁 Project Structure

```
crawlSeruti/
├── app/
│   ├── __init__.py           # Flask app
│   ├── config.py             # Configuration
│   ├── database.py           # SQLite manager
│   ├── scheduler.py          # Job scheduler
│   ├── download_log.py       # Download tracking
│   ├── routes.py             # API routes
│   ├── crawlers/
│   │   ├── __init__.py
│   │   ├── base_crawler.py   # Base class
│   │   ├── seruti_crawler.py # Seruti
│   │   └── susenas_crawler.py# Susenas
│   └── templates/
│       └── index.html        # Dashboard
│
├── docs/                     # Documentation
│   ├── CHANGELOG.md
│   ├── SERUTI_GUIDE.md
│   ├── SUSENAS_GUIDE.md
│   └── ...
│
├── tests/                    # Test files
├── downloads/                # Downloaded files
├── crawler.db                # SQLite database
├── .env                      # Configuration (create this)
├── requirements.txt          # Dependencies
├── run.py                    # Entry point
└── README.md                 # Project readme
```

---

## 🔧 Common Tasks

### Check Jobs Status

```python
# In Python console
from app.database import db

# Get all jobs
jobs = db.get_all_jobs()
for job in jobs:
    print(f"{job['name']}: {job['status']}")
```

### View Download History

```python
# In Python console
from app.database import db

# Get recent downloads
logs = db.get_all_download_logs(limit=10)
for log in logs:
    print(f"{log['nama_file']} - {log['tanggal_download']}")
```

### Cancel a Job

**Via Web UI:**

1. Find job in table
2. Click **Cancel** button
3. Confirm cancellation

**Via Python:**

```python
from app.database import db

db.cancel_job('job_20251108120000')
```

### Backup Database

```powershell
# Simple copy
Copy-Item crawler.db crawler_backup_$(Get-Date -Format 'yyyyMMdd').db

# Or use SQLite backup
sqlite3 crawler.db ".backup crawler_backup.db"
```

---

## 🐛 Troubleshooting

### Problem 1: ChromeDriver Error

**Error:**

```
WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

**Solution:**

```powershell
# Run fix script
.venv\Scripts\python.exe fix_chromedriver.py

# Or clear cache
Remove-Item -Recurse -Force "$env:USERPROFILE\.wdm"
```

### Problem 2: Port Already in Use

**Error:**

```
OSError: [WinError 10048] Only one usage of each socket address
```

**Solution:**

```powershell
# Check port 5000
netstat -ano | findstr :5000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or use different port
$env:FLASK_PORT="5001"
.venv\Scripts\python.exe run.py
```

### Problem 3: Login Failed

**Error:**

```
Login failed: Element not found
```

**Solution:**

1. Check credentials in `.env`
2. Test manual login in browser
3. Check SSO status: https://sso.bps.go.id
4. Run with visible browser:
   ```env
   HEADLESS_MODE=False
   ```

### Problem 4: Database Locked

**Error:**

```
sqlite3.OperationalError: database is locked
```

**Solution:**

```powershell
# Check if another process is using database
# Stop server
Ctrl+C

# Wait a moment
Start-Sleep -Seconds 5

# Restart server
.venv\Scripts\python.exe run.py
```

---

## 📚 Next Steps

### Learn More

1. [SERUTI_GUIDE.md](SERUTI_GUIDE.md) - Detailed Seruti crawler guide
2. [SUSENAS_GUIDE.md](SUSENAS_GUIDE.md) - Detailed Susenas crawler guide
3. [SCHEDULER_GUIDE.md](SCHEDULER_GUIDE.md) - Advanced scheduling
4. [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

### Advanced Topics

- Custom crawler development
- API integration
- Database optimization
- Performance tuning
- Production deployment

### Get Help

- Check [CHANGELOG.md](CHANGELOG.md) for recent changes
- Review [API.md](API.md) for API documentation
- See [DATABASE.md](DATABASE.md) for schema details

---

## ✅ Checklist

Before you start:

- [ ] Python 3.8+ installed
- [ ] Chrome browser installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Server starts successfully
- [ ] Dashboard accessible
- [ ] Test crawl successful
- [ ] First job scheduled

---

## 🎓 Tips for Success

1. **Start Simple**

   - Test manual crawl first
   - Then schedule one job
   - Monitor before scaling

2. **Monitor Regularly**

   - Check job status daily
   - Review download logs
   - Watch for errors

3. **Backup Often**

   - Backup database weekly
   - Keep configuration backup
   - Export important data

4. **Keep Updated**

   - Pull latest changes regularly
   - Review CHANGELOG
   - Test after updates

5. **Ask for Help**
   - Check documentation first
   - Review error messages
   - Contact support if needed

---

**Ready to Start?** 🚀

```powershell
# Start your crawler!
.venv\Scripts\python.exe run.py
```

Good luck! 🎉
