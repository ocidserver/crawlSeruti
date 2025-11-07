# 📋 TAHAPAN AUTOMATION - Step by Step

## 🎯 Ringkasan

Berikut **tahapan lengkap** membuat crawler berjalan otomatis tanpa intervensi manual.

---

## ✅ TAHAP 1: Persiapan (WAJIB)

### 1.1 Pastikan App Berjalan

```powershell
# Di terminal PowerShell
cd C:\Users\IPDS-OCID\crawlSeruti
.\.venv\Scripts\python.exe run.py
```

✅ **Cek:** Buka http://localhost:5000 - harusnya dashboard muncul

### 1.2 Konfigurasi Download URL

```powershell
# Edit file .env
# Ganti DOWNLOAD_URL dengan URL sebenarnya
```

**Sebelum:**

```env
DOWNLOAD_URL=https://example.com/logs
```

**Sesudah:**

```env
DOWNLOAD_URL=https://olah.web.bps.go.id/seruti/halaman-download-actual
```

⚠️ **PENTING:** URL ini HARUS URL halaman download yang sebenarnya!

### 1.3 Test Manual Crawl

1. Buka http://localhost:5000
2. Klik tombol "Start Crawl"
3. Lihat apakah berhasil:
   - ✅ Login ke SSO BPS
   - ✅ Masuk ke halaman download
   - ✅ File terdownload

Jika gagal, perbaiki dulu sebelum lanjut automation!

---

## ✅ TAHAP 2: Pilih Method Automation

### 🎯 **Method A: Python Scheduler (Recommended - Paling Mudah)**

#### Langkah A1: Test Scheduler via API

**1. Start scheduler (setiap hari jam 8 pagi):**

```powershell
# Windows PowerShell
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/start" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"mode":"daily","hour":8,"minute":0}'
```

**2. Cek status:**

```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/scheduler/status"
```

**Response yang diharapkan:**

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

#### Langkah A2: Test Manual Trigger

```powershell
# Trigger crawl sekarang (untuk test)
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/run-now"
```

Cek logs di terminal - harusnya muncul output crawling.

#### Langkah A3: Variasi Schedule

**Setiap jam:**

```powershell
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/start" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"mode":"hourly","minute":0}'
```

**Setiap 30 menit:**

```powershell
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/start" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"mode":"interval","hours":0,"minutes":30}'
```

**Custom schedule (jam 8, 12, 18):**

```powershell
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/start" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"mode":"custom","cron":"0 8,12,18 * * *"}'
```

#### Langkah A4: Stop Scheduler

```powershell
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/stop"
```

---

### 🎯 **Method B: Standalone Script (Paling Simple)**

#### Langkah B1: Test Script

```powershell
# Test konfigurasi dulu
.\.venv\Scripts\python.exe auto_crawl.py --test
```

**Output yang diharapkan:**

```
====================================
📋 CURRENT CONFIGURATION
====================================
Target URL    : https://olah.web.bps.go.id/seruti/login
Download URL  : https://olah.web.bps.go.id/seruti/download
Username      : rasyidka
Password      : *************
Headless Mode : True
====================================
```

#### Langkah B2: Run Sekali

```powershell
.\.venv\Scripts\python.exe auto_crawl.py
```

Cek apakah berhasil download file.

#### Langkah B3: Run Loop Mode

```powershell
# Loop setiap 30 menit
.\.venv\Scripts\python.exe auto_crawl.py --loop --interval 30
```

Biarkan terminal tetap terbuka - script akan jalan terus.

---

### 🎯 **Method C: Windows Task Scheduler (Auto-Start)**

#### Langkah C1: Test Batch File

```powershell
# Test file .bat
.\run_auto_crawl.bat
```

Harusnya crawler jalan dan download file.

#### Langkah C2: Setup Task Scheduler

**1. Buka Task Scheduler:**

```powershell
# Windows Key + R, ketik:
taskschd.msc
```

**2. Create Basic Task:**

- Klik `Create Basic Task...`
- **Name:** `Seruti Auto Crawl`
- **Description:** `Auto download log BPS Seruti`
- Klik `Next`

**3. Trigger (Pilih salah satu):**

**Opsi 1 - Daily:**

- When: `Daily`
- Start: `Hari ini`
- Time: `08:00:00`
- Recur every: `1 days`

**Opsi 2 - At startup:**

- When: `When the computer starts`

**Opsi 3 - Multiple times per day:**

- When: `Daily`
- Start: `Hari ini`
- Time: `08:00:00`
- Klik `Next`, lalu di summary page klik `Open Properties`
- Di tab `Triggers`, add multiple triggers (08:00, 12:00, 18:00)

**4. Action:**

