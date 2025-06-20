from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from enum import Enum
import json
import bcrypt

db = SQLAlchemy()

class DocumentStatus(Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class User(UserMixin, db.Model):
    """User model for authentication and document assignment"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    role = db.Column(db.String(20), default='user')  # 'user', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # OAuth fields
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    
    # Relationships
    documents_created = db.relationship('Document', foreign_keys='Document.created_by_id', backref='creator')
    field_assignments = db.relationship('DocumentField', backref='assigned_user')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set password hash using bcrypt"""
        password_bytes = password.encode('utf-8')
        self.password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check password against hash using bcrypt"""
        if not self.password_hash:
            return False
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    # Flask-Login required methods
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def is_admin(self):
        return self.role == 'admin'
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_by_google_id(google_id):
        """Find user by Google ID"""
        return User.query.filter_by(google_id=google_id).first()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'avatar_url': self.avatar_url
        }

class Document(db.Model):
    """Document model for PDF documents"""
    __tablename__ = 'documents'
    
    id = db.Column(db.String(50), primary_key=True)  # UUID
    name = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    status = db.Column(db.Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # JSON field for storing document metadata
    doc_metadata = db.Column(db.JSON, default=lambda: {})
    
    # Relationships
    fields = db.relationship('DocumentField', backref='document', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Document {self.name}>'
    
    def to_dict(self):
        # Get user data from metadata for template compatibility
        user1_data = self.doc_metadata.get('user1_data', {})
        user2_data = self.doc_metadata.get('user2_data', {})
        
        return {
            'id': self.id,
            'name': self.name,
            'original_filename': self.original_filename,
            'status': self.status.value if self.status else 'Draft',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'lastUpdated': self.updated_at.strftime('%B %d, %Y') if self.updated_at else 'Recently',
            'metadata': self.doc_metadata,
            'fields_count': len(self.fields) if self.fields else 0,
            # Template compatibility fields
            'user1_data': user1_data,
            'user2_data': user2_data,
            'invitation_sent': self.doc_metadata.get('invitation_sent', False),
            'invitation_sent_at': self.doc_metadata.get('invitation_sent_at')
        }
    
    def get_fields_by_user(self, user_role):
        """Get fields assigned to a specific user role"""
        return [field for field in self.fields if field.assigned_to == user_role]
    
    def is_complete(self):
        """Check if all required fields are filled"""
        return all(field.value for field in self.fields if field.required)

class FieldType(Enum):
    TEXT = "text"
    EMAIL = "email" 
    TEL = "tel"
    DATE = "date"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    SIGNATURE = "signature"

class DocumentField(db.Model):
    """Individual field within a document"""
    __tablename__ = 'document_fields'
    
    id = db.Column(db.String(50), primary_key=True)  # UUID
    document_id = db.Column(db.String(50), db.ForeignKey('documents.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    pdf_field_name = db.Column(db.String(255), nullable=True)  # Original PDF field name
    field_type = db.Column(db.Enum(FieldType), nullable=False)
    value = db.Column(db.Text, nullable=True)
    required = db.Column(db.Boolean, default=False)
    assigned_to = db.Column(db.String(20), nullable=False)  # 'user1', 'user2', etc.
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Position and styling information
    position = db.Column(db.JSON, default=lambda: {})  # {x, y, width, height, page}
    styling = db.Column(db.JSON, default=lambda: {})   # Font, color, etc.
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    filled_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<DocumentField {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'pdf_field_name': self.pdf_field_name,
            'type': self.field_type.value if self.field_type else None,
            'value': self.value,
            'required': self.required,
            'assigned_to': self.assigned_to,
            'position': self.position,
            'styling': self.styling,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'filled_at': self.filled_at.isoformat() if self.filled_at else None
        }
    
    def mark_as_filled(self):
        """Mark field as filled and update timestamp"""
        self.filled_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class AuditLog(db.Model):
    """Audit log for tracking changes"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.String(50), db.ForeignKey('documents.id'), nullable=True)
    field_id = db.Column(db.String(50), db.ForeignKey('document_fields.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # 'create', 'update', 'delete', 'fill'
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<AuditLog {self.action} at {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'field_id': self.field_id,
            'user_id': self.user_id,
            'action': self.action,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address
        }

class PDFConfiguration(db.Model):
    """Configuration for real-time PDF editing"""
    __tablename__ = 'pdf_configurations'
    
    id = db.Column(db.String(50), primary_key=True)  # UUID
    document_id = db.Column(db.String(50), db.ForeignKey('documents.id'), nullable=False)
    pdf_info = db.Column(db.JSON, default=lambda: {})  # PDF dimensions, page count, etc.
    field_mapping = db.Column(db.JSON, default=lambda: {})  # PDF field name to our field ID mapping
    rendering_config = db.Column(db.JSON, default=lambda: {})  # Zoom, display settings, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    document = db.relationship('Document', backref='pdf_config')
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'pdf_info': self.pdf_info,
            'field_mapping': self.field_mapping,
            'rendering_config': self.rendering_config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RealTimeSession(db.Model):
    """Track real-time editing sessions"""
    __tablename__ = 'realtime_sessions'
    
    id = db.Column(db.String(50), primary_key=True)  # Session UUID
    document_id = db.Column(db.String(50), db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_data = db.Column(db.JSON, default=lambda: {})  # Current field values, cursor position, etc.
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    document = db.relationship('Document', backref='realtime_sessions')
    user = db.relationship('User', backref='realtime_sessions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'user_id': self.user_id,
            'session_data': self.session_data,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }