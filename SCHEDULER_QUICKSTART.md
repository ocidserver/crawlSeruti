# 🚀 Quick Start - Task Scheduler

## ⚡ 3 Langkah Mudah

### 1️⃣ Akses Scheduler UI

```
http://localhost:5000/scheduler
```

### 2️⃣ Isi Form Jadwal

```
Nama Jadwal   : Crawl Pagi Hari
Tanggal Mulai : 2025-11-08
Tanggal Selesai: 2025-12-31
Jam           : 09
Menit         : 05
Max Retry     : 3
Delay Retry   : 300 (5 menit)
```

### 3️⃣ Klik "Tambah Jadwal"

✅ Done! Sistem akan crawl otomatis setiap hari jam 09:05

---

## 📋 Contoh Setting Populer

### Crawl Harian Pagi

```
⏰ 09:05 setiap hari
📅 1 bulan (Nov - Des)
🔄 Retry 3x jika gagal
⏳ Delay 5 menit antar retry
```

### Crawl Siang Hari

```
⏰ 13:00 setiap hari
📅 3 bulan
🔄 Retry 5x (aggressive)
⏳ Delay 2 menit
```

### Crawl Malam (Low Traffic)

```
⏰ 23:00 setiap hari
📅 Permanen (end date jauh)
🔄 Retry 3x
⏳ Delay 10 menit
```

---

## 🎯 Fitur Utama

✅ **Jadwal Otomatis** - Set dan lupakan  
✅ **Auto-Retry** - 3x percobaan ulang otomatis  
✅ **Date Range** - Dari tanggal A ke B  
✅ **Web UI** - Manage via browser  
✅ **Status Tracking** - Monitor real-time

---

## 🔄 Auto-Retry Explained

```
Crawl Start → Gagal → Tunggu 5 menit → Retry 1/3
                                         ↓
                                      Gagal → Retry 2/3
                                         ↓
                                      Gagal → Retry 3/3
                                         ↓
                                 Berhasil ✅ atau Failed ❌
```

**Default Setting:**

- Max Retry: **3x**
- Delay: **300 detik** (5 menit)

---

## 📊 Status Badge

| Badge           | Arti                     |
| --------------- | ------------------------ |
| 🔵 **Active**   | Jadwal aktif, siap jalan |
| 🟢 **Success**  | Terakhir berhasil        |
| 🔴 **Failed**   | Gagal setelah max retry  |
| 🟡 **Retrying** | Sedang retry             |

---

## 🛠️ Quick API Commands

### Tambah Jadwal via cURL

```bash
curl -X POST http://localhost:5000/api/scheduler/job/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Crawl Pagi",
    "start_date": "2025-11-08",
    "end_date": "2025-12-31",
    "hour": 9,
    "minute": 5,
    "max_retries": 3,
    "retry_delay": 300
  }'
```

### Lihat Semua Jadwal

```bash
curl http://localhost:5000/api/scheduler/jobs
```

### Hapus Jadwal

```bash
curl -X DELETE http://localhost:5000/api/scheduler/job/{job_id}
```

---

## ⚠️ Tips Penting

### DO ✅

- Set tanggal mulai = besok (bukan hari ini)
- Gunakan jam dengan traffic rendah
- Test dulu dengan 1 jadwal
- Monitor logs secara berkala
- Set retry delay minimum 5 menit

### DON'T ❌

- Jangan buat terlalu banyak jadwal sekaligus
- Jangan set retry delay < 60 detik
- Jangan lupa monitoring
- Jangan set end_date terlalu jauh jika testing

---

## 📁 File Locations

```
scheduler_jobs.json          ← Job configurations
logs/crawler_YYYYMMDD.log   ← Execution logs
downloads/                   ← Downloaded files
```

---

## 🔗 Links

- **Scheduler UI**: http://localhost:5000/scheduler
- **Main Dashboard**: http://localhost:5000/
- **Full Documentation**: TASK_SCHEDULER_GUIDE.md

---

## 🆘 Quick Troubleshooting

### Jadwal tidak jalan?

```bash
# Cek server running
curl http://localhost:5000/api/scheduler/status

# Restart server
python run.py
```

### Retry terus menerus?

```
1. Cek credentials di .env
2. Cek koneksi internet
3. Review logs untuk error detail
```

### Tidak bisa tambah jadwal?

```
1. Pastikan semua field terisi
2. Cek format tanggal (YYYY-MM-DD)
3. Jam 0-23, Menit 0-59
```

---

✅ **Ready to Use!**  
📖 **Full Guide:** TASK_SCHEDULER_GUIDE.md  
🎯 **Let the automation begin!**
