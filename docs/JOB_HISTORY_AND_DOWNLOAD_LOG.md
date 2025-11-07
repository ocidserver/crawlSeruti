# Job History & Download Log Enhancement

## Overview

Perubahan untuk menambahkan:

1. **Job History dengan Status** - Job yang sudah selesai/cancelled/error tidak hilang
2. **Download Log dengan Task Name** - Tracking file download dengan info task yang menjalankan

---

## 1. Job History dengan Status

### Fitur Baru

- ✅ Job yang di-cancel **tidak dihapus**, hanya diubah statusnya menjadi `cancelled`
- ✅ Job yang sudah selesai tetap muncul dengan status `completed`
- ✅ Job yang error/retry tetap tercatat dengan status detail
- ✅ Tombol berbeda untuk active jobs (Cancel) vs inactive jobs (Archived)

### Status Job

| Status      | Keterangan                     | Badge Color  |
| ----------- | ------------------------------ | ------------ |
| `active`    | Job sedang aktif dan terjadwal | 🔵 Primary   |
| `success`   | Job berhasil dijalankan        | 🟢 Success   |
| `skipped`   | Job di-skip (data sudah ada)   | 🟢 Success   |
| `failed`    | Job gagal setelah max retries  | 🔴 Danger    |
| `retrying`  | Job sedang retry               | 🟡 Warning   |
| `cancelled` | Job dibatalkan oleh user       | ⚪ Secondary |
| `completed` | Job selesai (periode berakhir) | 🔵 Info      |
| `inactive`  | Job tidak aktif                | ⚪ Secondary |

### Perubahan Kode

**app/scheduler.py:**

```python
def get_all_jobs(self):
    """Get all scheduled jobs (active and inactive)"""
    # ... get active jobs ...

    # Add inactive jobs from config (completed, cancelled, failed)
    for job_config in self.jobs_data:
        if job_config['id'] not in active_job_ids:
            # This is an inactive job - still show it
            job_info = {...}
            jobs.append(job_info)
```

```python
def remove_job(self, job_id):
    """Remove scheduled job (cancel active job, mark as cancelled)"""
    # Update status in jobs data (keep history, don't delete)
    for job in self.jobs_data:
        if job['id'] == job_id:
            job['status'] = 'cancelled'
            job['last_message'] = 'Cancelled by user'
            break
```

**app/templates/index.html:**

```javascript
// Status badge berdasarkan status field
let statusBadge = '';
if (job.status === 'success' || job.status === 'skipped') {
    statusBadge = '<span class="badge bg-success">Success</span>';
} else if (job.status === 'failed') {
    statusBadge = '<span class="badge bg-danger">Failed</span>';
}
// ... dll ...

// Tombol berbeda untuk active vs inactive
${job.is_active ? `
    <button class="btn btn-danger btn-sm" onclick="deleteJob('${job.id}')">
        <i class="bi bi-x-circle"></i> Cancel
    </button>
` : `
    <button class="btn btn-secondary btn-sm" disabled>
        <i class="bi bi-archive"></i> Archived
    </button>
`}
```

### Screenshot UI

```
┌─────────────────────────────────────────────────────────────┐
│ Job Name [SERUTI] [Active]          [Cancel]               │
│ 📅 2025-11-07 - 2025-11-30                                  │
│ 🕐 14:00                                                     │
│ ▶️ Next run: 2025-11-07 14:00:00                            │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Job Name [SUSENAS] [Success]        [Archived]             │
│ 📅 2025-11-01 - 2025-11-05                                  │
│ 🕐 10:00                                                     │
│ ✅ Last run: 2025-11-05 10:00:00                            │
│ Downloaded: Progress_Pencacahan_2025-11-05.xlsx            │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Job Name [SERUTI] [Cancelled]       [Archived]             │
│ 📅 2025-11-01 - 2025-12-31                                  │
│ 🕐 08:00                                                     │
│ ❌ Last run: 2025-11-03 08:00:00                            │
│ Cancelled by user                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Download Log dengan Task Name

### Fitur Baru

- ✅ Tracking file download dengan nama task yang menjalankan
- ✅ Bedakan antara download **Manual** vs **Scheduled Task**
- ✅ Menampilkan kolom: Filename, Task Name, Source, Data Date, Downloaded

### Kolom Download Log

| Kolom      | Keterangan                          | Contoh                                  |
| ---------- | ----------------------------------- | --------------------------------------- |
| Filename   | Nama file yang didownload           | `Progress_Pencacahan_2025-11-07.xlsx`   |
| Task Name  | Nama task scheduler (atau "Manual") | `Crawl Harian Susenas` 🟢 / `Manual` ⚪ |
| Source     | Crawler yang menjalankan            | `SERUTI` 🔵 / `SUSENAS` 🔵              |
| Data Date  | Tanggal data di file                | `2025-11-07`                            |
| Downloaded | Waktu download                      | `2025-11-07 14:30:15`                   |

### Perubahan Kode

**app/download_log.py:**

```python
def add_download(self, nama_file, tanggal_download, laman_web,
                 data_tanggal=None, task_name=None):
    """Add new download record with task name"""
    record = {
        'nama_file': nama_file,
        'tanggal_download': tanggal_download,
        'laman_web': laman_web,
        'data_tanggal': data_tanggal,
        'task_name': task_name or 'Manual'  # <-- NEW
    }
```

**app/crawlers/base_crawler.py:**

```python
def __init__(self, username=None, password=None, headless=None, task_name=None):
    # ...
    self.task_name = task_name  # <-- NEW

def log_download(self, filename, data_tanggal=None):
    """Log download ke database"""
    download_logger.add_download(
        nama_file=filename,
        tanggal_download=datetime.now(),
        laman_web=self.source_name,
        data_tanggal=data_tanggal,
        task_name=self.task_name  # <-- NEW
    )
