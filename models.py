"""
User models for Flask-Login authentication system
"""

from flask_login import UserMixin
from datetime import datetime
import bcrypt

class User(UserMixin):
    """User model for Flask-Login"""
    
    def __init__(self, user_data):
        """Initialize user from database record"""
        self.id = user_data['id']
        self.email = user_data['email'] 
        self.name = user_data.get('name', '')
        self.role = user_data.get('role', 'user')
        self.is_active = user_data.get('is_active', True)
        self.email_verified = user_data.get('email_verified', False)
        self.created_at = user_data.get('created_at')
        self.last_login = user_data.get('last_login')
        self.login_attempts = user_data.get('login_attempts', 0)
        self.locked_until = user_data.get('locked_until')
        self._password_hash = user_data.get('password_hash', '')
    
    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return str(self.id)
    
    def is_authenticated(self):
        """Return True if user is authenticated"""
        return True
    
    def is_anonymous(self):
        """Return False as this is not an anonymous user"""
        return False
    
    def is_admin(self):
        """Return True if user has admin role"""
        return self.role == 'admin'
    
    def check_password(self, password):
        """Check if provided password matches stored hash"""
        if not self._password_hash:
            return False
        
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self._password_hash.encode('utf-8'))
        except Exception as e:
            print(f"Error checking password: {e}")
            return False
    
    @staticmethod
    def hash_password(password):
        """Generate password hash"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def is_locked(self):
        """Check if account is currently locked"""
        if not self.locked_until:
            return False
        
        try:
            from dateutil.parser import parse
            locked_until = parse(self.locked_until)
            return datetime.now() < locked_until.replace(tzinfo=None)
        except Exception:
            return False
    
    def can_access_document(self, document_id, db_manager):
        """Check if user can access a specific document"""
        try:
            # Admins can access all documents
            if self.is_admin():
                return True
            
            # Check if user is owner or has access through user_documents
            user_docs = db_manager.get_user_documents(self.id)
            
            for doc in user_docs:
                if doc['id'] == document_id:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking document access: {e}")
            return False
    
    def can_edit_document(self, document_id, db_manager):
        """Check if user can edit a specific document"""
        try:
            # Admins can edit all documents
            if self.is_admin():
                return True
            
            # Check if user has edit permissions
            user_docs = db_manager.get_user_documents(self.id)
            
            for doc in user_docs:
                if doc['id'] == document_id:
                    user_doc_info = doc.get('user_documents', {})
                    return user_doc_info.get('can_edit', False)
            
            return False
            
        except Exception as e:
            print(f"Error checking document edit permissions: {e}")
            return False
    
    def get_role_in_document(self, document_id, db_manager):
        """Get user's role in a specific document"""
        try:
            user_docs = db_manager.get_user_documents(self.id)
            
            for doc in user_docs:
                if doc['id'] == document_id:
                    user_doc_info = doc.get('user_documents', {})
                    return user_doc_info.get('role', 'viewer')
            
            return None
            
        except Exception as e:
            print(f"Error getting document role: {e}")
            return None
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class AnonymousUser:
    """Anonymous user class for non-authenticated users"""
    
    def __init__(self):
        self.id = None
        self.email = None
        self.name = None
        self.role = None
        self.is_active = False
    
    def is_authenticated(self):
        return False
    
    def is_anonymous(self):
        return True
    
    def is_admin(self):
        return False
    
    def can_access_document(self, document_id, db_manager):
        return False
    
    def can_edit_document(self, document_id, db_manager):
        return False
    
    def get_role_in_document(self, document_id, db_manager):
        return None
    
    def get_id(self):
        return None