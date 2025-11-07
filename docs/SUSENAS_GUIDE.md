# 📊 Susenas Crawler - User Guide

## Overview

Susenas Crawler adalah sistem otomatis untuk mengunduh 7 laporan progress dari BPS Web Monitoring System.

## 🎯 Fitur

### Download 7 Laporan Sekaligus

Dalam 1x crawl, sistem akan mengunduh:

1. **Laporan Pencacahan** (`pencacahan`)
2. **Laporan Pemeriksaan** (`edcod`)
3. **Laporan Pengiriman ke Kabkot** (`pengiriman`)
4. **Laporan Penerimaan di Kabkot** (`penerimaan`)
5. **Laporan Penerimaan di IPDS** (`ipds`)
6. **Laporan Pengolahan Dokumen M** (`pengolahan`)
7. **Laporan Pengolahan Dokumen KP** (`pengolahan2`)

### Fitur Otomatis

- ✅ Login SSO BPS (sama seperti Seruti)
- ✅ Navigasi otomatis ke setiap laporan
- ✅ Menggunakan tanggal hari ini untuk parameter URL
- ✅ Download Excel untuk setiap laporan
- ✅ Tracking semua file yang diunduh
- ✅ Validasi duplikat (skip jika data sudah ada)

## 🔧 Konfigurasi

### URL Configuration

Crawler menggunakan URL berikut:

**SSO Login:**

```
https://sso.bps.go.id/auth/realms/pegawai-bps/protocol/openid-connect/auth?scope=profile-pegawai%2Cemail&response_type=code&approval_prompt=auto&redirect_uri=https%3A%2F%2Fwebmonitoring.bps.go.id%2F&client_id=03310-webmon-1kw
```

**Dashboard:**

```
https://webmonitoring.bps.go.id/beranda
```

**SEN Index:**

```
https://webmonitoring.bps.go.id/sen/site/index
```

**Report Base URL:**

```
https://webmonitoring.bps.go.id/sen/progress/{report_name}?wil=17&view=tabel&tgl_his={tanggal}
```

### Parameters

- `wil=17`: Wilayah (default: 17)
- `view=tabel`: Tampilan tabel
- `tgl_his`: Tanggal historis (YYYY-MM-DD, otomatis diisi dengan tanggal hari ini)

## 📋 Proses Crawling

### Step-by-Step Process

1. **Login SSO**

   - Navigate ke SSO BPS
   - Input username & password
   - Klik login button
   - Wait redirect ke webmonitoring.bps.go.id

2. **Navigate to SEN**

   - Buka https://webmonitoring.bps.go.id/sen/site/index
   - Confirm page loaded

3. **Download Report 1: Pencacahan**

   - URL: `.../sen/progress/pencacahan?wil=17&view=tabel&tgl_his=2025-11-07`
   - Click button `#export-excel`
   - Wait download complete

4. **Download Report 2: Pemeriksaan**

   - URL: `.../sen/progress/edcod?wil=17&view=tabel&tgl_his=2025-11-07`
   - Click button `#export-excel`
   - Wait download complete

5. **Download Report 3: Pengiriman**

   - URL: `.../sen/progress/pengiriman?wil=17&view=tabel&tgl_his=2025-11-07`
   - Click button `#export-excel`
   - Wait download complete

6. **Download Report 4: Penerimaan Kabkot**

   - URL: `.../sen/progress/penerimaan?wil=17&view=tabel&tgl_his=2025-11-07`
   - Click button `#export-excel`
   - Wait download complete

7. **Download Report 5: Penerimaan IPDS**

   - URL: `.../sen/progress/ipds?wil=17&view=tabel&tgl_his=2025-11-07`
   - Click button `#export-excel`
   - Wait download complete

8. **Download Report 6: Pengolahan M**

   - URL: `.../sen/progress/pengolahan?wil=17&view=tabel&tgl_his=2025-11-07`
   - Click button `#export-excel`
   - Wait download complete

9. **Download Report 7: Pengolahan KP**
   - URL: `.../sen/progress/pengolahan2?wil=17&view=tabel&tgl_his=2025-11-07`
   - Click button `#export-excel`
   - Wait download complete

## 🚀 Cara Menggunakan

### Via UI (Recommended)

1. **Buka aplikasi**: http://localhost:5000

2. **Pilih Susenas**:

   - Klik pada card "SUSENAS"
   - Card akan highlight biru

3. **Buat Jadwal**:

   - Isi nama jadwal: "Susenas Daily"
   - Pilih tanggal mulai & selesai
   - Set jam eksekusi (misal: 09:00)
   - Klik "Tambah Jadwal"

4. **Monitor**:
   - Lihat status di "Daftar Jadwal Aktif"
   - Badge akan menunjukkan "SUSENAS" dengan warna cyan
   - Check download history untuk file hasil

### Via API

```bash
curl -X POST http://localhost:5000/api/scheduler/job/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Susenas Daily Crawl",
    "crawler_type": "susenas",
    "start_date": "2025-11-07",
    "end_date": "2025-12-31",
    "hour": 9,
    "minute": 0,
    "max_retries": 3,
    "retry_delay": 300
  }'
```

