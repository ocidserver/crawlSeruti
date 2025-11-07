"""
Authentication and User Management Module
"""
from functools import wraps
from flask import session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

class AuthManager:
    """Manages authentication and user operations"""
    
    def __init__(self, db_path='users.db'):
        """Initialize auth manager with database path"""
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize users database and create default admin"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        ''')
        
        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT,
                updated_at TEXT NOT NULL,
                updated_by TEXT
            )
        ''')
        
        # Check if admin exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            # Create default admin user
            admin_hash = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', admin_hash, 'admin@bps.go.id', 'Administrator', 'admin', datetime.now().isoformat()))
            print("✓ Default admin user created (username: admin, password: admin123)")
        
        # Initialize default settings
        default_settings = [
            ('app_name', 'BPS Web Crawler System', 'Application name'),
            ('maintenance_mode', 'false', 'Enable/disable maintenance mode'),
            ('max_concurrent_jobs', '3', 'Maximum concurrent crawler jobs'),
            ('session_timeout', '3600', 'Session timeout in seconds'),
            ('enable_notifications', 'true', 'Enable email notifications'),
            ('notification_email', 'admin@bps.go.id', 'Notification recipient email'),
            ('auto_backup', 'true', 'Enable automatic database backup'),
            ('backup_retention_days', '30', 'Days to keep backup files'),
        ]
        
        for key, value, description in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO app_settings (key, value, description, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (key, value, description, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM users 
            WHERE username = ? AND is_active = 1
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            return dict(user)
        return None
    
    def update_last_login(self, username):
        """Update user's last login timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET last_login = ? 
            WHERE username = ?
        ''', (datetime.now().isoformat(), username))
        
        conn.commit()
        conn.close()
    
    def get_all_users(self):
        """Get all users (without password hashes)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, full_name, role, is_active, 
                   created_at, last_login
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, full_name, role, is_active, 
                   created_at, last_login
            FROM users
            WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def create_user(self, username, password, email=None, full_name=None, role='user'):
        """Create new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = generate_password_hash(password)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, email, full_name, role, datetime.now().isoformat()))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        allowed_fields = ['email', 'full_name', 'role', 'is_active']
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def change_password(self, user_id, new_password):
        """Change user password"""
        password_hash = generate_password_hash(new_password)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET password_hash = ? 
            WHERE id = ?
        ''', (password_hash, user_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def delete_user(self, user_id):
        """Delete user (soft delete by setting is_active to 0)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def get_setting(self, key):
        """Get application setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM app_settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_all_settings(self):
        """Get all application settings"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM app_settings ORDER BY key')
        settings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return settings
    
    def update_setting(self, key, value, updated_by=None):
        """Update application setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE app_settings 
            SET value = ?, updated_at = ?, updated_by = ?
            WHERE key = ?
        ''', (value, datetime.now().isoformat(), updated_by, key))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success


# Global auth manager instance
auth_manager = AuthManager()


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if session.get('role') != 'admin':
            flash('Akses ditolak. Anda tidak memiliki hak akses.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function
