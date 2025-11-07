# 🎯 Quick Start - Automation

## 🚀 Cara Tercepat Setup Automation

### **Method 1: Via Web Dashboard** (PALING MUDAH)

1. **Pastikan app sudah running:**

   ```powershell
   .\.venv\Scripts\python.exe run.py
   ```

2. **Buka browser:** http://localhost:5000

3. **Klik tombol "Start Auto Schedule"** (akan ditambahkan ke UI)

4. **Atau gunakan curl/Postman:**

   **Daily crawl jam 8 pagi:**

   ```powershell
   curl -X POST http://localhost:5000/api/scheduler/start `
     -H "Content-Type: application/json" `
     -d '{\"mode\":\"daily\",\"hour\":8,\"minute\":0}'
   ```

   **Setiap 30 menit:**

   ```powershell
   curl -X POST http://localhost:5000/api/scheduler/start `
     -H "Content-Type: application/json" `
     -d '{\"mode\":\"interval\",\"hours\":0,\"minutes\":30}'
   ```

   **Cek status:**

   ```powershell
   curl http://localhost:5000/api/scheduler/status
   ```

---

### **Method 2: Standalone Script** (PALING SIMPLE)

**Run sekali:**

```powershell
.\.venv\Scripts\python.exe auto_crawl.py
```

**Run loop setiap 30 menit:**

```powershell
.\.venv\Scripts\python.exe auto_crawl.py --loop --interval 30
```

**Test konfigurasi:**

```powershell
.\.venv\Scripts\python.exe auto_crawl.py --test
```

---

### **Method 3: Windows Task Scheduler** (AUTO-START)

1. **Buka Task Scheduler:**

   - Windows Key + R
   - Ketik: `taskschd.msc`
   - Enter

2. **Create Basic Task:**

   - Name: `Seruti Auto Crawl`
   - Trigger: `Daily` at `08:00 AM`
   - Action: `Start a program`
   - Program: `C:\Users\IPDS-OCID\crawlSeruti\run_auto_crawl.bat`

3. **Done!** Sekarang akan auto-run setiap hari jam 8 pagi

---

## 📝 BEFORE AUTOMATION - CHECKLIST

### ⚠️ PENTING! Konfigurasi ini HARUS dilakukan:

1. **Set DOWNLOAD_URL di `.env`:**

   ```env
   # Ganti dengan URL download yang sebenarnya
   DOWNLOAD_URL=https://olah.web.bps.go.id/seruti/download-page
   ```

2. **Test manual crawl dulu:**

   - Buka http://localhost:5000
   - Klik "Start Crawl"
   - Pastikan berhasil login dan download

3. **Cek download button XPath:**
   - Buka website target
   - Inspect element tombol download
   - Catat XPath-nya
   - Sesuaikan di crawler jika perlu

---

## 🔍 Monitoring

**Cek scheduler status:**

```powershell
curl http://localhost:5000/api/scheduler/status
```

**Trigger manual:**

```powershell
curl -X POST http://localhost:5000/api/scheduler/run-now
```

**Stop scheduler:**

```powershell
curl -X POST http://localhost:5000/api/scheduler/stop
```

**View logs:**

- `logs/app.log` - Application logs
- `logs/auto_crawl.log` - Auto crawl logs

---

## 💡 Tips

1. **Gunakan headless mode untuk automation**

   - Lebih cepat
   - Tidak ganggu kerja
   - Sudah otomatis di auto mode

2. **Setup email notification** (optional)

   - Install: `pip install smtplib`
   - Tambahkan email alert jika crawl gagal

3. **Backup downloads secara berkala**
   - Buat script untuk copy ke backup folder
   - Atau setup cloud sync (Google Drive, OneDrive)

---

**🎉 Siap Digunakan!**

Baca detail lengkap di: [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)
