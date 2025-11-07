# 🎯 Seruti Flow - Complete Guide

## 📋 Flow Lengkap Crawler

Crawler sekarang mengikuti flow spesifik website Seruti BPS:

### **Step 1: Login Page**

- URL: `https://olah.web.bps.go.id/seruti/login`
- Klik button **"Login SSO"**
  - Class: `btn btn-outline-light`
  - HTML: `<button class="btn btn-outline-light">Login SSO</button>`

### **Step 2: SSO BPS Login**

- Redirect otomatis ke: `https://sso.bps.go.id`
- Fill form:
  - **Username**: dari `.env`
  - **Password**: dari `.env`
- Klik button **Login**
  - Class: `btn btn-primary btn-block btn-lg`
  - Name: `login`

### **Step 3: Dashboard**

- Redirect ke: `https://olah.web.bps.go.id/seruti/dashboard#/`
- Wait for dashboard to load

### **Step 4: Navigate to Progres**

- Navigate ke: `https://olah.web.bps.go.id/seruti/progres#/`
- Langsung via URL atau klik menu Progres

### **Step 5: Process Progres Page**

#### 5.1 Get Kondisi Data

- Element class: `ml-2`
- Ambil info kondisi data, contoh:
  ```
  Kondisi: 2025-11-07 09:00:01
  ```
- Extract tanggal & jam update terakhir

#### 5.2 Select Tabel

- Form selector class: `form-control form-control-sm`
- Pilih opsi: **"Progres Entri per Kab/Kota"**

#### 5.3 Select Triwulan

- Form selector class: `form-control form-control-sm` (selector ke-2)
- Auto-detect triwulan berdasarkan tanggal hari ini:
  - **Januari-Maret** → Triwulan I
  - **April-Juni** → Triwulan II
  - **Juli-September** → Triwulan III
  - **Oktober-Desember** → Triwulan IV

#### 5.4 Klik Tampilkan

- Button class: `btn btn-sm btn-primary`
- Text: **"Tampilkan"**
- Wait 3 detik untuk data load

#### 5.5 Klik Export

- Button text: **"Export"**
- Wait untuk download selesai (max 30 detik)

### **Step 6: Exit**

- Browser otomatis close setelah download selesai

---

## 🔧 Konfigurasi

### File: `.env`

```env
TARGET_URL=https://olah.web.bps.go.id/seruti/login
USERNAME=your_username
PASSWORD=your_password
HEADLESS_MODE=False
```

---

## 🚀 Cara Menjalankan

### 1. **Via Test Script** (Recommended untuk testing)

```powershell
.\.venv\Scripts\python.exe test_seruti_flow.py
```

**Output:**

```
🧪 TESTING SERUTI CRAWLER - NEW FLOW
======================================================================
Target URL: https://olah.web.bps.go.id/seruti/login
Username: your_username
Headless: False (untuk testing)
======================================================================

🚀 STARTING SERUTI CRAWL
======================================================================
Step 1: Login to Seruti...
🔐 Detected SSO BPS redirect, handling SSO login...
✅ SSO BPS login completed

Step 2: Navigate to Progres page...
📊 Navigating to Progres page...
✅ Successfully navigated to Progres page

Step 3: Processing Progres page (select & export)...
📋 Processing Progres Page
======================================================================
📅 Kondisi: 2025-11-07 09:00:01
⏰ Last Update: 2025-11-07 09:00:01
📊 Selecting table: Progres Entri per Kab/Kota
✅ Selected: Progres Entri per Kab/Kota
📅 Selecting triwulan: Triwulan IV
✅ Selected: Triwulan IV
🔘 Clicking Tampilkan button
✅ Clicked Tampilkan button
📥 Clicking Export button
✅ Clicked Export button
⏳ Waiting for download to complete...
✅ Download completed: export_progres_20251107.xlsx
======================================================================
✅ Progres page processing completed
======================================================================

📊 TEST RESULT
======================================================================
Success: True
Message: Crawl completed successfully. File: export_progres_20251107.xlsx
File: export_progres_20251107.xlsx
======================================================================

✅ TEST PASSED!
```

