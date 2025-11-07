# 🔐 Panduan SSO BPS Integration

## Overview

Crawler ini sudah dilengkapi dengan kemampuan untuk menangani **SSO (Single Sign-On) BPS** secara otomatis.

## Cara Kerja

Ketika Anda mengakses website target (misalnya: `https://olah.web.bps.go.id/seruti/login`), sistem akan:

1. ✅ Membuka URL target
2. ✅ **Mendeteksi redirect ke SSO BPS** (`https://sso.bps.go.id`)
3. ✅ Otomatis menggunakan flow login SSO BPS
4. ✅ Mengisi username dan password
5. ✅ Submit form SSO
6. ✅ Menunggu redirect kembali ke aplikasi asli
7. ✅ Melanjutkan proses download

## Konfigurasi

Edit file `.env`:

```env
# Target Website (akan redirect ke SSO)
TARGET_URL=https://olah.web.bps.go.id/seruti/login

# Kredensial SSO BPS Anda
USERNAME=username_bps_anda
PASSWORD=password_bps_anda

# Untuk debugging, set False agar bisa melihat browser
HEADLESS_MODE=False
```

## Field Detection

Crawler akan mencoba berbagai kemungkinan selector untuk field SSO BPS:

### Username Field

- `id="username"`
- `id="user"`
- `id="email"`
- `name="username"`
- `name="user"`
- `input[type="text"]`

### Password Field

- `id="password"`
- `id="pass"`
- `name="password"`
- `input[type="password"]`

### Submit Button

- `button[type="submit"]`
- Button dengan text "Login", "Masuk", "Sign"
- `id="submit"`
- `id="login"`

## Testing

### 1. Test dengan Browser Terlihat (Recommended untuk pertama kali)

```env
HEADLESS_MODE=False
```

Jalankan aplikasi dan perhatikan:

- ✅ Browser akan terbuka
- ✅ Navigasi ke target URL
- ✅ Redirect ke SSO BPS
- ✅ Form diisi otomatis
- ✅ Submit dan redirect kembali

### 2. Test dengan Headless Mode

Setelah yakin berjalan, set:

```env
HEADLESS_MODE=True
```

## Troubleshooting

### ❌ "Username field tidak ditemukan di SSO BPS"

**Solusi:**

1. Set `HEADLESS_MODE=False`
2. Jalankan crawler
3. Lihat halaman SSO yang muncul
4. Klik kanan pada field username → Inspect
5. Catat `id`, `name`, atau selector CSS-nya
6. Update code di `app/crawler.py` method `_handle_sso_bps_login()`

### ❌ "Still on SSO page after login attempt"

**Kemungkinan penyebab:**

1. **Username/password salah** - Check kredensial di `.env`
2. **CAPTCHA** - SSO BPS mungkin menampilkan CAPTCHA (belum support otomatis)
3. **Field selector berubah** - Struktur halaman SSO berubah

**Debugging:**

- Check screenshot di folder `logs/sso_still_on_page.png`
- Check log file di folder `logs/`

### ❌ Login berhasil tapi download gagal

Pastikan setelah SSO redirect, URL sudah kembali ke aplikasi target. Check:

```python
# Di dashboard, lihat Current URL setelah login
```

## Advanced: Custom SSO Handling

Jika SSO BPS Anda memiliki field khusus, edit `app/crawler.py`:

```python
def _handle_sso_bps_login(self):
    # Tambahkan selector custom Anda di sini
    username_selectors = [
        (By.ID, 'custom_username_id'),  # <-- Tambahkan ini
        (By.ID, 'username'),
        # ... existing selectors
    ]
```

## Logs & Debugging

### Check Logs

```powershell
Get-Content logs/crawler_YYYYMMDD.log -Tail 50
```

### Screenshot Otomatis

Saat terjadi error, screenshot tersimpan di:

- `logs/sso_login_error.png` - Error saat login SSO
- `logs/sso_still_on_page.png` - Masih di halaman SSO
- `logs/error.png` - Error umum

## Flow Diagram

```
┌─────────────────────────────────────────────┐
│ User → Buka Web Dashboard                   │
│ http://localhost:5000                       │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Klik "Start Crawl"                          │
│ Target: https://olah.web.bps.go.id/...     │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Browser Selenium dibuka                      │
│ Navigate ke Target URL                       │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ ⚠️  REDIRECT DETECTED                       │
│ URL berubah ke: https://sso.bps.go.id      │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ 🔐 SSO Handler Activated                    │
│ - Detect username field                     │
│ - Fill username dari .env                   │
│ - Detect password field                     │
│ - Fill password dari .env                   │
│ - Detect submit button                      │
│ - Click submit                              │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ SSO Processing...                            │
│ Waiting for redirect...                     │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ ✅ Redirect back to application             │
│ https://olah.web.bps.go.id/seruti/...      │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Continue dengan download process            │
│ - Navigate to download page                 │
│ - Click download button                     │
│ - Wait for file download                    │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ ✅ SELESAI                                  │
│ File tersimpan di folder downloads/         │
└─────────────────────────────────────────────┘
```

## Tips

1. **Selalu test dengan HEADLESS_MODE=False dulu** untuk memastikan flow SSO bekerja
2. **Save credentials yang benar** di file `.env`
3. **Check logs** jika ada masalah
4. **Screenshot otomatis** akan membantu debugging
5. **Timeout mungkin perlu disesuaikan** jika koneksi lambat

## Security Notes

⚠️ **PENTING:**

- File `.env` berisi credentials, **JANGAN commit ke Git**
- Sudah ditambahkan ke `.gitignore`
- Gunakan credentials yang aman
- Ganti `FLASK_SECRET_KEY` untuk production

## Support

Jika ada masalah:

1. Check logs di `logs/crawler_YYYYMMDD.log`
2. Check screenshots di `logs/`
3. Set `HEADLESS_MODE=False` untuk visual debugging
4. Periksa apakah credentials SSO benar

---

**Happy Crawling! 🚀**
