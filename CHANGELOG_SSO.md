# ✅ UPDATE: SSO BPS Support Added!

## 🎉 Apa yang Baru?

Crawler Anda sekarang **otomatis support SSO BPS**!

Ketika target URL (misalnya `https://olah.web.bps.go.id/seruti/login`) redirect ke **SSO BPS** (`https://sso.bps.go.id`), crawler akan:

1. ✅ **Otomatis detect** redirect ke SSO BPS
2. ✅ **Smart field detection** - Mencoba berbagai kemungkinan selector untuk username/password/submit button
3. ✅ **Auto-fill credentials** dari file `.env`
4. ✅ **Submit form** SSO secara otomatis
5. ✅ **Wait for redirect** kembali ke aplikasi target
6. ✅ **Continue** proses download

---

## 📝 Yang Sudah Ditambahkan

### 1. **Enhanced Crawler Engine** (`app/crawler.py`)

- ✅ Method `_handle_sso_bps_login()` khusus untuk SSO BPS
- ✅ Deteksi otomatis redirect ke `sso.bps.go.id`
- ✅ Multiple selector strategies untuk field detection
- ✅ Screenshot otomatis saat error untuk debugging

### 2. **Dokumentasi Lengkap**

- ✅ `SSO_GUIDE.md` - Panduan lengkap SSO BPS
- ✅ `QUICKSTART_SSO.md` - Quick start guide 5 menit
- ✅ `README.md` - Updated dengan info SSO
- ✅ `CHANGELOG_SSO.md` - File ini

### 3. **UI Update**

- ✅ Banner SSO info di dashboard
- ✅ Visual indicator bahwa SSO supported

### 4. **Testing Tools**

- ✅ `test_setup.py` - Automated setup verification

---

## 🚀 Cara Menggunakan

### Quick Start (5 Menit)

1. **Pastikan .env sudah diisi:**

   ```env
   TARGET_URL=https://olah.web.bps.go.id/seruti/login
   USERNAME=username_bps_anda
   PASSWORD=password_bps_anda
   HEADLESS_MODE=False
   ```

2. **Test setup:**

   ```powershell
   .venv\Scripts\python.exe test_setup.py
   ```

3. **Jalankan aplikasi:**

   ```powershell
   .venv\Scripts\python.exe run.py
   ```

4. **Buka browser:**
   - Akses: http://localhost:5000
   - Klik "Start Crawl"
   - Lihat browser otomatis handle SSO!

---

## 🔍 Cara Kerja SSO Detection

```python
# Pseudocode flow
1. User klik "Start Crawl" dengan TARGET_URL
2. Browser navigate ke TARGET_URL
3. Check current_url setelah navigation
4. IF 'sso.bps.go.id' in current_url:
     → Activate SSO handler
     → Try berbagai selector untuk find username field
     → Fill username
     → Try berbagai selector untuk find password field
     → Fill password
     → Try berbagai selector untuk find submit button
     → Click submit
     → Wait for redirect
     → Continue to download process
5. ELSE:
     → Use standard login flow
```

---

## 🎯 Field Detection Strategy

SSO handler mencoba selector dalam urutan ini:

**Username Field:**

- `id="username"`
- `id="user"`
- `id="email"`
- `name="username"`
- `name="user"`
- `input[type="text"]`
- dll.

**Password Field:**

- `id="password"`
- `id="pass"`
- `name="password"`
- `input[type="password"]`

**Submit Button:**

- `button[type="submit"]`
- Button dengan text "Login", "Masuk", "Sign"
- `id="submit"`
- `id="login"`
- Enter key (fallback)

---

## 🐛 Debugging

### Set Headless Mode = False

```env
HEADLESS_MODE=False
```

Ini akan show browser sehingga Anda bisa lihat apa yang terjadi.

### Check Logs

```powershell
# Lihat log hari ini
Get-Content "logs/crawler_$(Get-Date -Format 'yyyyMMdd').log" -Tail 30
```

### Check Screenshots

Saat error, screenshot otomatis tersimpan di:

- `logs/sso_login_error.png`
- `logs/sso_still_on_page.png`
- `logs/error.png`

---

## 📚 Dokumentasi

| File                | Deskripsi                |
| ------------------- | ------------------------ |
| `README.md`         | Overview project & fitur |
| `SSO_GUIDE.md`      | Panduan lengkap SSO BPS  |
| `QUICKSTART_SSO.md` | Quick start 5 menit      |
| `CHANGELOG_SSO.md`  | File ini - Update log    |
| `test_setup.py`     | Test script setup        |

---

## ✨ Example Use Cases

### Use Case 1: Seruti BPS

```env
TARGET_URL=https://olah.web.bps.go.id/seruti/login
DOWNLOAD_URL=https://olah.web.bps.go.id/seruti/download
```

### Use Case 2: Aplikasi BPS Lainnya

```env
TARGET_URL=https://app.bps.go.id/login
# Akan auto-detect SSO redirect
```

### Use Case 3: Direct SSO (jika langsung ke SSO)

```env
TARGET_URL=https://sso.bps.go.id/
# Juga akan terdeteksi dan di-handle
```

---

## 🔒 Security Notes

⚠️ **PENTING:**

- `.env` berisi credentials sensitif
- File `.env` sudah di `.gitignore`
- **JANGAN commit `.env` ke Git**
- Gunakan credentials yang aman
- Untuk production, ganti `FLASK_SECRET_KEY`

---

## 🎓 Next Steps

1. ✅ **Test dengan kredensial asli** - Pastikan SSO login berhasil
2. ✅ **Set download URL** - Konfigurasi halaman download
3. ✅ **Set download button XPath** - Jika perlu download via button
4. ✅ **Test headless mode** - Setelah yakin berjalan
5. ✅ **Schedule crawling** - Bisa tambahkan scheduler nanti

---

## 🤝 Support

Jika ada masalah:

1. **Check test setup:**

   ```powershell
   .venv\Scripts\python.exe test_setup.py
   ```

2. **Run dengan browser visible:**

   ```env
   HEADLESS_MODE=False
   ```

3. **Check logs & screenshots:**

   ```powershell
   explorer logs
   ```

4. **Baca dokumentasi:**
   - `SSO_GUIDE.md` - Troubleshooting lengkap
   - `QUICKSTART_SSO.md` - Quick tips

---

## 📊 Test Results

```
✅ All tests passed!
✅ SSO handler implemented
✅ SSO detection active
✅ All dependencies installed
✅ All files in place
```

---

**Happy Crawling with SSO BPS! 🚀**

---

_Last Updated: November 7, 2025_
