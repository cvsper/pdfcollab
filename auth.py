"""
Authentication blueprint for user login, registration, and password management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import re
from models import User
from supabase_client import SupabaseManager

auth_bp = Blueprint('auth', __name__)

def init_auth(app, db_manager):
    """Initialize authentication with the app"""
    global db
    db = db_manager

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    """Check if password meets strength requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is strong"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        # Validate input
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth/login.html')
        
        if not is_valid_email(email):
            flash('Please enter a valid email address', 'error')
            return render_template('auth/login.html')
        
        # Get user from database
        user_data = db.get_user_by_email(email)
        
        if not user_data:
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')
        
        user = User(user_data)
        
        # Check if account is locked
        if user.is_locked():
            flash('Account is temporarily locked due to too many failed login attempts. Please try again later.', 'error')
            return render_template('auth/login.html')
        
        # Check if account is active
        if not user.is_active:
            flash('Account is deactivated. Please contact administrator.', 'error')
            return render_template('auth/login.html')
        
        # Verify password
        if not user.check_password(password):
            # Increment failed login attempts
            db.increment_login_attempts(user.id)
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')
        
        # Login successful
        login_user(user, remember=remember_me)
        
        # Update login time
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        db.update_user_login(user.id, client_ip)
        
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        
        flash(f'Welcome back, {user.name or user.email}!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate input
        if not all([name, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        if not is_valid_email(email):
            flash('Please enter a valid email address', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        # Check password strength
        is_strong, message = is_strong_password(password)
        if not is_strong:
            flash(message, 'error')
            return render_template('auth/register.html')
        
        # Check if user already exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            flash('An account with this email already exists', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        password_hash = User.hash_password(password)
        user_id = db.create_user(email, password_hash, name)
        
        if user_id:
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Error creating account. Please try again.', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    user_name = current_user.name or current_user.email
    logout_user()
    flash(f'You have been logged out. Goodbye, {user_name}!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        
        # Validate input
        if not name or not email:
            flash('Name and email are required', 'error')
            return render_template('auth/profile.html')
        
        if not is_valid_email(email):
            flash('Please enter a valid email address', 'error')
            return render_template('auth/profile.html')
        
        # Check if email is taken by another user
        if email != current_user.email:
            existing_user = db.get_user_by_email(email)
            if existing_user:
                flash('This email address is already in use', 'error')
                return render_template('auth/profile.html')
        
        # Update profile
        profile_data = {'name': name, 'email': email}
        if db.update_user_profile(current_user.id, profile_data):
            # Update current user object
            current_user.name = name
            current_user.email = email
            flash('Profile updated successfully!', 'success')
        else:
            flash('Error updating profile. Please try again.', 'error')
    
    return render_template('auth/profile.html')

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate input
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('auth/change_password.html')
        
        # Verify current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'error')
            return render_template('auth/change_password.html')
        
        # Check new password
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('auth/change_password.html')
        
        # Check password strength
        is_strong, message = is_strong_password(new_password)
        if not is_strong:
            flash(message, 'error')
            return render_template('auth/change_password.html')
        
        # Update password
        new_password_hash = User.hash_password(new_password)
        if db.update_user_password(current_user.id, new_password_hash):
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Error changing password. Please try again.', 'error')
    
    return render_template('auth/change_password.html')

@auth_bp.route('/invite/<token>')
def accept_invitation(token):
    """Accept a document invitation"""
    if not token:
        flash('Invalid invitation link', 'error')
        return redirect(url_for('auth.login'))
    
    # Get invitation details
    invitation = db.get_invitation_by_token(token)
    
    if not invitation:
        flash('Invitation not found or has expired', 'error')
        return redirect(url_for('auth.login'))
    
    if invitation.get('accepted_at'):
        flash('This invitation has already been accepted', 'info')
        return redirect(url_for('dashboard'))
    
    # If user is not logged in, ask them to log in or register
    if not current_user.is_authenticated:
        session['invitation_token'] = token
        flash(f'Please log in or create an account to access the document "{invitation["documents"]["name"]}"', 'info')
        return redirect(url_for('auth.login'))
    
    # Accept the invitation
    if db.accept_invitation(token, current_user.id):
        flash(f'Successfully joined document "{invitation["documents"]["name"]}"!', 'success')
    else:
        flash('Error accepting invitation. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

@auth_bp.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard (admin only)"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all users and documents for admin overview
    users = db.get_all_users(current_user.id)
    
    # Get system statistics
    stats = {
        'total_users': len(users),
        'active_users': len([u for u in users if u.get('is_active', False)]),
        'admin_users': len([u for u in users if u.get('role') == 'admin']),
        'recent_logins': len([u for u in users if u.get('last_login')])
    }
    
    return render_template('admin/dashboard.html', users=users, stats=stats)

@auth_bp.route('/admin/users/<user_id>/deactivate', methods=['POST'])
@login_required
def deactivate_user(user_id):
    """Deactivate a user account (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400
    
    if db.deactivate_user(current_user.id, user_id):
        return jsonify({'success': True, 'message': 'User deactivated successfully'})
    else:
        return jsonify({'error': 'Error deactivating user'}), 500

@auth_bp.route('/admin/users/<user_id>/promote', methods=['POST'])
@login_required  
def promote_user(user_id):
    """Promote a user to admin (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    # This would need a method in supabase_client.py
    # For now, return not implemented
    return jsonify({'error': 'Feature not implemented yet'}), 501