```

**app/scheduler.py:**

```python
def scheduled_crawl_task(self, job_id=None, retry_count=0, crawler_type='seruti'):
    # Get job name for logging
    job_config = next((j for j in self.jobs_data if j['id'] == job_id), None)
    task_name = job_config.get('name') if job_config else job_id

    # Initialize crawler with task name
    crawler = CrawlerClass(
        username=Config.USERNAME,
        password=Config.PASSWORD,
        headless=True,
        task_name=task_name  # <-- Pass task name to crawler
    )
```

**app/routes.py:**

```python
@main_bp.route('/api/downloads', methods=['GET'])
def list_downloads():
    """List semua file yang sudah didownload dari download log"""
    from app.download_log import download_logger

    # Get all logs from download log
    logs = download_logger.get_all_logs()

    # Format logs untuk display
    formatted_logs = []
    for log in logs_sorted:
        formatted_logs.append({
            'filename': log['nama_file'],
            'downloaded': log['tanggal_download'],
            'source': log['laman_web'],
            'data_date': log.get('data_tanggal', '-'),
            'task_name': log.get('task_name', 'Manual')  # <-- NEW
        })
```

**app/templates/index.html:**

```javascript
// Load downloads with task name
downloadsList.innerHTML = `
    <table class="table table-hover">
        <thead>
            <tr>
                <th>Filename</th>
                <th>Task Name</th>        <!-- NEW -->
                <th>Source</th>
                <th>Data Date</th>
                <th>Downloaded</th>
            </tr>
        </thead>
        <tbody>
            ${result.logs
              .map((log) => {
                const taskBadge =
                  log.task_name === "Manual"
                    ? '<span class="badge bg-secondary">Manual</span>'
                    : '<span class="badge bg-success">' +
                      log.task_name +
                      "</span>";

                return `
                    <tr>
                        <td>${log.filename}</td>
                        <td>${taskBadge}</td>    <!-- NEW -->
                        <td>${sourceBadge}</td>
                        <td>${log.data_date}</td>
                        <td>${log.downloaded}</td>
                    </tr>
                `;
              })
              .join("")}
        </tbody>
    </table>
`;
```

### Screenshot UI

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│ 📄 Download Log                                                  [Refresh]         │
├────────────────────────────────────────────────────────────────────────────────────┤
│ Filename                            │ Task Name      │ Source  │ Data Date │ Downl.│
├────────────────────────────────────────────────────────────────────────────────────┤
│ 📊 Progress_Pencacahan_2025-11-07   │ [Susenas Job]  │[SUSENAS]│ 2025-11-07│ 14:30 │
│ 📊 Progress_Edcod_2025-11-07        │ [Susenas Job]  │[SUSENAS]│ 2025-11-07│ 14:30 │
│ 📊 Progres_Triwulan_3_2025          │ [Manual]       │[SERUTI] │ 2025-11-01│ 10:15 │
│ 📊 Progress_IPDS_2025-11-06         │ [Daily Crawl]  │[SUSENAS]│ 2025-11-06│ 08:00 │
└────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Benefits

### Job History

1. ✅ **Audit Trail** - Semua job tersimpan untuk audit
2. ✅ **Error Tracking** - Lihat history error dan failed jobs
3. ✅ **Status Clarity** - Jelas bedakan active vs inactive jobs
4. ✅ **No Data Loss** - Cancel tidak menghapus data

### Download Log

1. ✅ **Better Tracking** - Tahu file didownload oleh task mana
2. ✅ **Manual vs Auto** - Bedakan download manual vs scheduled
3. ✅ **Complete Info** - 5 kolom: File, Task, Source, Date, Time
4. ✅ **Easy Filter** - Bisa filter by task, source, atau date

---

## Testing

### Test Job History

1. **Create job** → Status: Active ✅
2. **Job runs successfully** → Status: Success ✅
3. **Cancel job** → Status: Cancelled, masih muncul di list ✅
4. **Job end_date passed** → Status: Completed ✅
5. **Job fails** → Status: Failed ✅

### Test Download Log

1. **Manual crawl** → Task Name: Manual ⚪
2. **Scheduled crawl** → Task Name: [Job Name] 🟢
3. **Seruti crawl** → Source: SERUTI 🔵
4. **Susenas crawl** → Source: SUSENAS 🔵
5. **Check all columns** → File, Task, Source, Date, Time ✅

---

## Files Changed

1. ✅ `app/scheduler.py` - Job history logic
2. ✅ `app/download_log.py` - Add task_name field
3. ✅ `app/crawlers/base_crawler.py` - Pass task_name
4. ✅ `app/routes.py` - Update /api/downloads endpoint
5. ✅ `app/templates/index.html` - UI improvements

---

## Migration Notes

### Existing Jobs

- Job yang sudah ada akan tetap berfungsi
- Jika job di-cancel, akan masuk status `cancelled` dan tetap muncul di history

### Existing Download Logs

- File `download_log.json` yang sudah ada tetap valid
- Record lama tanpa `task_name` akan otomatis mendapat value `"Manual"`
- Tidak perlu migration script

---

## Summary

**Job History:**

- ✅ Jobs tidak hilang setelah cancel/complete
- ✅ Status badge yang jelas
- ✅ Tombol berbeda untuk active vs inactive

**Download Log:**

- ✅ Tambahan kolom Task Name
- ✅ Badge untuk Manual vs Scheduled task
- ✅ Info lengkap: File, Task, Source, Date, Time

**UI Title Changed:**

- ❌ ~~Download History~~
- ✅ **Download Log** 📄