### 2. **Via Web Dashboard**

```powershell
# Start Flask app
.\.venv\Scripts\python.exe run.py
```

Buka browser: http://localhost:5000

- Klik **"Start Crawl"**
- Wait for process selesai
- Download file muncul di list

### 3. **Via Auto Crawl Script**

```powershell
# Run once
.\.venv\Scripts\python.exe auto_crawl.py

# Run loop (setiap 30 menit)
.\.venv\Scripts\python.exe auto_crawl.py --loop --interval 30
```

---

## 🔍 Troubleshooting

### ❌ Button "Login SSO" tidak ditemukan

**Kemungkinan:**

- Halaman belum load sempurna
- Class berubah

**Fix:**

- Check element di halaman dengan Inspect Element
- Update selector di `crawler.py` method `login_seruti()`

### ❌ Triwulan tidak ter-select

**Kemungkinan:**

- Selector triwulan sama dengan selector tabel
- Logic `get_current_triwulan()` salah

**Fix:**

- Check bulan saat ini: `datetime.now().month`
- Verifikasi range triwulan sudah benar

### ❌ Export button tidak ditemukan

**Kemungkinan:**

- Data belum load setelah klik Tampilkan
- Button text berubah atau ada icon

**Fix:**

- Increase wait time setelah Tampilkan
- Check XPath button Export di halaman

### ❌ Download tidak muncul di folder

**Kemungkinan:**

- Download masih in progress
- Folder download salah
- Pop-up blocker

**Fix:**

```powershell
# Check download folder
Get-ChildItem -Path "downloads" | Sort-Object LastWriteTime -Descending

# Check Chrome download settings
# chrome://settings/downloads
```

---

## 📊 Element Selectors Reference

| Element           | Selector Type | Value                                      |
| ----------------- | ------------- | ------------------------------------------ |
| Login SSO Button  | Class         | `btn btn-outline-light`                    |
| SSO Username      | ID/Name       | `username`, `user`, `userId` (auto-detect) |
| SSO Password      | Type          | `input[type="password"]`                   |
| SSO Login Button  | Class         | `btn btn-primary btn-block btn-lg`         |
| Kondisi Data      | Class         | `ml-2`                                     |
| Tabel Selector    | Class         | `form-control form-control-sm` (1st)       |
| Triwulan Selector | Class         | `form-control form-control-sm` (2nd)       |
| Tampilkan Button  | Class         | `btn btn-sm btn-primary`                   |
| Export Button     | XPath         | `//button[contains(text(), 'Export')]`     |

---

## 💡 Tips

1. **Set `HEADLESS_MODE=False`** untuk testing awal

   - Bisa lihat prosesnya secara visual
   - Debug lebih mudah

2. **Check logs** di `logs/app.log`

   - Lihat detail setiap step
   - Error messages lengkap

3. **Screenshot otomatis** saat error

   - Saved di `logs/` folder
   - Filename: `error_YYYYMMDD_HHMMSS.png`

4. **Test manual dulu** sebelum automation
   - Pastikan flow berhasil
   - Verify download file

---

## 🎯 Next Steps

1. ✅ **Test flow manual** dengan `test_seruti_flow.py`
2. ✅ **Verify downloaded file** di folder `downloads/`
3. ✅ **Setup automation** (lihat `STEP_BY_STEP_AUTOMATION.md`)
4. ✅ **Monitor logs** untuk memastikan tidak ada error

---

**🎉 Flow sudah siap digunakan!**

Lihat juga:

- [README.md](README.md) - Overview aplikasi
- [STEP_BY_STEP_AUTOMATION.md](STEP_BY_STEP_AUTOMATION.md) - Setup automation
- [SSO_GUIDE.md](SSO_GUIDE.md) - SSO BPS handling
