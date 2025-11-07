# 🤖 Panduan Automation - Crawl Otomatis

## 📋 Ringkasan

Panduan ini menjelaskan cara membuat crawler berjalan **otomatis** tanpa intervensi manual.

---

## 🎯 Cara 1: Scheduler Python (Built-in) - **RECOMMENDED**

### ✅ Kelebihan:

- ✨ Paling mudah dan terintegrasi
- 🔧 Bisa diatur dari web dashboard
- 📊 Real-time monitoring
- 🚀 Langsung jalan saat aplikasi running

### 📝 Langkah-langkah:

#### **Step 1: Pastikan App Running**

```powershell
# Di terminal
cd C:\Users\IPDS-OCID\crawlSeruti
.\.venv\Scripts\python.exe run.py
```

#### **Step 2: Konfigurasi Target Download**

Sebelum automation, pastikan `DOWNLOAD_URL` sudah benar di `.env`:

```env
DOWNLOAD_URL=https://olah.web.bps.go.id/seruti/actual-download-page
```

#### **Step 3: Aktifkan Scheduler via Web Dashboard**

**Buka browser:** http://localhost:5000

**Pilih mode automation:**

##### Mode 1: **Daily (Setiap Hari)**

```javascript
// POST ke /api/scheduler/start
{
  "mode": "daily",
  "hour": 8,      // Jam 08:00 pagi
  "minute": 0
}
```

✅ Cocok untuk: Laporan harian

##### Mode 2: **Hourly (Setiap Jam)**

```javascript
{
  "mode": "hourly",
  "minute": 0     // Setiap jam di menit 0 (01:00, 02:00, dst)
}
```

✅ Cocok untuk: Monitoring real-time

##### Mode 3: **Interval (Setiap X Jam/Menit)**

```javascript
{
  "mode": "interval",
  "hours": 0,
  "minutes": 30   // Setiap 30 menit
}
```

✅ Cocok untuk: Update berkala

##### Mode 4: **Custom Cron**

```javascript
{
  "mode": "custom",
  "cron": "0 8,12,18 * * *"  // Jam 8 pagi, 12 siang, 6 sore
}
```

✅ Cocok untuk: Jadwal khusus

**Contoh Cron:**

- `0 8 * * *` = Setiap hari jam 8 pagi
- `0 */2 * * *` = Setiap 2 jam
- `30 9 * * 1-5` = Jam 9:30 Senin-Jumat
- `0 0 1 * *` = Tanggal 1 setiap bulan jam 00:00

#### **Step 4: Test Manual Trigger**

```javascript
// POST ke /api/scheduler/run-now
// Akan langsung menjalankan crawl sekali
```

#### **Step 5: Monitor Status**

