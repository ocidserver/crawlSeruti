# 🤖 BPS Web Crawler - Multi-Crawler System

Automated web crawler system for BPS (Badan Pusat Statistik) data sources with intelligent scheduling and download management.

## ✨ Features

### 🔄 Multi-Crawler Architecture

- **Seruti Crawler**: Survey Ekonomi Rumah Tangga Usaha Terintegrasi
- **Susenas Crawler**: Survey Sosial Ekonomi Nasional
- Easy to extend with new crawlers

### 📊 Smart Download Management

- **Download Log System**: Tracks all downloads with metadata
- **Duplicate Detection**: Automatically skips already downloaded data
- **Data Validation**: Checks data date before downloading

### ⏰ Intelligent Scheduler

- **Flexible Scheduling**: Set date ranges and execution times
- **Auto-Retry**: Configurable retry mechanism for failures
- **Multiple Jobs**: Run different crawlers on different schedules
- **Status Tracking**: Monitor job execution in real-time

### 🎨 Modern UI

- **Unified Interface**: All-in-one dashboard
- **Visual Crawler Selection**: Easy toggle between crawlers
- **Live Monitoring**: Auto-refreshing job status and downloads
- **Responsive Design**: Works on desktop and mobile

### ⚡ Performance Optimized

- **Fast Loading**: Optimized page load strategy
- **Quick Downloads**: Reduced wait times
- **Efficient Detection**: 0.5s download check interval
- **11.5% Faster**: Compared to baseline implementation

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Google Chrome browser
- ChromeDriver (auto-managed)

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd crawlSeruti
```

2. **Create virtual environment**

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**
   Create `.env` file:

```env
SERUTI_USERNAME=your_username
SERUTI_PASSWORD=your_password
DOWNLOAD_PATH=downloads
```

### Running the Application

```bash
python run.py
```

Open browser: `http://localhost:5000`

## 📖 Usage Guide

### Adding a Scheduled Job

1. **Select Crawler Type**

   - Click on **SERUTI** or **SUSENAS** card
   - Selected crawler will be highlighted

2. **Fill Job Details**

   - **Nama Jadwal**: Descriptive name (e.g., "Daily Morning Crawl")
   - **Tanggal Mulai**: Start date
   - **Tanggal Selesai**: End date
   - **Jam & Menit**: Execution time
   - **Max Retry**: Number of retries on failure (default: 3)
   - **Delay Retry**: Seconds between retries (default: 300)

3. **Submit**
   - Click **"Tambah Jadwal"** button
   - Job will appear in the active jobs list

### Monitoring Jobs

- **Jobs List**: Shows all active schedules
- **Color Coding**:
  - 🟢 Green border: Last run successful
  - 🔴 Red border: Last run failed
  - 🟡 Yellow border: Retrying
- **Badges**:
  - 🔵 Blue = SERUTI
  - 🔷 Cyan = SUSENAS

### Download History

- View all downloaded files
- Check file size and download timestamp
- Auto-refreshes every 30 seconds

## 🏗️ Architecture

### Directory Structure

```
crawlSeruti/
├── app/
│   ├── crawlers/
│   │   ├── __init__.py          # Crawler registry
│   │   ├── base_crawler.py      # Abstract base class
│   │   ├── seruti_crawler.py    # Seruti implementation
│   │   └── susenas_crawler.py   # Susenas implementation
│   ├── templates/
│   │   └── index.html           # Unified UI
│   ├── config.py                # Configuration
│   ├── download_log.py          # Download tracking
│   ├── routes.py                # Flask routes
│   └── scheduler.py             # Job scheduler
├── data/
│   ├── download_log.json        # Download history
│   └── jobs_config.json         # Scheduler jobs
├── downloads/                   # Downloaded files
├── tests/
│   └── test_multi_crawler.py    # Test suite
├── .env                         # Environment variables
├── requirements.txt             # Dependencies
└── run.py                       # Application entry
```

### Component Flow

```
User Interface (index.html)
         ↓
Flask Routes (routes.py)
         ↓
Scheduler (scheduler.py)
         ↓
Crawler Factory (crawlers/__init__.py)
         ↓
    ┌─────┴─────┐
    ↓           ↓
SerutiCrawler  SusenasCrawler
    └─────┬─────┘
          ↓
   BaseCrawler (Abstract)
          ↓
   DownloadLog System
```

## 🧪 Testing

Run the test suite:

```bash
python tests/test_multi_crawler.py
```

Tests include:

- ✅ Crawler registry functionality
- ✅ Download log system
- ✅ Crawler instantiation
- ✅ Method signatures

