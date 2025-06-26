# 🔐 Authentication System Setup Guide

## Overview

This PDF Collaborator application now includes a comprehensive authentication system with:

- **Username/Password Authentication** with secure password hashing (bcrypt)
- **Google OAuth Integration** for social login
- **Session Management** with Flask-Login
- **Form Validation** with Flask-WTF
- **User Profile Management** with avatar support
- **Secure Route Protection** for all sensitive areas

## 🚀 Quick Start

### 1. Install Dependencies

All authentication dependencies are already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Key authentication packages:
- `Flask-Login==0.6.3` - Session management
- `Flask-WTF==1.2.1` - Form handling and CSRF protection
- `WTForms==3.1.1` - Form validation
- `Authlib==1.3.0` - OAuth integration
- `bcrypt==4.1.2` - Password hashing
- `email-validator==2.1.0` - Email validation

### 2. Database Setup

The authentication system uses the existing User model with enhancements:

```bash
# The app will automatically create tables on first run
python3 app.py
```

### 3. Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Required for basic auth
FLASK_SECRET_KEY=your-secure-secret-key-here

# Optional: Google OAuth (see setup instructions below)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

SERVER_NAME=pdfcollab.onrender.com
PREFERRED_URL_SCHEME=https
```

## 🔧 Features

### User Registration & Login

**Registration Form** (`/auth/register`):
- Username validation (3-20 characters)
- Email validation with uniqueness check
- Strong password requirements (8+ characters)
- Password confirmation matching
- Terms of service acceptance
- Automatic password hashing with bcrypt

**Login Form** (`/auth/login`):
- Username or email login
- Password verification
- "Remember me" functionality
- Session management
- Secure redirects

### Google OAuth Integration

**Social Login Features**:
- One-click Google sign-in
- Automatic account creation
- Avatar import from Google
- Email verification bypass for OAuth users
- Seamless account linking

### Security Features

**Password Security**:
- bcrypt hashing with salt
- Secure password storage
- Password strength validation
- Protection against timing attacks

**Session Security**:
- Secure session cookies
- CSRF protection on all forms
- HttpOnly and Secure cookie flags
- Configurable session timeouts

**Route Protection**:
- `@login_required` decorators
- Automatic redirects to login
- User context throughout application
- Role-based access control ready

## 🌐 Google OAuth Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the following APIs:
   - Google+ API
   - Google OAuth2 API

### 2. Create OAuth Credentials

1. Navigate to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
2. Application type: "Web application"
3. Name: "PDF Collaborator"
4. Authorized redirect URIs:
   ```
   http://localhost:5006/auth/google/callback
   http://your-domain.com/auth/google/callback  # for production
   ```

### 3. Configure Environment

Add to your `.env` file:

```env
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
OAUTH_REDIRECT_URI=https://pdfcollab.onrender.com/dashboard
```

## 🗂️ File Structure

```
├── auth.py                 # Authentication routes and OAuth
├── models.py              # Enhanced User model with auth
├── forms.py               # Registration and login forms
├── config.py              # Authentication configuration
├── templates/auth/        # Authentication templates
│   ├── login.html
│   └── register.html
└── templates/base.html    # Updated with auth context
```

## 🧪 Testing

### Manual Testing

1. **Start the application**:
   ```bash
   python3 app.py
   ```

2. **Test authentication flow**:
   - Visit `http://localhost:5006` (should redirect to login)
   - Register a new account at `/auth/register`
   - Login with credentials at `/auth/login`
   - Test Google OAuth (if configured)
   - Access protected routes

### Automated Testing

Run the test script:

```bash
python3 test_auth.py
```

This tests:
- Route protection
- Login page accessibility
- Registration page accessibility
- Google OAuth initialization

## 🔒 Security Best Practices

### Implemented

✅ **Password Security**:
- bcrypt hashing with adaptive rounds
- Secure password storage
- No plaintext passwords

✅ **Session Security**:
- Secure session cookies
- HttpOnly flags
- CSRF protection
- Session timeouts

✅ **Input Validation**:
- Form validation with WTForms
- Email format validation
- Username uniqueness checks
- SQL injection prevention

✅ **OAuth Security**:
- State parameter validation
- Secure token handling
- Proper scope management

### Recommended Additional Measures

🔲 **Rate Limiting**: Add login attempt limiting
🔲 **2FA Support**: Implement two-factor authentication
🔲 **Password Reset**: Email-based password recovery
🔲 **Account Verification**: Email verification for new accounts
🔲 **Audit Logging**: Track authentication events

## 🚀 Usage Examples

### Register a New User

```python
# POST to /auth/register
{
    "username": "john_doe",
    "email": "john@example.com", 
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "terms": true
}
```

### Login with Credentials

```python
# POST to /auth/login
{
    "username": "john_doe",  # or email
    "password": "SecurePass123!",
    "remember_me": true
}
```

### Check Authentication Status

```python
from flask_login import current_user

if current_user.is_authenticated:
    print(f"Logged in as: {current_user.username}")
    print(f"Email: {current_user.email}")
    print(f"Admin: {current_user.is_admin()}")
```

### Protect Routes

```python
from flask_login import login_required

@app.route('/protected')
@login_required
def protected_route():
    return f"Hello {current_user.username}!"
```

## 🎨 UI Components

### Authentication Templates

**Modern, Responsive Design**:
- Clean login/register forms
- Google OAuth button with official styling
- Error message display
- Mobile-friendly responsive layout
- Consistent with application theme

**User Interface Elements**:
- User avatar display
- Dropdown user menu
- Login/logout links
- Profile information display
- Session status indicators

## 🔧 Customization

### Adding New OAuth Providers

1. Install provider-specific library
2. Add OAuth configuration to `config.py`
3. Create OAuth route in `auth.py`
4. Add provider button to templates

### Custom User Fields

1. Add fields to `User` model in `models.py`
2. Update registration form in `forms.py`
3. Modify registration template
4. Handle new fields in auth routes

### Email Verification

1. Configure SMTP settings in `.env`
2. Add verification fields to User model
3. Create email templates
4. Implement verification routes

## 📋 Troubleshooting

### Common Issues

**"No module named 'bcrypt'"**:
```bash
pip install bcrypt==4.1.2
```

**"CSRF token missing"**:
- Ensure `{{ form.hidden_tag() }}` in templates
- Check `WTF_CSRF_ENABLED` configuration

**Google OAuth errors**:
- Verify redirect URIs in Google Console
- Check client ID/secret configuration
- Ensure proper API enablement

**Database errors**:
- Delete existing database file for schema updates
- Check SQLite permissions
- Verify database initialization

## 🚀 Production Deployment

### Security Configuration

```env
FLASK_ENV=production
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

### Database Migration

For production with PostgreSQL:

```env
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### HTTPS Requirements

- Google OAuth requires HTTPS in production
- Update redirect URIs for production domain
- Configure SSL certificates
- Set secure cookie flags

---

## ✅ Authentication System Complete!

The PDF Collaborator now has a production-ready authentication system with:

- ✅ Secure user registration and login
- ✅ Google OAuth integration
- ✅ Session management and security
- ✅ Route protection and user context
- ✅ Modern, responsive UI
- ✅ Comprehensive error handling
- ✅ Security best practices

Users can now securely sign up and access the PDF collaboration features!