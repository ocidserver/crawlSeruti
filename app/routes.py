from flask import Blueprint, render_template, request, jsonify, send_file
from app.crawlers import get_crawler
from app.config import Config
from app.scheduler import scheduler_instance
import os
import logging
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render halaman utama"""
    return render_template('index.html')

@main_bp.route('/api/crawl', methods=['POST'])
def start_crawl():
    """
    API endpoint untuk memulai crawling manual (deprecated, gunakan scheduler)
    Expected JSON payload:
    {
        "crawler_type": "seruti" atau "susenas",
        "headless": true
    }
    """
    try:
        data = request.get_json()
        
        # Get crawler type
        crawler_type = data.get('crawler_type', 'seruti').lower()
        if crawler_type not in ['seruti', 'susenas']:
            return jsonify({
                'success': False,
                'message': f'Invalid crawler_type: {crawler_type}. Must be "seruti" or "susenas"'
            }), 400
        
        # Get crawler class
        CrawlerClass = get_crawler(crawler_type)
        if not CrawlerClass:
            return jsonify({
                'success': False,
                'message': f'Crawler tidak ditemukan: {crawler_type}'
            }), 400
        
        # Initialize and run crawler
        crawler = CrawlerClass(headless=data.get('headless', True))
        result = crawler.run()
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Crawl error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@main_bp.route('/api/downloads', methods=['GET'])
def list_downloads():
    """List semua file yang sudah didownload dari download log"""
    try:
        from app.download_log import download_logger
        
        # Get all logs from download log
        logs = download_logger.get_all_logs()
        
        # Sort by download date (newest first)
        logs_sorted = sorted(logs, key=lambda x: x['tanggal_download'], reverse=True)
        
        # Format logs untuk display
        formatted_logs = []
        for log in logs_sorted:
            formatted_logs.append({
                'filename': log['nama_file'],
                'downloaded': log['tanggal_download'],
                'source': log['laman_web'],
                'data_date': log.get('data_tanggal', '-'),
                'task_name': log.get('task_name', 'Manual')
            })
        
        return jsonify({
            'success': True,
            'logs': formatted_logs
        })
        
    except Exception as e:
        logging.error(f"Error listing downloads: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@main_bp.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download file dari server"""
    try:
        filepath = os.path.join(Config.DOWNLOAD_PATH, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'message': 'File tidak ditemukan'
            }), 404
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@main_bp.route('/api/logs', methods=['GET'])
def view_logs():
    """View application logs"""
    try:
        log_file = os.path.join(
            Config.LOG_PATH, 
            f'crawler_{datetime.now().strftime("%Y%m%d")}.log'
        )
        
        if not os.path.exists(log_file):
            return jsonify({
                'success': True,
                'logs': []
            })
        
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = f.readlines()
        
        # Return last 100 lines
        return jsonify({
            'success': True,
            'logs': logs[-100:]
        })
        
    except Exception as e:
        logging.error(f"Error reading logs: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@main_bp.route('/api/config', methods=['GET'])
def get_config():
    """Get default configuration"""
    return jsonify({
        'success': True,
        'config': {
            'target_url': Config.TARGET_URL,
            'download_url': Config.DOWNLOAD_URL,
            'username': Config.USERNAME,
            'headless': Config.HEADLESS_MODE
        }
    })

# ============================================
# SCHEDULER ENDPOINTS
# ============================================

@main_bp.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    """
    Start automated scheduler
    JSON payload:
    {
        "mode": "daily|hourly|interval|custom",
        "hour": 8,           // for daily mode
        "minute": 0,         // for daily/hourly mode
        "hours": 0,          // for interval mode
        "minutes": 30,       // for interval mode
        "cron": "0 8 * * *"  // for custom mode
    }
    """
    try:
        data = request.get_json() or {}
        mode = data.get('mode', 'daily')
        
        if mode == 'daily':
            hour = data.get('hour', 8)
            minute = data.get('minute', 0)
            scheduler_instance.start_daily_crawl(hour=hour, minute=minute)
            message = f"✅ Scheduler started: Daily at {hour:02d}:{minute:02d}"
            
        elif mode == 'hourly':
            minute = data.get('minute', 0)
            scheduler_instance.start_hourly_crawl(minute=minute)
            message = f"✅ Scheduler started: Hourly at minute {minute}"
            
        elif mode == 'interval':
            hours = data.get('hours', 0)
            minutes = data.get('minutes', 30)
            scheduler_instance.start_interval_crawl(hours=hours, minutes=minutes)
            message = f"✅ Scheduler started: Every {hours}h {minutes}m"
            
        elif mode == 'custom':
            cron = data.get('cron', '0 8 * * *')
            scheduler_instance.start_custom_schedule(cron)
            message = f"✅ Scheduler started: Custom '{cron}'"
            
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid mode. Use: daily, hourly, interval, or custom'
            }), 400
        
        return jsonify({
            'success': True,
            'message': message,
            'is_running': scheduler_instance.is_running
        })
        
    except Exception as e:
        logging.error(f"Scheduler start error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler"""
    try:
        scheduler_instance.stop_scheduler()
        return jsonify({
            'success': True,
            'message': '🛑 Scheduler stopped',
            'is_running': scheduler_instance.is_running
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/api/scheduler/status', methods=['GET'])
def get_scheduler_status():
    """Get scheduler status and jobs"""
    try:
        jobs = scheduler_instance.get_jobs()
        jobs_info = []
        
        for job in jobs:
            jobs_info.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None
            })
        
        return jsonify({
            'success': True,
            'is_running': scheduler_instance.is_running,
            'jobs': jobs_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/api/scheduler/run-now', methods=['POST'])
def run_scheduler_now():
    """Trigger crawl immediately"""
    try:
        scheduler_instance.run_now()
        return jsonify({
            'success': True,
            'message': '▶️ Manual crawl triggered (check logs)'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/scheduler')
def scheduler_page():
    """Render scheduler management page"""
    return render_template('scheduler.html')

@main_bp.route('/api/scheduler/jobs', methods=['GET'])
def get_scheduler_jobs():
    """Get all scheduled jobs"""
    try:
        jobs = scheduler_instance.get_all_jobs()
        return jsonify({
            'success': True,
            'jobs': jobs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/api/scheduler/job/add', methods=['POST'])
def add_scheduler_job():
    """
    Add new scheduled job
    Expected JSON:
    {
        "name": "Daily Morning Crawl",
        "crawler_type": "seruti",
        "start_date": "2025-11-07",
        "end_date": "2025-12-31",
        "hour": 9,
        "minute": 5,
        "max_retries": 3,
        "retry_delay": 300
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['name', 'start_date', 'end_date', 'hour', 'minute']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate crawler_type
        crawler_type = data.get('crawler_type', 'seruti').lower()
        if crawler_type not in ['seruti', 'susenas']:
            return jsonify({
                'success': False,
                'message': f'Invalid crawler_type: {crawler_type}. Must be "seruti" or "susenas"'
            }), 400
        
        # Add job
        job_id = scheduler_instance.add_scheduled_job(
            name=data['name'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            hour=int(data['hour']),
            minute=int(data['minute']),
            crawler_type=crawler_type,
            max_retries=int(data.get('max_retries', 3)),
            retry_delay=int(data.get('retry_delay', 300))
        )
        
        return jsonify({
            'success': True,
            'message': f'✅ Job "{data["name"]}" ({crawler_type.upper()}) berhasil ditambahkan',
            'job_id': job_id
        })
        
    except Exception as e:
        logging.error(f"Add job error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/api/scheduler/job/<job_id>', methods=['DELETE'])
def delete_scheduler_job(job_id):
    """Delete scheduled job"""
    try:
        success = scheduler_instance.remove_job(job_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'✅ Job dihapus'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Job tidak ditemukan'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/api/scheduler/job/<job_id>', methods=['GET'])
def get_job_details(job_id):
    """Get job details"""
    try:
        job = scheduler_instance.get_job_details(job_id)
        
        if job:
            return jsonify({
                'success': True,
                'job': job
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Job tidak ditemukan'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/api/scheduler/retry-config', methods=['POST'])
def update_retry_config():
    """
    Update global retry configuration
    Expected JSON:
    {
        "max_retries": 3,
        "retry_delay": 300
    }
    """
    try:
        data = request.get_json()
        
        max_retries = int(data.get('max_retries', 3))
        retry_delay = int(data.get('retry_delay', 300))
        
        scheduler_instance.update_retry_config(max_retries, retry_delay)
        
        return jsonify({
            'success': True,
            'message': f'✅ Retry config updated: max={max_retries}, delay={retry_delay}s'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
