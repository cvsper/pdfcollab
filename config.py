import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    """Application configuration class"""
    
    # Flask configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true' and FLASK_ENV != 'production'
    
    # Production Security Settings
    if FLASK_ENV == 'production':
        PREFERRED_URL_SCHEME = 'https'
        SESSION_COOKIE_SECURE = True
        WTF_CSRF_SSL_STRICT = True
    
    # Authentication configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # OAuth settings
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    OAUTH_REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')
    
    # Supabase API Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    # Supabase Database Configuration
    DB_USER = os.getenv('user', 'postgres')
    DB_PASSWORD = os.getenv('password')
    DB_HOST = os.getenv('host', 'localhost')
    DB_PORT = os.getenv('port', '5432')
    DB_NAME = os.getenv('dbname', 'postgres')
    
    # Construct SQLAlchemy Database URI
    if all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        # Fallback to SQLite for development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    
    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # Email Configuration (Optional)
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    FROM_EMAIL = os.getenv('FROM_EMAIL')
    
    # Upload configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    @classmethod
    def get_database_url(cls):
        """Get the database URL for logging purposes (without password)"""
        if cls.SQLALCHEMY_DATABASE_URI.startswith('postgresql://'):
            # Remove password for logging
            parts = cls.SQLALCHEMY_DATABASE_URI.replace('postgresql://', '').split('@')
            if len(parts) == 2:
                user_part = parts[0].split(':')[0]  # Remove password
                return f"postgresql://{user_part}:***@{parts[1]}"
        return cls.SQLALCHEMY_DATABASE_URI
    
    @classmethod
    def is_production(cls):
        """Check if running in production environment"""
        return cls.FLASK_ENV == 'production'