## 📋 API Endpoints

### Scheduler Endpoints

#### Add Scheduled Job

```http
POST /api/scheduler/job/add
Content-Type: application/json

{
  "name": "Daily Crawl",
  "crawler_type": "seruti",
  "start_date": "2025-11-07",
  "end_date": "2025-12-31",
  "hour": 9,
  "minute": 5,
  "max_retries": 3,
  "retry_delay": 300
}
```

#### Get All Jobs

```http
GET /api/scheduler/jobs
```

#### Delete Job

```http
DELETE /api/scheduler/job/{job_id}
```

### Crawler Endpoint

#### Manual Crawl

```http
POST /api/crawl
Content-Type: application/json

{
  "crawler_type": "seruti",
  "headless": true
}
```

### Downloads Endpoint

#### List Downloads

```http
GET /api/downloads
```

## 🔧 Configuration

### Environment Variables (`.env`)

```env
# Credentials
SERUTI_USERNAME=your_username
SERUTI_PASSWORD=your_password
SUSENAS_USERNAME=your_username
SUSENAS_PASSWORD=your_password

# Paths
DOWNLOAD_PATH=downloads
DATA_PATH=data

# Chrome Options
HEADLESS=true
```

### Adding New Crawlers

1. **Create crawler class** in `app/crawlers/`

```python
from app.crawlers.base_crawler import BaseCrawler

class NewCrawler(BaseCrawler):
    def __init__(self, headless=True):
        super().__init__("NewSource", headless)

    def login(self):
        # Implement login
        pass

    def navigate_to_data_page(self):
        # Implement navigation
        pass

    def get_data_date(self):
        # Extract data date
        return "2025-11-01"

    def download_data(self, *args):
        # Implement download
        pass
```

2. **Register crawler** in `app/crawlers/__init__.py`

```python
from .new_crawler import NewCrawler

CRAWLERS = {
    'seruti': SerutiCrawler,
    'susenas': SusenasCrawler,
    'new': NewCrawler  # Add here
}
```

3. **Update UI** in `app/templates/index.html`

```html
<div class="crawler-option" data-crawler="new" onclick="selectCrawler('new')">
  <i class="bi bi-icon"></i>
  <h4>NEW CRAWLER</h4>
  <p class="mb-0 small">Description</p>
</div>
```

## 📊 Download Log Format

`data/download_log.json`:

```json
[
  {
    "nama_file": "seruti_data_20251107.xlsx",
    "tanggal_download": "2025-11-07 09:05:23",
    "laman_web": "Seruti",
    "data_tanggal": "2025-11-01"
  }
]
```

## 🐛 Troubleshooting

### Chrome Driver Issues

```bash
# Automatically managed by webdriver-manager
# If issues occur, clear cache:
rm -rf ~/.wdm
```

### Scheduler Not Running

```bash
# Check scheduler status
GET /api/scheduler/status

# Restart if needed
POST /api/scheduler/stop
POST /api/scheduler/start
```

### Download Validation Failing

```bash
# Check download log
cat data/download_log.json

# Clear log if needed (backup first!)
mv data/download_log.json data/download_log.backup.json
```

## 📝 Performance Metrics

### Optimization Results

- **Baseline**: 64.87s
- **Optimized**: 57.43s
- **Improvement**: 11.5% faster

### Optimizations Applied

- Page load strategy: `eager`
- Reduced sleep times
- Faster download detection
- Smart validation to skip duplicates

## 🔒 Security Notes

- Credentials stored in `.env` (not committed to git)
- Headless mode recommended for production
- Download validation prevents unnecessary requests
- Retry mechanism prevents excessive load

## 📚 Documentation

- `MULTI_CRAWLER_IMPLEMENTATION.md`: Implementation details
- `PERFORMANCE_ANALYSIS.md`: Performance study
- `OPTIMIZATION_RESULTS.md`: Before/after comparison
- `TASK_SCHEDULER_GUIDE.md`: Scheduler documentation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-crawler`)
3. Commit changes (`git commit -am 'Add new crawler'`)
4. Push to branch (`git push origin feature/new-crawler`)
5. Create Pull Request

## 📄 License

[Your License Here]

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- BPS (Badan Pusat Statistik) for data sources
- Selenium WebDriver team
- Flask and APScheduler communities

## 📞 Support

For issues or questions:

- Check documentation files
- Review logs in console
- Open an issue on GitHub

---

**Version**: 2.0.0  
**Last Updated**: November 7, 2025  
**Status**: ✅ Production Ready (Seruti), ⚠️ Testing Needed (Susenas)
