"""
Authentication Routes Blueprint
Handles login, logout, and user management
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.auth import auth_manager, login_required, admin_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    # If already logged in, redirect to index
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Username dan password harus diisi.', 'danger')
            return render_template('auth/login.html')
        
        user = auth_manager.verify_user(username, password)
        
        if user:
            # Set session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            
            # Update last login
            auth_manager.update_last_login(username)
            
            # Set session permanent if remember me
            if remember:
                session.permanent = True
            
            flash(f'Selamat datang, {user["full_name"] or user["username"]}!', 'success')
            
            # Redirect to next page or index
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.index'))
        else:
            flash('Username atau password salah.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout handler"""
    username = session.get('username', 'User')
    session.clear()
    flash(f'Anda telah logout. Sampai jumpa, {username}!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = auth_manager.get_user_by_id(session['user_id'])
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change password handler"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        return jsonify({'success': False, 'message': 'Semua field harus diisi'}), 400
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'Password baru tidak cocok'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password minimal 6 karakter'}), 400
    
    # Verify current password
    user = auth_manager.verify_user(session['username'], current_password)
    if not user:
        return jsonify({'success': False, 'message': 'Password saat ini salah'}), 400
    
    # Change password
    success = auth_manager.change_password(session['user_id'], new_password)
    
    if success:
        return jsonify({'success': True, 'message': 'Password berhasil diubah'})
    else:
        return jsonify({'success': False, 'message': 'Gagal mengubah password'}), 500
