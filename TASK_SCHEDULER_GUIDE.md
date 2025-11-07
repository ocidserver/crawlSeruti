# 📅 Task Scheduler & Auto-Retry System

## 🎯 Overview

Sistem scheduler baru memungkinkan Anda untuk:

1. **Menjadwalkan crawling** dari tanggal A ke tanggal B pada jam tertentu
2. **Auto-retry** jika terjadi kegagalan
3. **Manage jadwal** melalui UI web yang user-friendly

---

## 🚀 Fitur Utama

### 1. **Scheduled Jobs dengan Date Range**

- Set tanggal mulai dan tanggal selesai
- Tentukan jam eksekusi (contoh: 09:05 setiap hari)
- Otomatis berhenti setelah tanggal selesai

### 2. **Auto-Retry Mechanism**

- Retry otomatis jika crawling gagal
- Konfigurasi max retry (default: 3x)
- Konfigurasi delay antar retry (default: 300 detik / 5 menit)
- Status tracking untuk setiap retry

### 3. **Web UI untuk Management**

- Tambah jadwal baru
- Lihat daftar jadwal aktif
- Hapus jadwal
- Monitor status (success, failed, retrying)
- Real-time update

---

## 📖 Cara Menggunakan

### A. Melalui Web UI

#### 1. **Akses Task Scheduler**

```
http://localhost:5000/scheduler
```

#### 2. **Tambah Jadwal Baru**

**Form Input:**

- **Nama Jadwal**: Contoh: "Crawl Pagi Hari"
- **Tanggal Mulai**: 2025-11-08 (besok)
- **Tanggal Selesai**: 2025-12-31 (akhir tahun)
- **Jam**: 09 (pukul 09 pagi)
- **Menit**: 05 (menit ke-5)
- **Max Retry**: 3 (coba 3x jika gagal)
- **Delay Retry**: 300 detik (tunggu 5 menit antar retry)

**Hasil:**
Sistem akan menjalankan crawl setiap hari pukul **09:05** mulai tanggal **8 Nov 2025** sampai **31 Des 2025**.

#### 3. **Monitor Status**

Di UI akan muncul card untuk setiap jadwal yang menampilkan:

- **Nama & Status** (Active, Success, Failed, Retrying)
- **Jadwal** (09:05)
- **Periode** (2025-11-08 s/d 2025-12-31)
- **Next Run** (kapan eksekusi berikutnya)
- **Last Run** (terakhir dijalankan kapan)
- **Retry Config** (Max 3x, Delay 300s)
- **Last Message** (status terakhir)

#### 4. **Hapus Jadwal**

Klik tombol **trash icon** di setiap card jadwal, konfirmasi, dan jadwal akan dihapus.

---

### B. Melalui API

#### 1. **Tambah Jadwal Baru**

```bash
curl -X POST http://localhost:5000/api/scheduler/job/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Crawl Pagi Hari",
    "start_date": "2025-11-08",
    "end_date": "2025-12-31",
    "hour": 9,
    "minute": 5,
    "max_retries": 3,
    "retry_delay": 300
  }'
```

**Response:**

```json
{
  "success": true,
  "message": "✅ Job 'Crawl Pagi Hari' berhasil ditambahkan",
  "job_id": "job_20251107110530"
}
```

#### 2. **Lihat Semua Jadwal**

```bash
curl http://localhost:5000/api/scheduler/jobs
```

**Response:**

```json
{
  "success": true,
  "jobs": [
    {
      "id": "job_20251107110530",
      "name": "Crawl Pagi Hari",
      "schedule": "09:05",
      "start_date": "2025-11-08",
      "end_date": "2025-12-31",
      "next_run": "2025-11-08 09:05:00",
      "last_run": null,
      "status": "active",
      "max_retries": 3,
      "retry_delay": 300
    }
  ]
}
```

#### 3. **Hapus Jadwal**

```bash
curl -X DELETE http://localhost:5000/api/scheduler/job/job_20251107110530
```

#### 4. **Update Retry Config Global**

