#!/usr/bin/env python3
"""
Authentication Routes and OAuth Integration
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from urllib.parse import urlencode
import secrets
import os

# Import our modules
from models import db, User
from forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm, ChangePasswordForm, ProfileForm
from email_utils import send_welcome_email, is_email_configured

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# OAuth configuration - will be initialized by app
oauth = None

def init_oauth(app):
    """Initialize OAuth with the Flask app"""
    global oauth
    oauth = OAuth(app)
    
    # Configure Google OAuth with explicit endpoints
    google = oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        access_token_url='https://oauth2.googleapis.com/token',
        access_token_params=None,
        refresh_token_url=None,
        redirect_uri=None,
        client_kwargs={
            'scope': 'openid email profile',
            'token_endpoint_auth_method': 'client_secret_basic'
        }
    )
    
    return oauth


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for username/password authentication"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Check if login is username or email
        username_or_email = form.username.data.strip()
        password = form.password.data
        
        # Try to find user by username or email
        user = None
        if '@' in username_or_email:
            user = User.find_by_email(username_or_email)
        else:
            user = User.find_by_username(username_or_email)
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been disabled. Please contact support.', 'error')
                return render_template('auth/login.html', form=form)
            
            # Log the user in
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password.', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page for new users"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            is_verified=False  # Will be verified via email or admin
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Send welcome email if configured
            if is_email_configured():
                try:
                    send_welcome_email(user.email, user.username)
                    flash('Registration successful! A welcome email has been sent. You can now log in.', 'success')
                except Exception as email_error:
                    current_app.logger.error(f"Welcome email failed: {email_error}")
                    flash('Registration successful! You can now log in. (Welcome email could not be sent)', 'success')
            else:
                flash('Registration successful! You can now log in.', 'success')
            
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            current_app.logger.error(f"Registration error: {e}")
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout current user"""
    username = current_user.username
    logout_user()
    flash(f'You have been logged out. Goodbye, {username}!', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    form = ProfileForm(current_user.username, current_user.email)
    
    if form.validate_on_submit():
        try:
            current_user.username = form.username.data.strip()
            current_user.email = form.email.data.strip().lower()
            db.session.commit()
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Profile update failed. Please try again.', 'error')
            current_app.logger.error(f"Profile update error: {e}")
    elif request.method == 'GET':
        # Pre-populate form with current user data
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('auth/profile.html', form=form)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Check current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/change_password.html', form=form)
        
        try:
            # Update password
            current_user.set_password(form.password.data)
            db.session.commit()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Password change failed. Please try again.', 'error')
            current_app.logger.error(f"Password change error: {e}")
    
    return render_template('auth/change_password.html', form=form)


# OAuth Routes
@auth_bp.route('/google')
def google_login():
    """Initiate Google OAuth login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Check if OAuth is configured
    if not oauth or not hasattr(oauth, 'google'):
        flash('Google OAuth is not configured. Please contact the administrator.', 'error')
        return redirect(url_for('auth.login'))
    
    # Check if Google credentials are available
    if not current_app.config.get('GOOGLE_CLIENT_ID') or not current_app.config.get('GOOGLE_CLIENT_SECRET'):
        flash('Google OAuth credentials are missing. Please contact the administrator.', 'error')
        return redirect(url_for('auth.login'))
    
    # Generate random state for security
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # Build redirect URI
    redirect_uri = url_for('auth.google_callback', _external=True)
    
    return oauth.google.authorize_redirect(redirect_uri, state=state)


@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Verify state parameter
    if request.args.get('state') != session.get('oauth_state'):
        flash('Invalid OAuth state. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Get access token
        token = oauth.google.authorize_access_token()
        
        # Get user info from Google using the People API
        resp = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
        user_info = resp.json()
        
        if not user_info:
            flash('Failed to get user information from Google.', 'error')
            return redirect(url_for('auth.login'))
        
        google_id = user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')
        
        if not google_id or not email:
            flash('Incomplete user information from Google.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user exists by Google ID
        user = User.find_by_google_id(google_id)
        
        if not user:
            # Check if user exists by email
            user = User.find_by_email(email)
            
            if user:
                # Link existing account with Google
                user.google_id = google_id
                user.avatar_url = picture
                db.session.commit()
            else:
                # Create new user
                username = email.split('@')[0]  # Use email prefix as username
                
                # Make sure username is unique
                counter = 1
                original_username = username
                while User.find_by_username(username):
                    username = f"{original_username}{counter}"
                    counter += 1
                
                user = User(
                    username=username,
                    email=email,
                    google_id=google_id,
                    avatar_url=picture,
                    is_verified=True  # Google accounts are pre-verified
                )
                
                db.session.add(user)
                db.session.commit()
                
                flash(f'Account created successfully! Welcome, {username}!', 'success')
        else:
            # Update avatar if it changed
            if user.avatar_url != picture:
                user.avatar_url = picture
                db.session.commit()
        
        # Log the user in
        login_user(user, remember=True)
        user.update_last_login()
        
        flash(f'Welcome, {user.username}!', 'success')
        
        # Redirect to next page or dashboard
        next_page = session.get('next_url')
        if next_page:
            session.pop('next_url', None)
            return redirect(next_page)
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Google OAuth error: {e}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    finally:
        # Clean up session
        session.pop('oauth_state', None)


# API Routes for frontend authentication
@auth_bp.route('/api/user')
@login_required
def api_current_user():
    """API endpoint to get current user info"""
    return jsonify({
        'user': current_user.to_dict(),
        'authenticated': True
    })


@auth_bp.route('/api/check-auth')
def api_check_auth():
    """API endpoint to check if user is authenticated"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        })
    else:
        return jsonify({
            'authenticated': False,
            'user': None
        })


# Password Reset Routes (for future implementation)
@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Request password reset (placeholder for email implementation)"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = PasswordResetRequestForm()
    
    if form.validate_on_submit():
        # TODO: Implement email sending functionality
        flash('Password reset instructions would be sent to your email (not implemented yet).', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token (placeholder for email implementation)"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # TODO: Implement token verification
    form = PasswordResetForm()
    
    if form.validate_on_submit():
        # TODO: Implement password reset logic
        flash('Password reset functionality not yet implemented.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)