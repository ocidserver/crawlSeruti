# ⚡ Quick Start - SSO BPS

## Setup Cepat (5 Menit)

### 1. Edit `.env`

```env
TARGET_URL=https://olah.web.bps.go.id/seruti/login
USERNAME=username_bps_anda
PASSWORD=password_bps_anda
HEADLESS_MODE=False
```

### 2. Jalankan

```powershell
.venv\Scripts\python.exe run.py
```

### 3. Buka Browser

- Akses: http://localhost:5000
- Isi form (atau biarkan terisi otomatis dari .env)
- Klik "Start Crawl"

### 4. Lihat Proses

Browser akan:

1. Buka target URL ✅
2. Redirect ke SSO BPS ✅
3. Isi username & password ✅
4. Submit form ✅
5. Redirect kembali ✅
6. Download file ✅

## ⚠️ Troubleshooting Cepat

### Masalah: Login gagal

```powershell
# Check credentials di .env
notepad .env
```

### Masalah: Field tidak ditemukan

```powershell
# Set headless = False untuk lihat browser
# Edit .env:
HEADLESS_MODE=False
```

### Masalah: Check logs

```powershell
# Lihat log hari ini
Get-Content "logs/crawler_$(Get-Date -Format 'yyyyMMdd').log" -Tail 20
```

### Masalah: Check screenshot error

```powershell
# Buka folder logs
explorer logs
# Lihat file .png untuk debugging
```

## 📝 Catatan

- **Pertama kali gunakan `HEADLESS_MODE=False`** untuk memastikan SSO bekerja
- **Screenshot otomatis** tersimpan di `logs/` jika ada error
- **Credentials** di `.env` JANGAN di-commit ke git (sudah di .gitignore)

## 🎯 Target URL Examples

```env
# Seruti BPS
TARGET_URL=https://olah.web.bps.go.id/seruti/login

# Atau aplikasi BPS lainnya yang pakai SSO
TARGET_URL=https://appbps.bps.go.id/login
```

Semua yang redirect ke `https://sso.bps.go.id` akan di-handle otomatis!

---

**Butuh bantuan lebih?** Baca [SSO_GUIDE.md](SSO_GUIDE.md) untuk detail lengkap.
