"""
Scheduler untuk menjalankan crawl otomatis secara berkala dengan retry mechanism
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import logging
import time
from app.crawlers import get_crawler
from app.config import Config
from app.database import db

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CrawlScheduler:
    """Scheduler untuk auto crawl dengan retry mechanism"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.retry_config = {
            'max_retries': 3,
            'retry_delay': 300  # 5 minutes in seconds
        }
        # Migrate existing JSON data on first run
        self.migrate_if_needed()
        
    def migrate_if_needed(self):
        """Migrate JSON data to SQLite if JSON files exist"""
        import os
        if os.path.exists('scheduler_jobs.json') or os.path.exists('download_log.json'):
            logging.info("🔄 Migrating existing JSON data to SQLite...")
            jobs_migrated, logs_migrated = db.migrate_from_json()
            logging.info(f"✅ Migration complete: {jobs_migrated} jobs, {logs_migrated} logs")
            
            # Rename JSON files as backup
            if os.path.exists('scheduler_jobs.json'):
                os.rename('scheduler_jobs.json', 'scheduler_jobs.json.backup')
            if os.path.exists('download_log.json'):
                os.rename('download_log.json', 'download_log.json.backup')
    
    def scheduled_crawl_task(self, job_id=None, retry_count=0, crawler_type='seruti'):
        """
        Task yang akan dijalankan secara terjadwal dengan retry mechanism
        
        Args:
            job_id: ID job untuk tracking
            retry_count: Current retry attempt number
            crawler_type: Type of crawler ('seruti' atau 'susenas')
        """
        logging.info("=" * 60)
        logging.info(f"🤖 AUTO CRAWL STARTED - {crawler_type.upper()}")
        logging.info(f"Job ID: {job_id}")
        logging.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if retry_count > 0:
            logging.info(f"🔄 Retry attempt: {retry_count}/{self.retry_config['max_retries']}")
        logging.info("=" * 60)
        
        try:
            # Get crawler class
            CrawlerClass = get_crawler(crawler_type)
            if not CrawlerClass:
                raise Exception(f"Unknown crawler type: {crawler_type}")
            
            # Get job name for logging from database
            job_config = db.get_job(job_id)
            task_name = job_config.get('name') if job_config else job_id
            
            # Initialize crawler with task name
            crawler = CrawlerClass(
                username=Config.USERNAME,
                password=Config.PASSWORD,
                headless=True,  # Selalu headless untuk auto mode
                task_name=task_name
            )
            
            # Run crawl
            result = crawler.run()
            
            if result['success']:
                if result.get('skipped'):
                    logging.info(f"⏭️  CRAWL SKIPPED: {result['message']}")
                    db.update_job_status(job_id, 'skipped', result.get('message'))
                else:
                    logging.info(f"✅ AUTO CRAWL SUCCESS: {result['message']}")
                    if result.get('file'):
                        logging.info(f"📄 File downloaded: {result['file']}")
                    db.update_job_status(job_id, 'success', result.get('message'))
            else:
                logging.warning(f"⚠️ AUTO CRAWL FAILED: {result['message']}")
                
                # Retry logic
                if retry_count < self.retry_config['max_retries']:
                    retry_count += 1
                    retry_delay = self.retry_config['retry_delay']
                    logging.info(f"🔄 Scheduling retry {retry_count} in {retry_delay} seconds...")
                    
                    # Schedule retry
                    retry_time = datetime.now() + timedelta(seconds=retry_delay)
                    self.scheduler.add_job(
                        self.scheduled_crawl_task,
                        DateTrigger(run_date=retry_time),
                        args=[job_id, retry_count, crawler_type],
                        id=f'{job_id}_retry_{retry_count}',
                        name=f'Retry {retry_count} for {job_id}',
                        replace_existing=True
                    )
                    
                    self.update_job_status(job_id, 'retrying', f'Retry {retry_count}/{self.retry_config["max_retries"]}')
                else:
                    logging.error(f"❌ Max retries reached for job {job_id}")
                    self.update_job_status(job_id, 'failed', f'Failed after {retry_count} retries')
                
        except Exception as e:
            logging.error(f"❌ AUTO CRAWL ERROR: {str(e)}")
            
            # Retry on exception
            if retry_count < self.retry_config['max_retries']:
                retry_count += 1
                retry_delay = self.retry_config['retry_delay']
                logging.info(f"🔄 Scheduling retry {retry_count} in {retry_delay} seconds...")
                
                retry_time = datetime.now() + timedelta(seconds=retry_delay)
                self.scheduler.add_job(
                    self.scheduled_crawl_task,
                    DateTrigger(run_date=retry_time),
                    args=[job_id, retry_count, crawler_type],
                    id=f'{job_id}_retry_{retry_count}',
                    name=f'Retry {retry_count} for {job_id}',
                    replace_existing=True
                )
                
                self.update_job_status(job_id, 'retrying', f'Error: {str(e)}, retry {retry_count}')
            else:
                self.update_job_status(job_id, 'failed', f'Error: {str(e)}')
        
        logging.info("=" * 60)
        logging.info("🏁 AUTO CRAWL FINISHED")
        logging.info("=" * 60)
    
    def add_scheduled_job(self, name, start_date, end_date, hour, minute, 
                         crawler_type='seruti', max_retries=3, retry_delay=300):
        """
        Tambah scheduled job dengan range tanggal
        
        Args:
            name: Nama job
            start_date: Tanggal mulai (YYYY-MM-DD)
            end_date: Tanggal selesai (YYYY-MM-DD)
            hour: Jam eksekusi (0-23)
            minute: Menit eksekusi (0-59)
            crawler_type: Jenis crawler ('seruti' atau 'susenas')
            max_retries: Maksimal retry jika gagal
            retry_delay: Delay antara retry (seconds)
        """
        job_id = f"job_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Parse dates
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Create job config
        job_config = {
            'id': job_id,
            'name': name,
            'crawler_type': crawler_type,
            'start_date': start_date,
            'end_date': end_date,
            'hour': hour,
            'minute': minute,
            'max_retries': max_retries,
            'retry_delay': retry_delay,
            'status': 'active',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_run': None,
            'last_message': None
        }
        
        # Save to database
        db.add_job(job_config)
        
        # Update retry config
        self.retry_config['max_retries'] = max_retries
        self.retry_config['retry_delay'] = retry_delay
        
        # Add job to scheduler
        self.scheduler.add_job(
            self.scheduled_crawl_task,
            CronTrigger(
                hour=hour, 
                minute=minute,
                start_date=start_dt,
                end_date=end_dt
            ),
            args=[job_id, 0, crawler_type],
            id=job_id,
            name=name,
            replace_existing=True
        )
        
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
        
        logging.info(f"⏰ Job '{name}' ({crawler_type}) scheduled: {hour:02d}:{minute:02d} from {start_date} to {end_date}")
        logging.info(f"   Retry config: max={max_retries}, delay={retry_delay}s")
        
        return job_id
    
    def remove_job(self, job_id):
        """Remove scheduled job (cancel active job, mark as cancelled)"""
        try:
            # Try to remove from scheduler (if active)
            try:
                self.scheduler.remove_job(job_id)
            except:
                pass  # Job might not be in scheduler (already completed/failed)
            
            # Update status in database (keep history, don't delete)
            db.cancel_job(job_id)
            
            logging.info(f"Job {job_id} cancelled")
            return True
        except Exception as e:
            logging.error(f"Error cancelling job {job_id}: {str(e)}")
            return False
    
    def get_all_jobs(self):
        """Get all scheduled jobs (active and inactive) from database"""
        jobs = []
        
        # Get all jobs from database
        all_jobs_db = db.get_all_jobs()
        
        # Get active jobs from scheduler
        active_job_ids = {job.id for job in self.scheduler.get_jobs()}
        
        for job_config in all_jobs_db:
            job_info = {
                'id': job_config['id'],
                'name': job_config['name'],
                'start_date': job_config['start_date'],
                'end_date': job_config['end_date'],
                'hour': job_config['hour'],
                'minute': job_config['minute'],
                'schedule': f"{job_config['hour']:02d}:{job_config['minute']:02d}",
                'crawler_type': job_config.get('crawler_type', 'seruti'),
                'status': job_config.get('status', 'active'),
                'last_run': job_config.get('last_run'),
                'last_message': job_config.get('last_message'),
                'max_retries': job_config.get('max_retries'),
                'retry_delay': job_config.get('retry_delay'),
                'is_active': job_config['id'] in active_job_ids
            }
            
            # Get next_run from scheduler if active
            if job_info['is_active']:
                try:
                    job = self.scheduler.get_job(job_config['id'])
                    if job and job.next_run_time:
                        job_info['next_run'] = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        job_info['next_run'] = None
                except:
                    job_info['next_run'] = None
            else:
                job_info['next_run'] = None
            
            jobs.append(job_info)
        
        return jobs
    
    def get_job_details(self, job_id):
        """Get job details from database"""
        job_config = db.get_job(job_id)
        
        if job_config:
            try:
                job = self.scheduler.get_job(job_id)
                if job:
                    job_config['next_run'] = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None
                    job_config['is_active'] = True
                else:
                    job_config['is_active'] = False
            except:
                job_config['is_active'] = False
        
        return job_config
    
    def update_retry_config(self, max_retries, retry_delay):
        """Update global retry configuration"""
        self.retry_config['max_retries'] = max_retries
        self.retry_config['retry_delay'] = retry_delay
        logging.info(f"Retry config updated: max={max_retries}, delay={retry_delay}s")
    
    def start_daily_crawl(self, hour=8, minute=0):
        """
        Jalankan crawl setiap hari pada jam tertentu
        
        Args:
            hour: Jam (0-23)
            minute: Menit (0-59)
        """
        job_id = 'daily_crawl'
        
        # Tambahkan job ke scheduler
        self.scheduler.add_job(
            self.scheduled_crawl_task,
            CronTrigger(hour=hour, minute=minute),
            args=[job_id, 0],
            id=job_id,
            name='Daily Auto Crawl',
            replace_existing=True
        )
        
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
        
        logging.info(f"⏰ Scheduler started: Daily crawl at {hour:02d}:{minute:02d}")
    
    def start_hourly_crawl(self, minute=0):
        """
        Jalankan crawl setiap jam
        
        Args:
            minute: Menit (0-59)
        """
        self.scheduler.add_job(
            self.scheduled_crawl_task,
            CronTrigger(minute=minute),
            id='hourly_crawl',
            name='Hourly Auto Crawl',
            replace_existing=True
        )
        
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
        
        logging.info(f"⏰ Scheduler started: Hourly crawl at minute {minute}")
    
    def start_interval_crawl(self, hours=0, minutes=30):
        """
        Jalankan crawl setiap interval tertentu
        
        Args:
            hours: Jumlah jam
            minutes: Jumlah menit
        """
        self.scheduler.add_job(
            self.scheduled_crawl_task,
            'interval',
            hours=hours,
            minutes=minutes,
            id='interval_crawl',
            name='Interval Auto Crawl',
            replace_existing=True
        )
        
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
        
        logging.info(f"⏰ Scheduler started: Every {hours}h {minutes}m")
    
    def start_custom_schedule(self, cron_expression):
        """
        Jalankan crawl dengan custom cron expression
        
        Args:
            cron_expression: Cron format (contoh: '0 8,12,18 * * *' = jam 8, 12, 18)
        """
        self.scheduler.add_job(
            self.scheduled_crawl_task,
            CronTrigger.from_crontab(cron_expression),
            id='custom_crawl',
            name='Custom Schedule Crawl',
            replace_existing=True
        )
        
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
        
        logging.info(f"⏰ Scheduler started: Custom schedule '{cron_expression}'")
    
    def stop_scheduler(self):
        """Stop scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logging.info("🛑 Scheduler stopped")
    
    def get_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()
    
    def run_now(self):
        """Jalankan crawl sekarang (manual trigger)"""
        logging.info("▶️ Manual crawl triggered")
        self.scheduled_crawl_task()

# Global scheduler instance
scheduler_instance = CrawlScheduler()
