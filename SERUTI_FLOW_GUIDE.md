# 🎯 Seruti BPS - Specific Flow Guide

## 📋 Flow Otomatis Seruti BPS

Crawler telah dikonfigurasi dengan flow spesifik untuk Seruti BPS:

---

## 🔄 Alur Proses (Automatic)

### **Step 1: Buka Halaman Login**

```
URL: https://olah.web.bps.go.id/seruti/login
```

### **Step 2: Klik Button "Login SSO"**

```html
<button class="btn btn-outline-light">Login SSO</button>
```

✅ Crawler otomatis detect dan klik button ini

### **Step 3: Isi Form SSO**

- **Username Field**: Auto-detect (input type text/email)
- **Password Field**: Auto-detect (input type password)
- **Credentials**: Dari file `.env`

```env
USERNAME=rasyidka
PASSWORD=muthiamylady13
```

### **Step 4: Klik Button Login**

```html
<button class="btn btn-primary btn-block btn-lg" name="login">Login</button>
```

✅ Crawler otomatis detect dan klik button ini

### **Step 5: Redirect ke Dashboard**

```
URL: https://olah.web.bps.go.id/seruti/dashboard#/
```

✅ Crawler otomatis tunggu redirect

### **Step 6: Navigate ke Progres**

```
URL: https://olah.web.bps.go.id/seruti/progres#/
```

✅ Crawler otomatis pindah ke halaman Progres

---

## 🚀 Cara Menggunakan

### **Option 1: Via Test Script (Recommended untuk First Time)**

```powershell
# Test dengan browser visible (untuk lihat prosesnya)
.\.venv\Scripts\python.exe test_seruti_flow.py
```

**Output yang diharapkan:**

```
======================================================================
🧪 TESTING SERUTI CRAWLER - NEW FLOW
======================================================================
Target URL: https://olah.web.bps.go.id/seruti/login
Username: rasyidka
Headless: False (untuk testing)
======================================================================

🌐 Navigating to Seruti: https://olah.web.bps.go.id/seruti/login
🔍 Looking for 'Login SSO' button...
✅ Found 'Login SSO' button, clicking...
📝 Filling SSO login form...
   - Finding username field...
   ✅ Username filled: rasyidka
   - Finding password field...
   ✅ Password filled
🔘 Looking for login submit button...
✅ Found login button (by name='login'), clicking...
⏳ Waiting for login to complete...
✅ Login successful! Redirected to dashboard
📊 Navigating to Progres page...
✅ Successfully navigated to Progres page
📸 Screenshot saved: logs/progres_page_20241107_123045.png

======================================================================
📊 TEST RESULT
======================================================================
Success: True
Message: Successfully navigated to Progres page (no download performed)
Screenshots: progres_page_20241107_123045.png
======================================================================

✅ TEST PASSED!
```

---

### **Option 2: Via Web Dashboard**

1. **Start Flask app:**

   ```powershell
   .\.venv\Scripts\python.exe run.py
   ```

2. **Buka browser:** http://localhost:5000

3. **Klik "Start Crawl"**
   - Username & Password sudah otomatis dari `.env`
   - Crawler akan otomatis:
     - Klik "Login SSO"
     - Isi form
     - Klik login
     - Navigate ke Progres

---

### **Option 3: Via Automation Script**

```powershell
# Run once dengan flow baru
.\.venv\Scripts\python.exe auto_crawl.py

# Run loop setiap 30 menit
.\.venv\Scripts\python.exe auto_crawl.py --loop --interval 30
```

---

## 🎨 Kustomisasi Download

Jika ingin tambahkan download di halaman Progres:

### **1. Inspect Element di Halaman Progres**

- Buka https://olah.web.bps.go.id/seruti/progres#/
- Cari button/link download
- Inspect → Copy XPath

### **2. Update `.env`**

```env
DOWNLOAD_URL=https://olah.web.bps.go.id/seruti/progres#/
# DOWNLOAD_BUTTON_XPATH akan ditambahkan di update berikutnya
```

### **3. Update `crawler.py`** (jika perlu custom logic)

Tambahkan method `download_from_progres()`:

```python
def download_from_progres(self):
    """Download file dari halaman Progres"""
    # Custom logic untuk download dari progres page
    pass
```

---

## 📝 Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     SERUTI CRAWL FLOW                       │
└─────────────────────────────────────────────────────────────┘

  ┌──────────────────────────┐
  │  1. Open Login Page      │
  │  /seruti/login           │
  └─────────┬────────────────┘
            │
            ▼
  ┌──────────────────────────┐
  │  2. Click "Login SSO"    │
  │  class="btn-outline-light"│
  └─────────┬────────────────┘
            │
            ▼
  ┌──────────────────────────┐
  │  3. Fill SSO Form        │
  │  - Username (auto-detect)│
  │  - Password (auto-detect)│
  └─────────┬────────────────┘
            │
            ▼
  ┌──────────────────────────┐
  │  4. Click Login Button   │
  │  class="btn-primary..."  │
  │  name="login"            │
  └─────────┬────────────────┘
            │
            ▼
  ┌──────────────────────────┐
  │  5. Wait for Redirect    │
  │  → Dashboard             │
  └─────────┬────────────────┘
            │
            ▼
  ┌──────────────────────────┐
  │  6. Navigate to Progres  │
  │  /seruti/progres#/       │
  └─────────┬────────────────┘
            │
            ▼
  ┌──────────────────────────┐
  │  7. Screenshot & Done    │
  │  (atau download file)    │
  └──────────────────────────┘
```

---

## 🔧 Troubleshooting

### ❌ Button "Login SSO" tidak ditemukan

**Kemungkinan:**

- Halaman sudah langsung redirect ke SSO
- Class button berbeda

**Solusi:**

```python
# Crawler akan skip dan lanjut ke fill form SSO
# No action needed - sudah di-handle otomatis
```

### ❌ Login button tidak ditemukan

**Kemungkinan:**

- Button punya attribute berbeda
- Form struktur berubah

**Solusi:**
Cek element di browser:

```powershell
# Buka DevTools (F12)
# Inspect login button
# Copy HTML
```

### ❌ Stuck di SSO page setelah login

**Kemungkinan:**

- Credentials salah
- SSO timeout

**Solusi:**

```powershell
# Cek credentials di .env
# Test manual login dulu
```

**Screenshot otomatis disimpan di:**

```
logs/sso_still_on_page_YYYYMMDD_HHMMSS.png
```

---

## 📊 Monitoring

### Lihat Logs

```powershell
# Real-time log
Get-Content -Path "logs\crawler_20241107.log" -Wait -Tail 50

# Last 100 lines
Get-Content -Path "logs\crawler_20241107.log" -Tail 100
```

### Screenshot Locations

```
logs/
  ├── login_error_20241107_123045.png
  ├── progres_page_20241107_123050.png
  └── sso_still_on_page_20241107_123048.png
```

---

## ✅ Checklist Pre-Run

- [ ] `.env` file configured with correct credentials
- [ ] Chrome browser installed
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test manual login works on website
- [ ] Run test script first: `python test_seruti_flow.py`

---

## 🎉 Next Steps

Setelah flow login & navigate ke Progres berhasil:

1. **Identifikasi Download Button** di halaman Progres
2. **Update crawler** untuk auto-download
3. **Setup automation** untuk run berkala
4. **Configure alerts** (email/telegram) untuk notifikasi

---

**📚 Related Documentation:**

- [README.md](README.md) - Main documentation
- [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) - Automation setup
- [STEP_BY_STEP_AUTOMATION.md](STEP_BY_STEP_AUTOMATION.md) - Step-by-step guide
