"""
Management Routes Blueprint
Handles user management and application settings
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from app.auth import auth_manager, login_required, admin_required
from app.database import db
from app.scheduler import scheduler_instance
import os
from datetime import datetime

management_bp = Blueprint('management', __name__, url_prefix='/management')

@management_bp.route('/')
@login_required
@admin_required
def index():
    """Management dashboard"""
    # Get statistics
    users = auth_manager.get_all_users()
    jobs = db.get_all_jobs()
    
    # Calculate stats
    stats = {
        'total_users': len(users),
        'active_users': len([u for u in users if u['is_active']]),
        'total_jobs': len(jobs),
        'active_jobs': len([j for j in jobs if j['status'] == 'active']),
        'downloads_today': len(db.get_download_logs_by_date(datetime.now().strftime('%Y-%m-%d'))),
    }
    
    return render_template('management/index.html', stats=stats)

# ============================================================================
# USER MANAGEMENT
# ============================================================================

@management_bp.route('/users')
@login_required
@admin_required
def users():
    """User management page"""
    users = auth_manager.get_all_users()
    return render_template('management/users.html', users=users)

@management_bp.route('/users/create', methods=['POST'])
@login_required
@admin_required
def create_user():
    """Create new user"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    full_name = data.get('full_name')
    role = data.get('role', 'user')
    
    # Validation
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username dan password harus diisi'}), 400
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password minimal 6 karakter'}), 400
    
    if role not in ['user', 'admin']:
        return jsonify({'success': False, 'message': 'Role tidak valid'}), 400
    
    # Create user
    user_id = auth_manager.create_user(username, password, email, full_name, role)
    
    if user_id:
        return jsonify({
            'success': True,
            'message': f'User {username} berhasil dibuat',
            'user_id': user_id
        })
    else:
        return jsonify({'success': False, 'message': 'Username sudah digunakan'}), 400

@management_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    """Update user"""
    data = request.get_json()
    
    # Don't allow updating own role
    if user_id == session['user_id'] and 'role' in data:
        return jsonify({'success': False, 'message': 'Tidak dapat mengubah role sendiri'}), 400
    
    success = auth_manager.update_user(user_id, **data)
    
    if success:
        return jsonify({'success': True, 'message': 'User berhasil diupdate'})
    else:
        return jsonify({'success': False, 'message': 'Gagal mengupdate user'}), 500

@management_bp.route('/users/<int:user_id>/password', methods=['PUT'])
@login_required
@admin_required
def reset_user_password(user_id):
    """Reset user password"""
    data = request.get_json()
    new_password = data.get('password')
    
    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password minimal 6 karakter'}), 400
    
    success = auth_manager.change_password(user_id, new_password)
    
    if success:
        return jsonify({'success': True, 'message': 'Password berhasil direset'})
    else:
        return jsonify({'success': False, 'message': 'Gagal mereset password'}), 500

@management_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user (soft delete)"""
    # Don't allow deleting own account
    if user_id == session['user_id']:
        return jsonify({'success': False, 'message': 'Tidak dapat menghapus akun sendiri'}), 400
    
    success = auth_manager.delete_user(user_id)
    
    if success:
        return jsonify({'success': True, 'message': 'User berhasil dihapus'})
    else:
        return jsonify({'success': False, 'message': 'Gagal menghapus user'}), 500

# ============================================================================
# SETTINGS MANAGEMENT
# ============================================================================

@management_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Settings management page"""
    settings = auth_manager.get_all_settings()
    
    # Group settings by category
    grouped_settings = {
        'general': [],
        'scheduler': [],
        'notification': [],
        'backup': [],
    }
    
    for setting in settings:
        key = setting['key']
        if key.startswith('app_') or key == 'maintenance_mode' or key == 'session_timeout':
            grouped_settings['general'].append(setting)
        elif key.startswith('max_concurrent') or 'job' in key:
            grouped_settings['scheduler'].append(setting)
        elif 'notification' in key or 'email' in key:
            grouped_settings['notification'].append(setting)
        elif 'backup' in key:
            grouped_settings['backup'].append(setting)
        else:
            grouped_settings['general'].append(setting)
    
    return render_template('management/settings.html', grouped_settings=grouped_settings)

@management_bp.route('/settings/update', methods=['POST'])
@login_required
@admin_required
def update_settings():
    """Update multiple settings"""
    data = request.get_json()
    updated = []
    failed = []
    
    for key, value in data.items():
        success = auth_manager.update_setting(key, value, session['username'])
        if success:
            updated.append(key)
        else:
            failed.append(key)
    
    if failed:
        return jsonify({
            'success': False,
            'message': f'Gagal mengupdate: {", ".join(failed)}',
            'updated': updated
        }), 500
    
    return jsonify({
        'success': True,
        'message': f'{len(updated)} pengaturan berhasil diupdate',
        'updated': updated
    })

# ============================================================================
# SYSTEM MANAGEMENT
# ============================================================================

@management_bp.route('/system')
@login_required
@admin_required
def system():
    """System information page"""
    # Get system info
    import platform
    
    system_info = {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'python_version': platform.python_version(),
        'cpu_percent': 0,  # Placeholder - requires psutil
        'memory_percent': 0,  # Placeholder - requires psutil
        'disk_percent': 0,  # Placeholder - requires psutil
    }
    
    # Get database info
    db_path = db.db_path
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    
    # Get scheduler info
    scheduler_jobs = scheduler_instance.get_all_jobs()
    
    return render_template('management/system.html', 
                         system_info=system_info,
                         db_size=db_size,
                         scheduler_jobs=len(scheduler_jobs))

@management_bp.route('/system/backup', methods=['POST'])
@login_required
@admin_required
def create_backup():
    """Create database backup"""
    try:
        import shutil
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups'
        
        # Create backups directory if not exists
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup crawler database
        crawler_db = 'crawler.db'
        if os.path.exists(crawler_db):
            backup_file = os.path.join(backup_dir, f'crawler_{timestamp}.db')
            shutil.copy2(crawler_db, backup_file)
        
        # Backup users database
        users_db = 'users.db'
        if os.path.exists(users_db):
            backup_file = os.path.join(backup_dir, f'users_{timestamp}.db')
            shutil.copy2(users_db, backup_file)
        
        return jsonify({
            'success': True,
            'message': f'Backup berhasil dibuat: {timestamp}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Gagal membuat backup: {str(e)}'
        }), 500

@management_bp.route('/system/logs')
@login_required
@admin_required
def view_logs():
    """View application logs"""
    log_file = 'logs/app.log'
    
    if not os.path.exists(log_file):
        return jsonify({'success': False, 'message': 'Log file tidak ditemukan'}), 404
    
    # Read last 100 lines
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        last_lines = lines[-100:] if len(lines) > 100 else lines
    
    return jsonify({
        'success': True,
        'logs': ''.join(last_lines)
    })
