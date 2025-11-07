# Login & Management System

Dokumentasi sistem login dan manajemen pengguna untuk BPS Web Crawler.

---

## Overview

Sistem ini menambahkan:

- **Authentication System** - Login/logout dengan session management
- **User Management** - CRUD operasi untuk user
- **Settings Management** - Konfigurasi aplikasi
- **System Information** - Monitoring resource dan logs

---

## Default Admin Account

```
Username: admin
Password: admin123
```

**⚠️ PENTING:** Segera ubah password default setelah login pertama kali!

---

## Features

### 1. Authentication

#### Login Page (`/auth/login`)

- Form login dengan username & password
- "Remember me" checkbox untuk persistent session
- Redirect ke halaman sebelumnya setelah login

#### Logout (`/auth/logout`)

- Clear session dan redirect ke login page

#### Profile Page (`/auth/profile`)

- Lihat informasi user (username, email, role, dll)
- Ubah password sendiri

### 2. User Management (`/management/users`)

**Access:** Admin only

**Features:**

- **View Users** - Daftar semua user dengan status
- **Create User** - Tambah user baru dengan role (user/admin)
- **Edit User** - Update email, nama, role, status
- **Reset Password** - Reset password user lain (admin)
- **Delete User** - Soft delete (set inactive)

**Validasi:**

- Username harus unique
- Password minimal 6 karakter
- Admin tidak bisa hapus akun sendiri
- Admin tidak bisa ubah role sendiri

### 3. Settings Management (`/management/settings`)

**Access:** Admin only

**Kategori Settings:**

#### General

- `app_name` - Nama aplikasi
- `maintenance_mode` - Mode maintenance (true/false)
- `session_timeout` - Timeout session (detik)

#### Scheduler

- `max_concurrent_jobs` - Max job bersamaan

#### Notification

- `enable_notifications` - Enable notifikasi email
- `notification_email` - Email tujuan notifikasi

#### Backup

- `auto_backup` - Auto backup database
- `backup_retention_days` - Lama simpan backup

### 4. System Information (`/management/system`)

**Access:** Admin only

**Informasi:**

- Platform & Python version
- Database size
- Scheduler jobs count
- Resource usage (CPU, Memory, Disk) - requires psutil

**Actions:**

- Create database backup
- View application logs
- Refresh information

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    full_name TEXT,
    role TEXT DEFAULT 'user',
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    last_login TEXT
);
```

### App Settings Table

```sql
CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    description TEXT,
    updated_at TEXT NOT NULL,
    updated_by TEXT
);
```

---

## API Endpoints

### Authentication

| Method   | Endpoint                | Description          | Access        |
| -------- | ----------------------- | -------------------- | ------------- |
| GET/POST | `/auth/login`           | Login page & handler | Public        |
| GET      | `/auth/logout`          | Logout handler       | Authenticated |
| GET      | `/auth/profile`         | User profile page    | Authenticated |
| POST     | `/auth/change-password` | Change own password  | Authenticated |

### Management

| Method | Endpoint                          | Description          | Access |
| ------ | --------------------------------- | -------------------- | ------ |
| GET    | `/management/`                    | Management dashboard | Admin  |
| GET    | `/management/users`               | User management page | Admin  |
| POST   | `/management/users/create`        | Create new user      | Admin  |
| PUT    | `/management/users/<id>`          | Update user          | Admin  |
| PUT    | `/management/users/<id>/password` | Reset user password  | Admin  |
| DELETE | `/management/users/<id>`          | Delete user          | Admin  |
| GET    | `/management/settings`            | Settings page        | Admin  |
| POST   | `/management/settings/update`     | Update settings      | Admin  |
| GET    | `/management/system`              | System info page     | Admin  |
| POST   | `/management/system/backup`       | Create backup        | Admin  |
| GET    | `/management/system/logs`         | View logs            | Admin  |

---

## Usage Examples

### 1. Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123&remember=1
```

### 2. Create User

```javascript
fetch("/management/users/create", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "user1",
    password: "password123",
    full_name: "User Satu",
    email: "user1@bps.go.id",
    role: "user",
  }),
});
```

### 3. Update Settings

```javascript
fetch("/management/settings/update", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    app_name: "BPS Crawler Pro",
    max_concurrent_jobs: "5",
    enable_notifications: "true",
  }),
});
```

### 4. Create Backup

```javascript
fetch("/management/system/backup", {
  method: "POST",
});
```

---

## Security Features

### Password Hashing

- Menggunakan **Werkzeug** `generate_password_hash()` & `check_password_hash()`
- Hashing algorithm: **pbkdf2:sha256**

### Session Management

- Flask session dengan secure cookie
- Session timeout configurable
- "Remember me" untuk persistent session