```bash
curl -X POST http://localhost:5000/api/scheduler/retry-config \
  -H "Content-Type: application/json" \
  -d '{
    "max_retries": 5,
    "retry_delay": 600
  }'
```

---

## 🔄 Auto-Retry Logic

### Alur Kerja:

```
1. Jadwal tereksekusi → Crawl dimulai
                         ↓
                    Berhasil? ────── YES ──→ Done ✅
                         ↓ NO
                         ↓
2. Cek retry count < max_retries?
                         ↓ YES
                         ↓
3. Tunggu retry_delay (default: 5 menit)
                         ↓
4. Retry attempt 1/3 → Crawl lagi
                         ↓
                    Berhasil? ────── YES ──→ Done ✅
                         ↓ NO
                         ↓
5. Retry attempt 2/3 → Crawl lagi
                         ↓
                    Berhasil? ────── YES ──→ Done ✅
                         ↓ NO
                         ↓
6. Retry attempt 3/3 → Crawl lagi
                         ↓
                    Berhasil? ────── YES ──→ Done ✅
                         ↓ NO
                         ↓
7. Max retries reached → Failed ❌
```

### Status Tracking:

| Status       | Deskripsi                             |
| ------------ | ------------------------------------- |
| **active**   | Jadwal aktif, belum pernah dijalankan |
| **success**  | Eksekusi terakhir berhasil            |
| **failed**   | Eksekusi gagal setelah max retries    |
| **retrying** | Sedang dalam proses retry             |

### Log Output:

**Retry Attempt 1:**

```
🔄 AUTO CRAWL FAILED: Download failed
🔄 Scheduling retry 1 in 300 seconds...
```

**Retry Attempt 2:**

```
🤖 AUTO CRAWL STARTED
Job ID: job_20251107110530
🔄 Retry attempt: 2/3
```

**Max Retries Reached:**

```
❌ Max retries reached for job job_20251107110530
```

---

## 📊 Contoh Use Cases

### Use Case 1: Daily Morning Crawl

**Requirement:** Crawl setiap pagi jam 09:05 selama 1 bulan

**Setting:**

- Nama: "Daily Morning Crawl"
- Start: 2025-11-08
- End: 2025-12-07
- Waktu: 09:05
- Retry: 3x, delay 5 menit

**Hasil:**
Sistem akan crawl otomatis setiap pagi jam 09:05 dari 8 Nov - 7 Des 2025. Jika gagal, akan retry sampai 3x dengan jeda 5 menit.

---

### Use Case 2: Weekly Report (Setiap Senin)

**Requirement:** Crawl setiap Senin jam 10:00

**Catatan:** Untuk spesifik hari dalam seminggu, gunakan Custom Cron:

```bash
curl -X POST http://localhost:5000/api/scheduler/start \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "custom",
    "cron": "0 10 * * 1"
  }'
```

(0 10 \* \* 1 = menit 0, jam 10, setiap hari, setiap bulan, hari Senin)

---

### Use Case 3: High Priority dengan Retry Agresif

**Requirement:** Crawl harus berhasil, retry sampai 10x

**Setting:**

- Max Retry: 10
- Delay: 60 detik (1 menit)

**Hasil:**
Jika gagal, sistem akan retry sampai 10x dengan jeda 1 menit antar retry.

---

## 🛠️ Konfigurasi File

### scheduler_jobs.json

File ini menyimpan konfigurasi semua jadwal:

```json
[
  {
    "id": "job_20251107110530",
    "name": "Crawl Pagi Hari",
    "start_date": "2025-11-08",
    "end_date": "2025-12-31",
    "hour": 9,
    "minute": 5,
    "max_retries": 3,
    "retry_delay": 300,
    "status": "active",
    "created_at": "2025-11-07 11:05:30",
    "last_run": null,
    "last_message": null
  }
]
```

File ini otomatis dibuat dan diupdate oleh sistem.

---

## 📝 API Endpoints Reference

### Jobs Management

