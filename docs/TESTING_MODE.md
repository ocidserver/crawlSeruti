# Testing Mode - Override Triwulan

## Latar Belakang

Pada tanggal 7 November 2025, sistem berada di **Triwulan IV** (Oktober-Desember). Namun, data Triwulan IV belum tersedia di sistem Seruti (masih dalam tahap ujicoba/exception).

Untuk keperluan testing, sistem perlu bisa download data **Triwulan III** yang sudah tersedia, sambil tetap mempertahankan kemampuan auto-detect triwulan untuk operasi normal di masa depan.

## Solusi: Override Triwulan

Sistem telah diupdate dengan parameter `override_triwulan` yang memungkinkan:

1. **Mode Testing**: Menggunakan triwulan tertentu (misal: Triwulan III)
2. **Mode Normal**: Auto-detect triwulan berdasarkan tanggal saat ini

## Cara Menggunakan

### 1. Testing dengan Triwulan Tertentu

```python
from app.crawler import SerutiCrawler

# Initialize crawler
crawler = SerutiCrawler(headless=False)

# Setup dan login
crawler.setup_driver()
crawler.login_seruti()
crawler.navigate_to_progres()

# Process dengan override triwulan
crawler.process_progres_page(override_triwulan="Triwulan III")

# Cleanup
crawler.cleanup()
```

### 2. Script Testing Siap Pakai

```bash
# Test download Triwulan 3
.\.venv\Scripts\python.exe test_triwulan3.py
```

### 3. Mode Normal (Auto-detect)

```python
# Tidak perlu parameter, akan otomatis detect
crawler.process_progres_page()

# Atau explicit None
crawler.process_progres_page(override_triwulan=None)
```

## Auto-detect Logic

Sistem akan otomatis mendeteksi triwulan berdasarkan bulan saat ini:

| Bulan                      | Triwulan     |
| -------------------------- | ------------ |
| Januari - Maret (1-3)      | Triwulan I   |
| April - Juni (4-6)         | Triwulan II  |
| Juli - September (7-9)     | Triwulan III |
| Oktober - Desember (10-12) | Triwulan IV  |

## Log Output

### Mode Testing (Override)

```
📅 [TESTING MODE] Using override triwulan: Triwulan III
```

### Mode Normal (Auto-detect)

```
📅 Auto-detected triwulan: Triwulan IV
```

## Use Cases

### Testing Saat Ini (November 2025)

- **Masalah**: Triwulan IV belum tersedia
- **Solusi**: `override_triwulan="Triwulan III"`
- **Script**: `test_triwulan3.py`

### Operasi Normal (Masa Depan)

- **Kondisi**: Semua triwulan sudah tersedia tepat waktu
- **Penggunaan**: Tidak perlu override, biarkan auto-detect
- **Script**: `test_seruti_flow.py` atau `auto_crawl.py`

### Testing Triwulan Spesifik

- **Kondisi**: Ingin test triwulan tertentu (misal: Triwulan I)
- **Solusi**: `override_triwulan="Triwulan I"`

## Format Override

Gunakan format yang sama dengan dropdown di website:

- `"Triwulan I"`
- `"Triwulan II"`
- `"Triwulan III"`
- `"Triwulan IV"`

⚠️ **Perhatian**: Case-sensitive! Harus persis seperti di atas.

## Backward Compatibility

Semua script existing tetap bekerja karena parameter `override_triwulan` bersifat **optional**:

- `test_seruti_flow.py` - Tetap menggunakan auto-detect
- `auto_crawl.py` - Tetap menggunakan auto-detect
- `app/scheduler.py` - Tetap menggunakan auto-detect
- `run_full_crawl()` - Tetap menggunakan auto-detect

## Rekomendasi

### Untuk Testing

```bash
# Gunakan test_triwulan3.py
.\.venv\Scripts\python.exe test_triwulan3.py
```

### Untuk Production

```bash
# Gunakan auto_crawl.py (auto-detect)
.\.venv\Scripts\python.exe auto_crawl.py --test

# Atau scheduler API
curl http://localhost:5000/api/scheduler/start -X POST
```

## Timeline

- **Saat ini (Nov 2025)**: Gunakan override untuk test Triwulan III
- **Masa depan**: Sistem akan otomatis download sesuai triwulan berjalan
- **Januari 2026**: Auto-detect akan download Triwulan I
- **April 2026**: Auto-detect akan download Triwulan II
- **Juli 2026**: Auto-detect akan download Triwulan III
- **Oktober 2026**: Auto-detect akan download Triwulan IV (jika sudah tersedia)

## Troubleshooting

### Triwulan tidak ditemukan di dropdown

```
Error: Could not find triwulan selector
```

**Solusi**:

1. Cek apakah format override sudah benar
2. Pastikan website Seruti sudah load sempurna
3. Lihat screenshot di folder `logs/`

### Download file kosong

```
Warning: No new files detected in download folder
```

**Solusi**:

1. Pastikan triwulan yang dipilih memiliki data
2. Cek koneksi internet
3. Tunggu lebih lama (adjust `_wait_for_download()`)

## Summary

✅ **Testing Mode**: Bisa pilih triwulan spesifik dengan `override_triwulan`  
✅ **Normal Mode**: Auto-detect berdasarkan tanggal  
✅ **Backward Compatible**: Semua script lama tetap jalan  
✅ **Future Proof**: Siap untuk operasi normal di masa depan
