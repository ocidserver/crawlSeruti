# 🤖 Web Crawler - Seruti

Automated Login & File Download System menggunakan Python, Flask, dan Selenium.

## 📋 Fitur

- ✅ **Web Interface** - Dashboard modern untuk mengontrol crawler
- ✅ **Auto Login** - Login otomatis ke website target
- ✅ **SSO Support** - 🔐 Otomatis handle SSO BPS (https://sso.bps.go.id)
- ✅ **File Download** - Download file secara otomatis
- ✅ **🤖 AUTO SCHEDULER** - Crawl otomatis sesuai jadwal (daily, hourly, interval, custom cron)
- ✅ **Task Scheduler** - Windows Task Scheduler integration untuk auto-start
- ✅ **Headless Mode** - Jalankan browser tanpa tampilan GUI
- ✅ **Download Manager** - Kelola dan download file yang sudah diunduh
- ✅ **Real-time Logs** - Monitoring aktivitas crawler
- ✅ **Customizable** - Konfigurasi field selector dan URL
- ✅ **Auto Screenshot** - Screenshot otomatis saat error untuk debugging

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
# Install Python packages
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Konfigurasi

Copy file `.env.example` ke `.env` dan sesuaikan konfigurasi:

```powershell
Copy-Item .env.example .env
```

Edit file `.env`:

```env
# Target Website Configuration
TARGET_URL=https://example.com/login
DOWNLOAD_URL=https://example.com/logs

# Login Credentials
USERNAME=your_username
PASSWORD=your_password

# Application Settings
FLASK_SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
FLASK_PORT=5000

# Browser Settings
HEADLESS_MODE=False
BROWSER_TIMEOUT=30
```

### 3. Install Chrome Driver

Aplikasi akan otomatis mendownload ChromeDriver saat pertama kali dijalankan. Pastikan Google Chrome sudah terinstall.

### 4. Jalankan Aplikasi

```powershell
.venv\Scripts\python.exe run.py
```

Buka browser dan akses: **http://localhost:5000**

## � SSO BPS Support

Crawler ini **otomatis mendeteksi dan handle redirect ke SSO BPS**!

Ketika target URL redirect ke `https://sso.bps.go.id`, crawler akan:

- ✅ Otomatis detect redirect SSO
- ✅ Fill username & password dari file `.env`
- ✅ Submit form SSO
- ✅ Wait untuk redirect kembali ke aplikasi
- ✅ Lanjutkan proses download

**Lihat dokumentasi lengkap:** [SSO_GUIDE.md](SSO_GUIDE.md)

## 🤖 AUTO SCHEDULER

**Crawler bisa berjalan otomatis sesuai jadwal!**

### Quick Start Automation:

**1. Via Web API (Paling Mudah):**

```powershell
# Start scheduler - setiap hari jam 8 pagi
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/start" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"mode":"daily","hour":8,"minute":0}'

# Start scheduler - setiap 30 menit
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/start" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"mode":"interval","hours":0,"minutes":30}'

# Check status
Invoke-WebRequest -Uri "http://localhost:5000/api/scheduler/status"
```

**2. Via Standalone Script:**

```powershell
# Run once
.\.venv\Scripts\python.exe auto_crawl.py

# Run loop setiap 30 menit
.\.venv\Scripts\python.exe auto_crawl.py --loop --interval 30
```

**3. Via Windows Task Scheduler (Auto-start):**

- Buka Task Scheduler (`taskschd.msc`)
- Create Task → Program: `run_auto_crawl.bat`
- Set trigger (daily/startup/etc)

**� Dokumentasi Lengkap:**

- [STEP_BY_STEP_AUTOMATION.md](STEP_BY_STEP_AUTOMATION.md) - **Tahapan lengkap automation**
- [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) - Guide detail semua method
- [QUICKSTART_AUTOMATION.md](QUICKSTART_AUTOMATION.md) - Quick reference

## �📁 Struktur Project

```
crawlSeruti/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Konfigurasi aplikasi
│   ├── crawler.py           # Selenium crawler engine
│   ├── scheduler.py         # 🤖 Auto scheduler untuk crawl otomatis
│   ├── routes.py            # API endpoints
│   ├── templates/
│   │   └── index.html       # Web dashboard
│   └── static/              # Static files (CSS, JS)
├── downloads/               # Downloaded files
├── logs/                    # Application logs
├── auto_crawl.py            # 🤖 Standalone automation script
├── start_crawler.bat        # Windows batch file untuk start app
├── run_auto_crawl.bat       # Windows batch file untuk auto crawl
├── .env                     # Environment variables (buat manual)
├── .env.example             # Template konfigurasi
├── .gitignore              # Git ignore rules
├── requirements.txt         # Python dependencies
└── run.py                   # Main entry point
```

## 🎯 Cara Penggunaan

### Web Interface

1. **Buka Dashboard**

   - Akses http://localhost:5000
   - Dashboard akan menampilkan form crawl

2. **Isi Form Crawl**

   - **Username & Password**: Kredensial login
   - **Target URL**: URL halaman login
   - **Download URL**: URL halaman download (optional)
   - **Headless Mode**: Centang untuk menjalankan tanpa tampilan browser

3. **Advanced Settings** (Optional)

   - **Username Field**: Nama field input username (default: `username`)
   - **Password Field**: Nama field input password (default: `password`)
   - **Submit Button**: XPath tombol submit (default: `//button[@type='submit']`)
   - **Download Button**: XPath tombol download

4. **Start Crawl**

   - Klik tombol "🚀 Start Crawl"
   - Tunggu proses selesai
   - File akan muncul di bagian "Downloaded Files"

5. **Download Files**

   - Klik tombol "⬇️ Download" pada file yang diinginkan
   - File akan didownload ke komputer Anda

6. **View Logs**
   - Klik "🔄 Refresh Logs" untuk melihat activity log
   - Berguna untuk debugging

### Programmatic Usage

Anda juga bisa menggunakan crawler secara programmatic:

```python
from app.crawler import SerutiCrawler

# Inisialisasi crawler
crawler = SerutiCrawler(
    username="your_username",
    password="your_password",
    headless=False
)

# Jalankan full crawl
result = crawler.run_full_crawl(
    target_url="https://example.com/login",
    download_url="https://example.com/download",
    username_field="username",
    password_field="password",
    submit_button="//button[@type='submit']",
    download_button_xpath="//a[@id='download']"
)

print(result)
```

## 🔧 API Endpoints

### Crawl Endpoints

#### POST `/api/crawl`

Memulai proses crawling

**Request Body:**

```json
{
  "username": "user",
  "password": "pass",
  "target_url": "https://example.com/login",
  "download_url": "https://example.com/download",
  "username_field": "username",
  "password_field": "password",
  "submit_button": "//button[@type='submit']",
  "download_button_xpath": "//a[@id='download']",
  "headless": false
}
```

**Response:**

```json
{
  "success": true,
  "message": "Crawl completed successfully. File: report.pdf",
  "file": "report.pdf",
  "screenshots": []
}
```

#### GET `/api/downloads`

List semua file yang sudah didownload

**Response:**

```json
{
  "success": true,
  "files": [
    {
      "filename": "report.pdf",
      "size": 1024000,
      "modified": "2025-11-07 10:30:00"
    }
  ]
}
```

#### GET `/api/download/<filename>`

Download file tertentu

#### GET `/api/logs`

Melihat application logs

#### GET `/api/config`

Mendapatkan konfigurasi default

---

### 🤖 Scheduler Endpoints (NEW!)

#### POST `/api/scheduler/start`

Start automated scheduler

**Request Body:**

```json
{
  "mode": "daily", // daily, hourly, interval, custom
  "hour": 8, // for daily mode (0-23)
  "minute": 0, // for daily/hourly mode (0-59)
  "hours": 0, // for interval mode
  "minutes": 30, // for interval mode
  "cron": "0 8 * * *" // for custom mode
}
```

**Response:**

```json
{
  "success": true,
  "message": "✅ Scheduler started: Daily at 08:00",
  "is_running": true
}
```

#### POST `/api/scheduler/stop`

Stop the scheduler

**Response:**

```json
{
  "success": true,
  "message": "🛑 Scheduler stopped",
  "is_running": false
}
```

#### GET `/api/scheduler/status`

Get scheduler status and jobs

**Response:**

```json
{
  "success": true,
  "is_running": true,
  "jobs": [
    {
      "id": "daily_crawl",
      "name": "Daily Auto Crawl",
      "next_run": "2024-01-15 08:00:00"
    }
  ]
}
```

#### POST `/api/scheduler/run-now`

Trigger crawl immediately (manual trigger)

Mendapatkan konfigurasi default

## 🔍 Tips & Troubleshooting

### Menemukan XPath Element

1. Buka website target di Chrome
2. Klik kanan pada element (input/button) → Inspect
3. Klik kanan pada HTML element → Copy → Copy XPath
4. Paste XPath tersebut di Advanced Settings

### Common Issues

**Error: ChromeDriver not found**

- Pastikan Google Chrome terinstall
- Aplikasi akan auto-download driver saat pertama kali run

**Error: Element not found**

- Periksa XPath selector
- Coba gunakan Headless Mode = False untuk debugging
- Check screenshot di folder `logs/` untuk melihat kondisi halaman

**Error: Download tidak berjalan**

- Pastikan Download URL sudah benar
- Atau gunakan Download Button XPath jika download via button
- Check folder `downloads/` apakah file ada

**Login gagal**

- Periksa username dan password
- Check apakah ada CAPTCHA (belum support auto CAPTCHA)
- Lihat logs untuk detail error

## 🛡️ Security Notes

- **JANGAN commit file `.env`** ke Git (sudah ada di `.gitignore`)
- Gunakan environment variables untuk credentials
- Untuk production, set `FLASK_DEBUG=False`
- Ganti `FLASK_SECRET_KEY` dengan value yang secure

## 📦 Dependencies

- **Flask** - Web framework
- **Selenium** - Browser automation
- **webdriver-manager** - Auto ChromeDriver download
- **python-dotenv** - Environment variable management
- **requests** - HTTP library
- **apscheduler** - Task scheduling (untuk future enhancement)

## 🔮 Future Enhancements

- [ ] Scheduled crawling (cron jobs)
- [ ] Multi-site support
- [ ] CAPTCHA handling
- [ ] Email notifications
- [ ] Database integration
- [ ] User authentication
- [ ] Download queue management
- [ ] Proxy support

## 📝 License

MIT License - Feel free to use and modify

## 👨‍💻 Developer

Created for automated web crawling and file download purposes.

---

**Happy Crawling! 🚀**