- Action: `Start a program`
- Program/script: `C:\Users\IPDS-OCID\crawlSeruti\run_auto_crawl.bat`
- Start in: `C:\Users\IPDS-OCID\crawlSeruti`

**5. Settings (Important!):**

- ✅ Run whether user is logged on or not
- ✅ Run with highest privileges
- ✅ Configure for: `Windows 10`

#### Langkah C3: Test Task

- Right-click task → `Run`
- Lihat di `History` tab - harusnya success

---

## ✅ TAHAP 3: Monitoring & Maintenance

### 3.1 Cek Logs

**App logs:**

```powershell
Get-Content -Path "logs\app.log" -Tail 50
```

**Auto crawl logs:**

```powershell
Get-Content -Path "logs\auto_crawl.log" -Tail 50
```

### 3.2 Monitor Downloads

```powershell
# List downloaded files
Get-ChildItem -Path "downloads" | Sort-Object LastWriteTime -Descending | Select-Object -First 10
```

### 3.3 Disk Space Monitoring

```powershell
# Check folder size
Get-ChildItem -Path "downloads" -Recurse | Measure-Object -Property Length -Sum
```

Jika terlalu besar, backup dan hapus file lama.

---

## ✅ TAHAP 4: Troubleshooting

### ❌ Problem: Scheduler tidak jalan

**Cek status:**

```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/scheduler/status"
```

**Fix:**

```powershell
# Stop dulu
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/stop"

# Start lagi
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/start" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"mode":"daily","hour":8,"minute":0}'
```

### ❌ Problem: Crawl gagal saat auto mode

**Cek logs:**

```powershell
Get-Content -Path "logs\auto_crawl.log" -Tail 100
```

**Kemungkinan penyebab:**

1. `DOWNLOAD_URL` salah → perbaiki di `.env`
2. Website error → coba lagi nanti
3. Credentials salah → cek `.env`
4. XPath berubah → update di `crawler.py`

**Test manual:**

```powershell
# Run manual untuk debug
.\.venv\Scripts\python.exe auto_crawl.py
```

### ❌ Problem: Task Scheduler tidak start

**Cek:**

1. User account harus admin
2. Path di `.bat` harus benar
3. "Run with highest privileges" enabled

**Test batch file manual:**

```powershell
.\run_auto_crawl.bat
```

---

## ✅ TAHAP 5: Advanced Features (Optional)

### 5.1 Email Notification

Install package:

```powershell
.\.venv\Scripts\pip.exe install secure-smtplib
```

Tambahkan di `auto_crawl.py`:

```python
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'crawler@example.com'
    msg['To'] = 'your@email.com'

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your@email.com', 'password')
        server.send_message(msg)
```

### 5.2 Cloud Backup

Setup OneDrive/Google Drive sync untuk folder `downloads/`

### 5.3 Webhook Notification

Kirim ke Slack/Discord/Telegram saat crawl selesai.

---

## 📊 Rekapitulasi Method

| Method                | Kompleksitas    | Auto-Start | Monitoring   | Recommended For       |
| --------------------- | --------------- | ---------- | ------------ | --------------------- |
| **Python Scheduler**  | ⭐⭐ Mudah      | ❌ Manual  | ✅ Web UI    | Testing & Development |
| **Standalone Script** | ⭐ Sangat Mudah | ❌ Manual  | ⚠️ Logs only | Quick Jobs            |
| **Task Scheduler**    | ⭐⭐⭐ Sedang   | ✅ Auto    | ⚠️ Limited   | **Production**        |

---

## 🎯 Rekomendasi Final

### Untuk **Development/Testing:**

✅ **Gunakan Python Scheduler (Method A)**

```powershell
# One command setup:
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/start" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"mode":"interval","hours":0,"minutes":30}'
```

### Untuk **Production (24/7):**

✅ **Gunakan Task Scheduler (Method C)**

- Auto-start saat PC nyala
- Reliable
- No manual intervention

---

## 🎉 Selesai!

**Your crawler is now FULLY AUTOMATED! 🚀**

### Quick Commands Cheat Sheet:

```powershell
# Start scheduler (every 30 min)
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/start" -Headers @{"Content-Type"="application/json"} -Body '{"mode":"interval","hours":0,"minutes":30}'

# Check status
Invoke-WebRequest -Uri "http://localhost:5000/api/scheduler/status"

# Run now (test)
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/run-now"

# Stop scheduler
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/scheduler/stop"

# Check logs
Get-Content -Path "logs\auto_crawl.log" -Tail 50

# List downloads
Get-ChildItem -Path "downloads" | Sort-Object LastWriteTime -Descending
```

---

**Butuh bantuan?** Lihat:

- [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) - Dokumentasi lengkap
- [QUICKSTART_AUTOMATION.md](QUICKSTART_AUTOMATION.md) - Quick reference
- `logs/` folder - Check error logs
