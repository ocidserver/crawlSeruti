# API Reference

REST API documentation untuk BPS Web Crawler System.

---

## Base URL

```
http://localhost:5000
```

---

## Authentication

Currently no authentication required (internal use only).

---

## Endpoints

### 1. Dashboard

#### GET `/`

Get main dashboard page.

**Response:** HTML page

---

### 2. Manual Crawl

#### POST `/api/crawl`

Trigger manual crawl.

**Request Body:**

```json
{
  "crawler_type": "seruti" // or "susenas"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Downloaded: Progres_Triwulan_3_2025.xlsx",
  "file": "Progres_Triwulan_3_2025.xlsx",
  "data_tanggal": "2025-11-07"
}
```

**Errors:**

```json
{
  "success": false,
  "message": "Error message here"
}
```

---

### 3. Scheduler

#### POST `/api/scheduler/job/add`

Add new scheduled job.

**Request Body:**

```json
{
  "name": "Daily Seruti Crawl",
  "crawler_type": "seruti",
  "start_date": "2025-11-08",
  "end_date": "2025-12-31",
  "hour": 8,
  "minute": 0,
  "max_retries": 3,
  "retry_delay": 300
}
```

**Validation:**

- `name`: required, string
- `crawler_type`: required, "seruti" or "susenas"
- `start_date`: required, YYYY-MM-DD format
- `end_date`: required, YYYY-MM-DD format, >= start_date
- `hour`: required, integer 0-23
- `minute`: required, integer 0-59
- `max_retries`: optional, integer 0-10, default 3
- `retry_delay`: optional, integer >= 60, default 300

**Response:**

```json
{
  "success": true,
  "job_id": "job_20251108120000",
  "message": "Job 'Daily Seruti Crawl' scheduled successfully"
}
```

**Errors:**

```json
{
  "success": false,
  "message": "Invalid crawler_type. Must be 'seruti' or 'susenas'"
}
```

---

#### GET `/api/scheduler/jobs`

Get all scheduled jobs (active and inactive).

**Response:**

```json
{
  "success": true,
  "jobs": [
    {
      "id": "job_20251108120000",
      "name": "Daily Seruti Crawl",
      "crawler_type": "seruti",
      "start_date": "2025-11-08",
      "end_date": "2025-12-31",
      "hour": 8,
      "minute": 0,
      "schedule": "08:00",
      "status": "active",
      "is_active": true,
      "next_run": "2025-11-08 08:00:00",
      "last_run": null,
      "last_message": null,
      "max_retries": 3,
      "retry_delay": 300
    }
  ]
}
```

**Job Status Values:**

- `active` - Job is scheduled and running
- `success` - Job completed successfully
- `skipped` - Job was skipped (data exists)
- `failed` - Job failed after max retries
- `retrying` - Job is retrying after failure
- `cancelled` - Job was cancelled by user
- `completed` - Job period ended

---

#### DELETE `/api/scheduler/job/<job_id>`

Cancel/remove scheduled job.

**Parameters:**

- `job_id` (path): Job ID to cancel

**Response:**

```json
{
  "success": true,
  "message": "Job cancelled successfully"
}
```

**Errors:**

```json
{
  "success": false,
  "message": "Job not found"
}
```

---

### 4. Downloads

#### GET `/api/downloads`

Get download history from database.

**Response:**

```json
{
  "success": true,
  "logs": [
    {
      "filename": "Progres_Triwulan_3_2025.xlsx",
      "downloaded": "2025-11-07 14:30:15",
      "source": "SerutiCrawler",
      "data_date": "2025-11-07",
      "task_name": "Daily Seruti Crawl"
    },
    {
      "filename": "Progress_Pencacahan_2025-11-07.xlsx",
      "downloaded": "2025-11-07 10:15:30",
      "source": "SusenasCrawler",
      "data_date": "2025-11-07",
      "task_name": "Manual"
    }
  ]
}
```

**Fields:**

- `filename`: Downloaded file name
- `downloaded`: Download timestamp
- `source`: Crawler source (SerutiCrawler/SusenasCrawler)
- `data_date`: Date of data in file
- `task_name`: Task name or "Manual"

---

#### GET `/api/download/<filename>`

Download file from server.

**Parameters:**

- `filename` (path): File name to download

**Response:** File download

**Errors:**

```json
{
  "success": false,
  "message": "File tidak ditemukan"
}
```

---

## Error Codes

| HTTP Code | Description                    |
| --------- | ------------------------------ |
| 200       | Success                        |
| 400       | Bad Request (validation error) |
| 404       | Not Found                      |
| 500       | Internal Server Error          |

---

## Database Schema

### Table: scheduled_jobs

```sql
CREATE TABLE scheduled_jobs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    crawler_type TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    hour INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    max_retries INTEGER DEFAULT 3,
    retry_delay INTEGER DEFAULT 300,
    status TEXT DEFAULT 'active',
    created_at TEXT NOT NULL,
    last_run TEXT,
    last_message TEXT
);
```

### Table: download_logs

```sql
CREATE TABLE download_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_file TEXT NOT NULL,
    tanggal_download TEXT NOT NULL,
    laman_web TEXT NOT NULL,
    data_tanggal TEXT,
    task_name TEXT DEFAULT 'Manual',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## Examples

### Example 1: Schedule Daily Job

```python
import requests

url = "http://localhost:5000/api/scheduler/job/add"
data = {
    "name": "Morning Seruti Crawl",
    "crawler_type": "seruti",
    "start_date": "2025-11-08",
    "end_date": "2025-12-31",
    "hour": 7,
    "minute": 30,
    "max_retries": 3,
    "retry_delay": 300
}

response = requests.post(url, json=data)
print(response.json())
```

### Example 2: Get All Jobs

```python
import requests

url = "http://localhost:5000/api/scheduler/jobs"
response = requests.get(url)

jobs = response.json()['jobs']
for job in jobs:
    print(f"{job['name']}: {job['status']}")
```

### Example 3: Manual Crawl

```python
import requests

url = "http://localhost:5000/api/crawl"
data = {"crawler_type": "susenas"}

response = requests.post(url, json=data)
result = response.json()

if result['success']:
    print(f"Downloaded: {result['file']}")
else:
    print(f"Error: {result['message']}")
```

### Example 4: Cancel Job

```python
import requests

job_id = "job_20251108120000"
url = f"http://localhost:5000/api/scheduler/job/{job_id}"

response = requests.delete(url)
print(response.json())
```

### Example 5: Get Download History

```python
import requests

url = "http://localhost:5000/api/downloads"
response = requests.get(url)

logs = response.json()['logs']
for log in logs:
    print(f"{log['filename']} - {log['task_name']} - {log['downloaded']}")
```

---

## Rate Limiting

Currently no rate limiting implemented.

---

## Webhooks

Not yet supported.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for API changes across versions.