### Manual Run (Testing)

```bash
# Via Python
python -c "from app.crawlers import get_crawler; c = get_crawler('susenas')(headless=True); c.run()"
```

## 📊 Output

### File Naming

Files akan didownload dengan nama dari server (biasanya format Excel):

- `pencacahan_17_2025-11-07.xlsx`
- `edcod_17_2025-11-07.xlsx`
- `pengiriman_17_2025-11-07.xlsx`
- dll.

### Download Location

```
downloads/
├── pencacahan_17_2025-11-07.xlsx
├── edcod_17_2025-11-07.xlsx
├── pengiriman_17_2025-11-07.xlsx
├── penerimaan_17_2025-11-07.xlsx
├── ipds_17_2025-11-07.xlsx
├── pengolahan_17_2025-11-07.xlsx
└── pengolahan2_17_2025-11-07.xlsx
```

### Download Log

Semua download dicatat di `data/download_log.json`:

```json
{
  "nama_file": "pencacahan_17_2025-11-07.xlsx",
  "tanggal_download": "2025-11-07 09:05:23",
  "laman_web": "Susenas",
  "data_tanggal": "2025-11-07"
}
```

## 🔍 Monitoring & Logging

### Console Output

```
🔐 Logging in to Susenas via SSO...
✅ Username entered: your_username
✅ Password entered
🔄 Login button clicked
✅ Login successful - redirected to Web Monitoring
🧭 Navigating to SEN index page...
✅ Navigation to SEN page successful
📅 Getting data date...
✅ Data date: 2025-11-07
📥 Starting Susenas download process...
   Target date: 2025-11-07

📊 [1/7] Downloading Laporan Pencacahan...
   URL: https://webmonitoring.bps.go.id/sen/progress/pencacahan?wil=17&view=tabel&tgl_his=2025-11-07
   ✅ Found export button, clicking...
   ✅ Downloaded: pencacahan_17_2025-11-07.xlsx

📊 [2/7] Downloading Laporan Pemeriksaan...
   ...

📦 Download Summary:
   Total files downloaded: 7/7
   1. pencacahan_17_2025-11-07.xlsx
   2. edcod_17_2025-11-07.xlsx
   3. pengiriman_17_2025-11-07.xlsx
   4. penerimaan_17_2025-11-07.xlsx
   5. ipds_17_2025-11-07.xlsx
   6. pengolahan_17_2025-11-07.xlsx
   7. pengolahan2_17_2025-11-07.xlsx
```

## ⚠️ Troubleshooting

### Issue: Login Gagal

**Solusi:**

- Cek kredensial di `.env`
- Pastikan username/password benar
- Coba login manual di browser

### Issue: Export Button Tidak Ditemukan

**Solusi:**

- Cek apakah URL benar
- Buka URL manual di browser
- Pastikan button ID = "export-excel"
- Cek parameter `wil=17` sesuai wilayah

### Issue: Download Incomplete (< 7 files)

**Solusi:**

- Cek log untuk error detail
- Beberapa laporan mungkin tidak tersedia
- Sistem akan continue download sisanya
- Retry akan otomatis jika scheduled

### Issue: File Tidak Terdownload

**Solusi:**

- Cek folder downloads
- Pastikan Chrome download path benar
- Cek permission folder
- Disable popup blocker

## 🔧 Customization

### Ubah Wilayah

Edit `susenas_crawler.py`:

```python
# Change wil parameter
report_url = f"{self.base_report_url}/{report['name']}?wil=34&view=tabel&tgl_his={self.today}"
```

### Tambah Laporan Baru

Edit array `self.reports`:

```python
self.reports = [
    # ... existing reports ...
    {'name': 'new_report', 'label': 'Laporan Baru'},
]
```

### Ubah Tanggal

Default menggunakan hari ini. Untuk custom:

```python
# In download_data method
custom_date = "2025-11-01"
report_url = f"{self.base_report_url}/{report['name']}?wil=17&view=tabel&tgl_his={custom_date}"
```

## 📈 Performance

### Timing Estimates

- Login: ~5 seconds
- Navigate: ~2 seconds
- Per report download: ~3-5 seconds
- **Total**: ~35-50 seconds for 7 files

### Optimization Tips

- Use headless mode (faster)
- Increase wait times if network slow
- Run during off-peak hours

## 🔐 Security

### Credentials

Store in `.env`:

```env
SUSENAS_USERNAME=your_username
SUSENAS_PASSWORD=your_password
```

### Headless Mode

Recommended for production:

```python
crawler = SusenasCrawler(headless=True)
```

## 📚 Related Documentation

- `MULTI_CRAWLER_IMPLEMENTATION.md` - Architecture overview
- `TASK_SCHEDULER_GUIDE.md` - Scheduler setup
- `README_NEW.md` - Main documentation

## 🆘 Support

Jika ada masalah:

1. Cek log di console
2. Review `download_log.json`
3. Test manual di browser dulu
4. Buka issue di GitHub

---

**Version**: 1.0  
**Last Updated**: November 7, 2025  
**Status**: ✅ Ready for Testing
