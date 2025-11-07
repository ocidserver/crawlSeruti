# 🎯 Quick Guide: Testing vs Production Mode

## 📋 Ringkasan Singkat

**Saat ini (November 2025):**

- ✅ Gunakan `test_triwulan3.py` untuk download **Triwulan III** (testing)
- ⚠️ Triwulan IV belum tersedia di sistem

**Masa depan (operasi normal):**

- ✅ Gunakan `test_seruti_flow.py` atau `auto_crawl.py`
- 🤖 Sistem akan otomatis download sesuai periode berjalan

---

## 🧪 Mode Testing (Saat Ini)

### Download Triwulan 3

```powershell
# Jalankan test Triwulan 3
.\.venv\Scripts\python.exe test_triwulan3.py
```

**Hasil:**

```
✅ TEST PASSED!
File: Progres Entri per Kab_Kota 2025-11-07 10_46_57.xlsx
```

### Kenapa Triwulan 3?

- 📅 Saat ini November 2025 (Triwulan IV)
- ⚠️ Data Triwulan IV belum tersedia (masih ujicoba/exception)
- ✅ Data Triwulan III sudah tersedia dan bisa didownload
- 🎯 Testing mode memungkinkan pilih triwulan tertentu

---

## 🚀 Mode Production (Masa Depan)

### Auto-detect Triwulan

```powershell
# Test full flow dengan auto-detect
.\.venv\Scripts\python.exe test_seruti_flow.py

# Atau gunakan auto crawler
.\.venv\Scripts\python.exe auto_crawl.py --test
```

### Kapan Auto-detect Aktif?

Sistem akan otomatis mendeteksi dan download sesuai periode:

| Periode | Triwulan     | Bulan              |
| ------- | ------------ | ------------------ |
| **Q1**  | Triwulan I   | Januari - Maret    |
| **Q2**  | Triwulan II  | April - Juni       |
| **Q3**  | Triwulan III | Juli - September   |
| **Q4**  | Triwulan IV  | Oktober - Desember |

**Contoh:**

- 🗓️ **15 Januari 2026** → Download **Triwulan I**
- 🗓️ **20 April 2026** → Download **Triwulan II**
- 🗓️ **10 Juli 2026** → Download **Triwulan III**
- 🗓️ **5 Oktober 2026** → Download **Triwulan IV** (jika sudah tersedia)

---

## 🔧 Penggunaan Advanced

### Custom Override Triwulan

```python
from app.crawler import SerutiCrawler

crawler = SerutiCrawler(headless=False)
crawler.setup_driver()
crawler.login_seruti()
crawler.navigate_to_progres()

# Pilih triwulan tertentu
crawler.process_progres_page(override_triwulan="Triwulan I")

crawler.close()
```

### Opsi Override:

- `"Triwulan I"` - Januari s/d Maret
- `"Triwulan II"` - April s/d Juni
- `"Triwulan III"` - Juli s/d September
- `"Triwulan IV"` - Oktober s/d Desember

---

## 📊 Perbandingan Mode

| Aspek           | Testing Mode                         | Production Mode             |
| --------------- | ------------------------------------ | --------------------------- |
| **Script**      | `test_triwulan3.py`                  | `test_seruti_flow.py`       |
|                 |                                      | `auto_crawl.py`             |
| **Triwulan**    | Override manual                      | Auto-detect                 |
|                 | `"Triwulan III"`                     | Sesuai tanggal              |
| **Kapan Pakai** | Data periode saat ini belum tersedia | Operasi normal              |
| **Headless**    | `False` (lihat browser)              | `True` (background)         |
| **Log Output**  | `[TESTING MODE] Using override...`   | `Auto-detected triwulan...` |

---

## 🗓️ Timeline Penggunaan

### **Saat Ini: November 2025**

```powershell
# Gunakan testing mode
.\.venv\Scripts\python.exe test_triwulan3.py
```

→ Download **Triwulan III**

### **Januari 2026**

```powershell
# Gunakan production mode
.\.venv\Scripts\python.exe test_seruti_flow.py
```

→ Auto-download **Triwulan I**

### **April 2026**

```powershell
# Tetap production mode
.\.venv\Scripts\python.exe auto_crawl.py --test
```

→ Auto-download **Triwulan II**

---

## ✅ Checklist

### Testing (Saat Ini)

- [x] Script: `test_triwulan3.py` ready
- [x] Override: `"Triwulan III"` configured
- [x] File downloaded: `Progres Entri per Kab_Kota 2025-11-07 10_46_57.xlsx`
- [x] Log: `[TESTING MODE] Using override triwulan: Triwulan III`

### Production (Masa Depan)

- [x] Auto-detect logic implemented
- [x] Backward compatible dengan script lama
- [x] Scheduler tetap jalan dengan auto-detect
- [x] Dokumentasi lengkap tersedia

---

## 📁 File Terkait

### Testing Mode

- `test_triwulan3.py` - Test script Triwulan 3
- `TESTING_MODE.md` - Dokumentasi lengkap testing mode

### Production Mode

- `test_seruti_flow.py` - Test script auto-detect
- `auto_crawl.py` - Standalone crawler
- `app/scheduler.py` - Automated scheduler

### Dokumentasi

- `QUICK_REFERENCE.md` - Guide ini
- `SERUTI_COMPLETE_FLOW.md` - Flow lengkap
- `AUTOMATION_GUIDE.md` - Panduan automation

---

## 🆘 Troubleshooting

### "Triwulan tidak ditemukan"

```
Could not find triwulan selector
```

**Solusi:**

1. Pastikan format override benar: `"Triwulan III"` (huruf besar)
2. Tunggu page load sempurna
3. Cek screenshot di folder `logs/`

### "File tidak terdownload"

```
No new files detected in download folder
```

**Solusi:**

1. Cek koneksi internet
2. Pastikan folder `downloads/` ada
3. Tunggu lebih lama (Chrome sedang download)

### "Login gagal"

```
Login failed: Username field tidak ditemukan
```

**Solusi:**

1. Cek `.env` file
2. Pastikan `SERUTI_USERNAME=rasyidka`
3. Pastikan `SERUTI_PASSWORD` terisi

---

## 🎓 Kesimpulan

**Untuk Testing Sekarang:**

```powershell
.\.venv\Scripts\python.exe test_triwulan3.py
```

**Untuk Production Nanti:**

```powershell
.\.venv\Scripts\python.exe test_seruti_flow.py
```

**Untuk Automation:**

```powershell
# Setup Windows Task Scheduler dengan auto_crawl.py
# Sistem akan jalan otomatis sesuai jadwal
```

---

📝 **Note:** File ini adalah quick reference. Untuk detail lengkap, lihat `TESTING_MODE.md`
