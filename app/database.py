"""
SQLite Database Management untuk Crawler System
"""
import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager
import logging

class Database:
    """SQLite Database Manager"""
    
    def __init__(self, db_path='crawler.db'):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager untuk database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table: scheduled_jobs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_jobs (
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
                )
            ''')
            
            # Table: download_logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS download_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama_file TEXT NOT NULL,
                    tanggal_download TEXT NOT NULL,
                    laman_web TEXT NOT NULL,
                    data_tanggal TEXT,
                    task_name TEXT DEFAULT 'Manual',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_jobs_status 
                ON scheduled_jobs(status)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_logs_laman 
                ON download_logs(laman_web, data_tanggal)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_logs_date 
                ON download_logs(tanggal_download)
            ''')
            
            logging.info(f"✅ Database initialized: {self.db_path}")
    
    # ==================== SCHEDULED JOBS ====================
    
    def add_job(self, job_data):
        """Add new scheduled job"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scheduled_jobs 
                (id, name, crawler_type, start_date, end_date, hour, minute,
                 max_retries, retry_delay, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data['id'],
                job_data['name'],
                job_data['crawler_type'],
                job_data['start_date'],
                job_data['end_date'],
                job_data['hour'],
                job_data['minute'],
                job_data.get('max_retries', 3),
                job_data.get('retry_delay', 300),
                job_data.get('status', 'active'),
                job_data['created_at']
            ))
            logging.info(f"✅ Job added to database: {job_data['id']}")
    
    def update_job_status(self, job_id, status, message=None, last_run=None):
        """Update job status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if last_run is None:
                last_run = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                UPDATE scheduled_jobs 
                SET status = ?, last_message = ?, last_run = ?
                WHERE id = ?
            ''', (status, message, last_run, job_id))
            
            if cursor.rowcount > 0:
                logging.info(f"✅ Job status updated: {job_id} -> {status}")
    
    def get_job(self, job_id):
        """Get single job by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM scheduled_jobs WHERE id = ?', (job_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_jobs(self):
        """Get all jobs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM scheduled_jobs ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_active_jobs(self):
        """Get only active jobs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM scheduled_jobs 
                WHERE status = 'active' 
                ORDER BY created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_job(self, job_id):
        """Delete job (permanently)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM scheduled_jobs WHERE id = ?', (job_id,))
            logging.info(f"✅ Job deleted from database: {job_id}")
    
    def cancel_job(self, job_id):
        """Cancel job (mark as cancelled, keep in database)"""
        self.update_job_status(job_id, 'cancelled', 'Cancelled by user')
    
    # ==================== DOWNLOAD LOGS ====================
    
    def add_download_log(self, nama_file, tanggal_download, laman_web, 
                        data_tanggal=None, task_name='Manual'):
        """Add download log"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if isinstance(tanggal_download, datetime):
                tanggal_download = tanggal_download.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                INSERT INTO download_logs 
                (nama_file, tanggal_download, laman_web, data_tanggal, task_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (nama_file, tanggal_download, laman_web, data_tanggal, task_name))
            
            logging.info(f"✅ Download logged: {nama_file} (Task: {task_name})")
            return cursor.lastrowid
    
    def get_all_download_logs(self, limit=100):
        """Get all download logs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_logs 
                ORDER BY tanggal_download DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def check_download_exists(self, laman_web, data_tanggal):
        """Check if download with same data_tanggal exists"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as count FROM download_logs 
                WHERE laman_web = ? AND data_tanggal = ?
            ''', (laman_web, data_tanggal))
            result = cursor.fetchone()
            return result['count'] > 0
    
    def get_latest_by_source(self, laman_web):
        """Get latest download for specific source"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_logs 
                WHERE laman_web = ? 
                ORDER BY tanggal_download DESC 
                LIMIT 1
            ''', (laman_web,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_logs_by_task(self, task_name):
        """Get all logs for specific task"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_logs 
                WHERE task_name = ? 
                ORDER BY tanggal_download DESC
            ''', (task_name,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== MIGRATION ====================
    
    def migrate_from_json(self, jobs_json='scheduler_jobs.json', 
                         logs_json='download_log.json'):
        """Migrate data from JSON files to SQLite"""
        migrated_jobs = 0
        migrated_logs = 0
        
        # Migrate jobs
        if os.path.exists(jobs_json):
            try:
                with open(jobs_json, 'r') as f:
                    jobs = json.load(f)
                
                for job in jobs:
                    try:
                        # Check if already exists
                        existing = self.get_job(job['id'])
                        if not existing:
                            self.add_job(job)
                            migrated_jobs += 1
                    except Exception as e:
                        logging.warning(f"Error migrating job {job.get('id')}: {e}")
                
                logging.info(f"✅ Migrated {migrated_jobs} jobs from {jobs_json}")
            except Exception as e:
                logging.error(f"Error reading {jobs_json}: {e}")
        
        # Migrate download logs
        if os.path.exists(logs_json):
            try:
                with open(logs_json, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                for log in logs:
                    try:
                        self.add_download_log(
                            nama_file=log['nama_file'],
                            tanggal_download=log['tanggal_download'],
                            laman_web=log['laman_web'],
                            data_tanggal=log.get('data_tanggal'),
                            task_name=log.get('task_name', 'Manual')
                        )
                        migrated_logs += 1
                    except Exception as e:
                        logging.warning(f"Error migrating log {log.get('nama_file')}: {e}")
                
                logging.info(f"✅ Migrated {migrated_logs} logs from {logs_json}")
            except Exception as e:
                logging.error(f"Error reading {logs_json}: {e}")
        
        return migrated_jobs, migrated_logs
    
    def get_all_download_logs(self, limit=100):
        """Get all download logs with limit"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_logs
                ORDER BY tanggal_download DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_download_logs_by_date(self, date):
        """Get download logs for specific date (YYYY-MM-DD)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_logs
                WHERE date(tanggal_download) = ?
                ORDER BY tanggal_download DESC
            ''', (date,))
            return [dict(row) for row in cursor.fetchall()]


# Global database instance
db = Database()
