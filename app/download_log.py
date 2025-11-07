"""
Download Log Manager untuk tracking file yang sudah didownload
Now using SQLite database
"""
from datetime import datetime
import logging
from app.database import db

class DownloadLog:
    """Manage download history log using SQLite database"""
    
    def __init__(self, log_file='download_log.json'):
        # Keep for backward compatibility but use database
        self.log_file = log_file
    
    def add_download(self, nama_file, tanggal_download, laman_web, data_tanggal=None, task_name=None):
        """
        Add new download record to database
        
        Args:
            nama_file: Nama file yang didownload
            tanggal_download: Tanggal saat download (datetime object atau string)
            laman_web: URL/nama laman yang dicrawl
            data_tanggal: Tanggal data yang ada di file (opsional)
            task_name: Nama task scheduler yang menjalankan download (opsional)
        """
        if isinstance(tanggal_download, datetime):
            tanggal_download = tanggal_download.strftime('%Y-%m-%d %H:%M:%S')
        
        log_id = db.add_download_log(
            nama_file=nama_file,
            tanggal_download=tanggal_download,
            laman_web=laman_web,
            data_tanggal=data_tanggal,
            task_name=task_name or 'Manual'
        )
        
        logging.info(f"📝 Download logged: {nama_file} (Task: {task_name or 'Manual'})")
        
        return {
            'id': log_id,
            'nama_file': nama_file,
            'tanggal_download': tanggal_download,
            'laman_web': laman_web,
            'data_tanggal': data_tanggal,
            'task_name': task_name or 'Manual'
        }
    
    def get_latest_by_source(self, laman_web):
        """
        Get latest download for specific source/laman from database
        
        Args:
            laman_web: URL/nama laman
            
        Returns:
            Latest download record or None
        """
        return db.get_latest_by_source(laman_web)
    
    def get_all_by_source(self, laman_web):
        """Get all downloads for specific source from database"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_logs 
                WHERE laman_web = ? 
                ORDER BY tanggal_download DESC
            ''', (laman_web,))
            return [dict(row) for row in cursor.fetchall()]
    
    def check_if_exists(self, laman_web, data_tanggal):
        """
        Check if data with same tanggal already downloaded
        
        Args:
            laman_web: URL/nama laman
            data_tanggal: Tanggal data yang mau dicek
            
        Returns:
            True jika sudah ada, False jika belum
        """
        return db.check_download_exists(laman_web, data_tanggal)
    
    def get_all_logs(self, limit=100):
        """Get all download logs from database"""
        return db.get_all_download_logs(limit=limit)
    
    def get_stats(self):
        """Get download statistics"""
        logs = self.get_all_logs(limit=10000)
        total = len(logs)
        
        # Group by laman_web
        by_source = {}
        for log in logs:
            source = log['laman_web']
            if source not in by_source:
                by_source[source] = 0
            by_source[source] += 1
        
        return {
            'total_downloads': total,
            'by_source': by_source,
            'latest_download': logs[0] if logs else None
        }


# Global instance
download_logger = DownloadLog()