```javascript
// GET ke /api/scheduler/status
// Response:
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

#### **Step 6: Stop Scheduler (jika perlu)**

```javascript
// POST ke /api/scheduler/stop
```

---

## 🎯 Cara 2: Windows Task Scheduler - **Untuk Auto-Start di Windows**

### ✅ Kelebihan:

- 🔄 Auto-start saat komputer nyala
- 💪 Berjalan meski user logout
- 🛡️ Built-in Windows, no additional software

### 📝 Langkah-langkah:

#### **Step 1: Buat Script Runner**

Buat file `start_crawler.bat`:

```batch
@echo off
cd /d C:\Users\IPDS-OCID\crawlSeruti
call .venv\Scripts\activate.bat
python run.py
```

#### **Step 2: Setup Task Scheduler**

1. **Buka Task Scheduler:**

   - Windows Key + R
   - Ketik: `taskschd.msc`
   - Enter

2. **Create Task:**

   - Klik "Create Basic Task"
   - Name: `Seruti Crawler Auto`
   - Description: `Auto crawl BPS Seruti`

3. **Trigger:**

   - When: `When the computer starts` (auto-start)
   - Atau: `Daily` at specific time

4. **Action:**

   - Action: `Start a program`
   - Program: `C:\Users\IPDS-OCID\crawlSeruti\start_crawler.bat`

5. **Settings:**
   - ✅ Allow task to be run on demand
   - ✅ Run task as soon as possible after scheduled start
   - ✅ If task fails, restart every: 5 minutes

#### **Step 3: Test Manual Run**

- Right-click task → "Run"
- Check: http://localhost:5000

---

## 🎯 Cara 3: Python Script Standalone (Paling Simple)

### ✅ Kelebihan:

- 🎯 Sederhana, satu script saja
- 🔧 Mudah di-custom
- 📦 Tidak perlu Flask running

### 📝 File: `auto_crawl.py`

```python
"""
Script standalone untuk auto crawl
Jalankan dengan: python auto_crawl.py
"""
from app.crawler import SerutiCrawler
from app.config import Config
import logging
from datetime import datetime
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def auto_crawl():
    """Run single crawl"""
    logging.info("🤖 AUTO CRAWL STARTED")

    try:
        crawler = SerutiCrawler(
            username=Config.USERNAME,
            password=Config.PASSWORD,
            headless=True  # Headless untuk automation
        )

        result = crawler.run_full_crawl(
            target_url=Config.TARGET_URL,
            download_url=Config.DOWNLOAD_URL
        )

        if result['success']:
            logging.info(f"✅ SUCCESS: {result['message']}")
        else:
            logging.warning(f"⚠️ FAILED: {result['message']}")

    except Exception as e:
        logging.error(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    # Mode 1: Run once
    auto_crawl()

    # Mode 2: Run loop (uncomment below)
    # while True:
    #     auto_crawl()
    #     time.sleep(1800)  # Sleep 30 menit (1800 detik)
```

#### **Jalankan via Task Scheduler:**

- Program: `C:\Users\IPDS-OCID\crawlSeruti\.venv\Scripts\python.exe`
- Arguments: `C:\Users\IPDS-OCID\crawlSeruti\auto_crawl.py`
- Start in: `C:\Users\IPDS-OCID\crawlSeruti`

---

## 🎯 Cara 4: Docker + Cron (Advanced)

### ✅ Kelebihan:

- 🐳 Isolated environment
- ☁️ Deploy ke server easily
- 📦 Portable

### 📝 File: `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Chrome & ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Setup cron
RUN apt-get update && apt-get install -y cron
COPY crontab /etc/cron.d/crawler-cron
RUN chmod 0644 /etc/cron.d/crawler-cron
RUN crontab /etc/cron.d/crawler-cron

CMD cron && tail -f /var/log/cron.log
```

### 📝 File: `crontab`

```cron
0 8 * * * cd /app && python auto_crawl.py >> /var/log/cron.log 2>&1
```

---

## 📊 Perbandingan Methods

| Method                | Kompleksitas  | Auto-Start | Monitoring | Best For             |
| --------------------- | ------------- | ---------- | ---------- | -------------------- |
| **Python Scheduler**  | ⭐⭐ Easy     | ❌ Manual  | ✅ Web UI  | Development          |
| **Task Scheduler**    | ⭐⭐⭐ Medium | ✅ Yes     | ⚠️ Limited | Production (Windows) |
| **Standalone Script** | ⭐ Very Easy  | ❌ Manual  | ❌ No      | Quick jobs           |
| **Docker + Cron**     | ⭐⭐⭐⭐ Hard | ✅ Yes     | ⚠️ Logs    | Cloud/Server         |

---

## 🚀 Rekomendasi Implementasi

### **Untuk Development/Testing:**

✅ **Gunakan Python Scheduler (Cara 1)**

- Mudah diatur via web
- Real-time monitoring
- Flexible scheduling

### **Untuk Production (Local Server):**

✅ **Gunakan Task Scheduler (Cara 2)**

- Auto-start saat PC nyala
- Reliable
- No dependencies

### **Untuk Cloud/Remote Server:**

✅ **Gunakan Docker + Cron (Cara 4)**

- Portable
- Isolated
- Easy deployment

---

## 🔧 Troubleshooting

### ❌ Scheduler tidak jalan

**Cek:**

```python
# GET /api/scheduler/status
# is_running harus True
```

**Fix:**

```python
# POST /api/scheduler/start
{
  "mode": "daily",
  "hour": 8,
  "minute": 0
}
```

### ❌ Crawl gagal saat auto mode

**Kemungkinan:**

- `DOWNLOAD_URL` belum dikonfigurasi
- Credentials salah
- Website error

**Cek logs:**

```powershell
# Lihat terminal output
# Atau check logs/ folder
```

### ❌ Task Scheduler tidak start app

**Cek:**

- Path di `.bat` file harus absolute
- User account harus punya permission
- "Run with highest privileges" di-enable

---

## 📝 Next Steps

1. ✅ **Setup scheduler** (pilih Cara 1-4)
2. ✅ **Konfigurasi `DOWNLOAD_URL`** di `.env`
3. ✅ **Test manual trigger** dulu
4. ✅ **Monitor logs** untuk memastikan success
5. ✅ **Setup alerts** (optional - email/telegram notification)

---

## 💡 Tips Pro

1. **Gunakan `headless=True`** untuk auto mode (lebih ringan)
2. **Setup retry logic** jika crawl gagal
3. **Backup downloads** secara berkala
4. **Monitor disk space** (downloads bisa besar)
5. **Log rotation** untuk mencegah log terlalu besar

---

**🎉 Selamat! Crawler Anda sekarang bisa berjalan otomatis!**