| Method | Endpoint                      | Deskripsi            |
| ------ | ----------------------------- | -------------------- |
| GET    | `/scheduler`                  | Halaman UI scheduler |
| GET    | `/api/scheduler/jobs`         | List semua jobs      |
| POST   | `/api/scheduler/job/add`      | Tambah job baru      |
| GET    | `/api/scheduler/job/<job_id>` | Detail job           |
| DELETE | `/api/scheduler/job/<job_id>` | Hapus job            |
| POST   | `/api/scheduler/retry-config` | Update retry config  |

### Legacy Endpoints (Still Available)

| Method | Endpoint                 | Deskripsi                                      |
| ------ | ------------------------ | ---------------------------------------------- |
| POST   | `/api/scheduler/start`   | Start scheduler (daily/hourly/interval/custom) |
| POST   | `/api/scheduler/stop`    | Stop scheduler                                 |
| GET    | `/api/scheduler/status`  | Get status                                     |
| POST   | `/api/scheduler/run-now` | Trigger manual run                             |

---

## 🎯 Best Practices

### 1. **Setting Waktu Eksekusi**

- Pilih jam dengan traffic rendah (contoh: dini hari)
- Hindari bentrok dengan maintenance server
- Pertimbangkan timezone server

### 2. **Retry Configuration**

- **Conservative** (production):
  - Max retry: 3
  - Delay: 300s (5 menit)
- **Aggressive** (critical task):
  - Max retry: 5-10
  - Delay: 60-120s (1-2 menit)
- **Minimal** (testing):
  - Max retry: 1
  - Delay: 60s

### 3. **Monitoring**

- Check UI scheduler secara berkala
- Review logs di folder `logs/`
- Monitor success rate

### 4. **Cleanup**

- Hapus jadwal yang sudah selesai
- Archive file `scheduler_jobs.json` periodic
- Review dan optimize retry config

---

## 🐛 Troubleshooting

### Problem: Jadwal tidak berjalan

**Cek:**

1. Server Flask running?

   ```bash
   curl http://localhost:5000/api/scheduler/status
   ```

2. Jadwal sudah lewat start_date?
3. Lihat logs untuk error

**Solusi:**

- Restart server: `python run.py`
- Re-add jadwal jika perlu

---

### Problem: Retry terus menerus

**Cek:**

- Apakah credentials benar?
- Network stabil?
- Target URL accessible?

**Solusi:**

- Fix root cause (credentials, network)
- Atau temporary disable retry:
  ```json
  { "max_retries": 0 }
  ```

---

### Problem: Performance lambat

**Cek:**

- Berapa banyak jadwal aktif?
- Apakah retry delay terlalu kecil?

**Solusi:**

- Limit concurrent jobs
- Increase retry delay
- Optimize crawler code

---

## 📈 Monitoring & Logs

### Log File Location

```
logs/crawler_YYYYMMDD.log
```

### Log Format

```
2025-11-07 09:05:00 - INFO - 🤖 AUTO CRAWL STARTED
2025-11-07 09:05:00 - INFO - Job ID: job_20251107110530
2025-11-07 09:05:45 - INFO - ✅ AUTO CRAWL SUCCESS
```

### Status Monitoring

Cek via UI atau API:

```bash
curl http://localhost:5000/api/scheduler/jobs
```

---

## ✅ Summary

**Fitur Baru:**
✅ Schedule dari tanggal A ke B  
✅ Set jam eksekusi spesifik  
✅ Auto-retry dengan konfigurasi  
✅ Web UI untuk management  
✅ Real-time status monitoring  
✅ API endpoints lengkap

**Files Involved:**

- `app/scheduler.py` - Core scheduler logic
- `app/routes.py` - API endpoints
- `app/templates/scheduler.html` - Web UI
- `scheduler_jobs.json` - Jobs storage

**Access Points:**

- Web UI: http://localhost:5000/scheduler
- API: http://localhost:5000/api/scheduler/\*

**Dokumentasi:**

- Setup: Lihat bagian "Cara Menggunakan"
- API: Lihat bagian "API Endpoints Reference"
- Troubleshooting: Lihat bagian "Troubleshooting"

---

📝 **Created:** 2025-11-07  
👤 **Author:** Copilot  
✅ **Status:** Production Ready