### Access Control

- `@login_required` decorator untuk authenticated routes
- `@admin_required` decorator untuk admin-only routes
- Role-based access control (RBAC)

### Protection

- Password minimal 6 karakter
- Username unique constraint
- Soft delete untuk user (preserve history)
- Admin tidak bisa delete/modify sendiri

---

## File Structure

```
app/
├── auth.py                          # Auth manager & decorators
├── auth_routes.py                   # Login/logout routes
├── management_routes.py             # User/settings management
├── templates/
│   ├── auth/
│   │   ├── login.html              # Login page
│   │   └── profile.html            # User profile
│   └── management/
│       ├── index.html              # Dashboard
│       ├── users.html              # User management
│       ├── settings.html           # Settings management
│       └── system.html             # System info
users.db                             # User & settings database
```

---

## Configuration

### Config.py

```python
class Config:
    SECRET_KEY = 'your-secret-key-here'  # Change in production!
    PERMANENT_SESSION_LIFETIME = 86400    # 24 hours
```

### Environment Variables

```bash
FLASK_SECRET_KEY=your-super-secret-key-change-this
```

---

## Testing

### 1. Login Test

```bash
# Start server
python run.py

# Navigate to http://localhost:5000
# Should redirect to /auth/login
# Login with: admin / admin123
```

### 2. User Management Test

```bash
# Login as admin
# Go to dropdown menu > Management
# Click "Kelola User"
# Create new user
# Edit user
# Reset password
# Delete user (except admin)
```

### 3. Settings Test

```bash
# Login as admin
# Go to dropdown menu > Settings
# Change any setting
# Click "Simpan Pengaturan"
# Verify changes saved
```

### 4. System Info Test

```bash
# Login as admin
# Go to dropdown menu > System Info
# Check system details
# Click "Create Backup" - should create backup file
# Click "View Logs" - should display logs
```

---

## Troubleshooting

### Cannot Login

**Problem:** Username/password salah

**Solution:**

- Pastikan menggunakan: `admin` / `admin123`
- Cek `users.db` sudah ter-create
- Restart server jika perlu

### Database Error

**Problem:** `sqlite3.OperationalError: no such table: users`

**Solution:**

```bash
# Delete database and restart
Remove-Item users.db
python run.py
```

### Session Expired

**Problem:** Terus diminta login

**Solution:**

- Centang "Ingat saya" saat login
- Periksa `PERMANENT_SESSION_LIFETIME` di config
- Clear browser cookies

### Access Denied

**Problem:** "Anda tidak memiliki hak akses"

**Solution:**

- Pastikan login sebagai admin
- Periksa role di database:
  ```sql
  SELECT username, role FROM users;
  ```
- Update role jika perlu:
  ```sql
  UPDATE users SET role='admin' WHERE username='admin';
  ```

---

## Best Practices

### Security

1. **Ubah Secret Key:**

   ```python
   SECRET_KEY = 'your-random-secret-key-here'
   ```

2. **Ubah Default Password:**

   - Login → Profile → Ubah Password

3. **HTTPS di Production:**

   - Deploy dengan HTTPS/SSL
   - Set `SESSION_COOKIE_SECURE = True`

4. **Regular Backup:**
   - Enable auto backup di settings
   - Backup manual sebelum update

### User Management

1. **Principle of Least Privilege:**

   - Beri role `user` by default
   - Role `admin` hanya untuk keperluan management

2. **Strong Password:**

   - Minimal 8-12 karakter
   - Kombinasi huruf, angka, simbol

3. **Audit Trail:**
   - Monitor `last_login` untuk aktivitas user
   - Check settings `updated_by`

---

## Upgrade from Previous Version

### Migration Steps

1. **Backup existing data:**

   ```bash
   Copy-Item crawler.db crawler_backup.db
   Copy-Item scheduler_jobs.json scheduler_jobs_backup.json
   ```

2. **Start server:**

   ```bash
   python run.py
   ```

3. **Auto-initialization:**

   - `users.db` akan dibuat otomatis
   - Default admin user ter-create
   - Default settings ter-create

4. **First login:**

   - Login dengan: `admin` / `admin123`
   - Ubah password segera

5. **Create additional users:**
   - Management → Users → Tambah User

---

## Future Enhancements

- [ ] Email notification system
- [ ] Two-factor authentication (2FA)
- [ ] API key authentication
- [ ] User activity logging
- [ ] Role permission customization
- [ ] LDAP/Active Directory integration
- [ ] Password reset via email
- [ ] Account lockout after failed attempts

---

## Support

Untuk pertanyaan atau issue, hubungi administrator sistem atau buka issue di repository.

---

**Version:** 2.1.0  
**Date:** November 2025  
**Author:** BPS Development Team
