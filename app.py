from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import PyPDF2
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import json
import base64
from io import BytesIO
import logging
import sys

# Import new modules
from config import Config
from models import db, Document, DocumentField, User, AuditLog, DocumentStatus, FieldType
from pdf_processor import PDFProcessor

# Optional imports for enhanced features
try:
    from supabase_api import supabase_api
except ImportError:
    print("Warning: supabase_api module not available")
    supabase_api = None

# Removed SocketIO/realtime functionality for simpler deployment

# Make auth completely optional for deployment
try:
    from auth import auth_bp, init_oauth
    AUTH_AVAILABLE = True
except ImportError:
    print("Warning: auth module not available - using minimal auth")
    auth_bp = None
    init_oauth = None
    AUTH_AVAILABLE = False

from email_utils import send_document_completion_email, send_welcome_email, send_document_invitation_email, is_email_configured

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging for production
if Config.is_production():
    # Production logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )
    
    # Set specific log levels
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Application logger
    app.logger.setLevel(logging.INFO)
    app.logger.info("PDF Collaborator starting in production mode")
else:
    # Development logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.info("PDF Collaborator starting in development mode")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' if auth_bp else None
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Initialize OAuth (optional)
oauth = init_oauth(app) if init_oauth else None

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Add public route for unauthenticated users
@app.route('/public')
def public_home():
    """Public landing page for unauthenticated users"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login') if auth_bp else '/')

# Health check endpoint for monitoring
@app.route('/health')
def health_check():
    """Health check endpoint for load balancers and monitoring"""
    try:
        # Check database connectivity
        if USE_DATABASE and db:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db_status = "connected"
        else:
            db_status = "not_configured"
        
        # Check email service configuration
        email_configured = is_email_configured()
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": os.getenv('FLASK_ENV', 'development'),
            "services": {
                "database": db_status,
                "email": "configured" if email_configured else "not_configured"
            }
        }
        
        return jsonify(health_data), 200
        
    except Exception as e:
        error_data = {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "environment": os.getenv('FLASK_ENV', 'development')
        }
        return jsonify(error_data), 503

# Register blueprints (optional)
if auth_bp:
    app.register_blueprint(auth_bp, url_prefix='/auth')
else:
    # Minimal auth fallback routes
    @app.route('/auth/login')
    def fallback_login():
        return '''
        <html>
        <head><title>Login - PDF Collaborator</title></head>
        <body style="font-family: Arial; margin: 40px; text-align: center;">
            <h2>Login</h2>
            <p>Authentication module not available</p>
            <a href="/" style="color: #3b82f6;">← Back to Home</a>
        </body>
        </html>
        '''

# Initialize database and PDF processor
try:
    db.init_app(app)
    pdf_processor = PDFProcessor()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        print("✅ Connected to Supabase database with SQLAlchemy")
        print(f"📊 Database URL: {Config.get_database_url()}")
        
        # Check Supabase API availability
        if supabase_api and supabase_api.is_available():
            print("📡 Supabase API client ready for advanced features")
        else:
            print("⚠️  Supabase API not available (using database only)")
    
    USE_DATABASE = True
except Exception as e:
    print(f"⚠️  Database connection failed: {e}")
    print("🔄 Falling back to in-memory storage")
    USE_DATABASE = False

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USERNAME)

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Mock data for development (matching your React wireframe data)
# In production, set FLASK_ENV=production to disable mock data
MOCK_DOCUMENTS = [
    {
        'id': '1',
        'name': 'Employment Contract',
        'status': 'Awaiting User 2',
        'lastUpdated': '2 hours ago',
        'created_at': datetime.now().isoformat(),
        'created_by': None,  # No owner - won't appear for any user
        'user1_data': {'name': 'John Doe', 'email': 'john@example.com'}
    },
    {
        'id': '2', 
        'name': 'Rental Agreement',
        'status': 'Signed & Sent',
        'lastUpdated': '1 day ago',
        'created_at': datetime.now().isoformat(),
        'completed_at': datetime.now().isoformat(),
        'created_by': None,  # No owner - won't appear for any user
        'user1_data': {'name': 'Alice Smith', 'email': 'alice@example.com'},
        'user2_data': {'name': 'Bob Johnson', 'email': 'bob@example.com'}
    },
    {
        'id': '3',
        'name': 'Insurance Form', 
        'status': 'Awaiting User 1',
        'lastUpdated': '3 days ago',
        'created_at': datetime.now().isoformat(),
        'created_by': None  # No owner - won't appear for any user
    },
    {
        'id': 'working_example',
        'name': 'Working Example with Field Values.pdf',
        'status': 'Signed & Sent',
        'lastUpdated': 'Just created',
        'created_at': datetime.now().isoformat(),
        'completed_at': datetime.now().isoformat(),
        'created_by': None,  # No owner - won't appear for any user
        'user1_data': {
            'name': 'John Test User',
            'email': 'john@test.com',
            'employee_id': 'TEST001',
            'department': 'Testing'
        },
        'user2_data': {
            'name': 'Jane Test Manager',
            'email': 'jane@test.com',
            'signature': 'Jane Test Manager',
            'date_signed': datetime.now().isoformat()
        },
        'pdf_fields': [
            {
                'id': 'working_field_1',
                'name': 'Employee Full Name',
                'type': 'text',
                'value': 'John Test User - Employee',
                'assigned_to': 'user1',
                'source': 'working_example'
            },
            {
                'id': 'working_field_2',
                'name': 'Employee Email Address',
                'type': 'email',
                'value': 'john.employee@company.com',
                'assigned_to': 'user1',
                'source': 'working_example'
            },
            {
                'id': 'working_field_3',
                'name': 'Employee Phone',
                'type': 'tel',
                'value': '+1-555-TEST-001',
                'assigned_to': 'user1',
                'source': 'working_example'
            },
            {
                'id': 'working_field_4',
                'name': 'Employee Department',
                'type': 'text',
                'value': 'Software Engineering',
                'assigned_to': 'user1',
                'source': 'working_example'
            },
            {
                'id': 'working_field_5',
                'name': 'Manager Name',
                'type': 'text',
                'value': 'Jane Test Manager - Supervisor',
                'assigned_to': 'user2',
                'source': 'working_example'
            },
            {
                'id': 'working_field_6',
                'name': 'Manager Signature',
                'type': 'signature',
                'value': 'Jane Test Manager Digital Signature',
                'assigned_to': 'user2',
                'source': 'working_example'
            },
            {
                'id': 'working_field_7',
                'name': 'Approval Notes',
                'type': 'textarea',
                'value': 'This employee has been approved for the position. All requirements have been met and background checks completed successfully.',
                'assigned_to': 'user2',
                'source': 'working_example'
            },
            {
                'id': 'working_field_8',
                'name': 'Start Date',
                'type': 'date',
                'value': '2024-02-01',
                'assigned_to': 'user1',
                'source': 'working_example'
            }
        ]
    }
]

def get_documents(user_id=None):
    """Get documents from database or mock data, optionally filtered by user"""
    # In production, disable mock data entirely
    is_production = os.getenv('FLASK_ENV') == 'production'
    
    if USE_DATABASE and db:
        try:
            # Query documents from the database
            if user_id:
                documents = Document.query.filter_by(created_by=user_id).all()
            else:
                documents = Document.query.all()
            # Convert to dictionary format for template compatibility
            db_documents = [doc.to_dict() for doc in documents] if documents else []
            
            # In production, only use database documents
            if is_production:
                return db_documents
            
            # In development, combine with mock documents
            # Filter mock documents by user if specified
            if user_id:
                user_mock_documents = [doc for doc in MOCK_DOCUMENTS if doc.get('created_by') == user_id]
            else:
                user_mock_documents = MOCK_DOCUMENTS
            
            # Combine database documents with mock documents
            all_documents = user_mock_documents + db_documents
            return all_documents if all_documents else user_mock_documents
        except Exception as e:
            print(f"Database error in get_documents function")
            print(f"Error details: {e}")
            # Log the error for debugging
            import traceback
            print(f"Stack trace: {traceback.format_exc()}")
            
            # In production, return empty list if database fails
            if is_production:
                return []
            # In development, fallback to mock data
            if user_id:
                return [doc for doc in MOCK_DOCUMENTS if doc.get('created_by') == user_id]
            return MOCK_DOCUMENTS
    
    # In production without database, return empty (should not happen)
    if is_production:
        return []
    
    # Development fallback to mock data
    if user_id:
        return [doc for doc in MOCK_DOCUMENTS if doc.get('created_by') == user_id]
    return MOCK_DOCUMENTS

def get_document_by_id(document_id):
    """Get single document by ID"""
    if USE_DATABASE and db:
        try:
            # Query document from the database
            document = Document.query.filter_by(id=document_id).first()
            return document.to_dict() if document else next((doc for doc in MOCK_DOCUMENTS if doc['id'] == document_id), None)
        except Exception as e:
            print(f"Database error in get_document_by_id function")
            print(f"Error details: {e}")
            # Log the error for debugging
            import traceback
            print(f"Stack trace: {traceback.format_exc()}")
            return next((doc for doc in MOCK_DOCUMENTS if doc['id'] == document_id), None)
    return next((doc for doc in MOCK_DOCUMENTS if doc['id'] == document_id), None)

def check_document_access(document_id, user_id=None):
    """Check if user has access to document (either owns it or is User 2)"""
    document = get_document_by_id(document_id)
    if not document:
        return False, None
    
    # Allow access if:
    # 1. User is the creator (for authenticated users)
    # 2. User is unauthenticated (User 2 access)
    if user_id is None:  # Unauthenticated user (User 2)
        return True, document
    elif document.get('created_by') == user_id:  # Document owner
        return True, document
    else:
        return False, None

def extract_pdf_fields(pdf_path):
    """Enhanced PDF field extraction using PyMuPDF for better accuracy"""
    try:
        print(f"🔍 Analyzing PDF with enhanced processing: {pdf_path}")
        
        # Try PyMuPDF first for better accuracy
        try:
            result = pdf_processor.extract_fields_with_pymupdf(pdf_path)
            
            if "error" not in result and result.get("fields") and len(result["fields"]) > 0:
                print(f"✅ PyMuPDF extraction successful: {len(result['fields'])} fields")
                return result
        except Exception as pymupdf_error:
            print(f"⚠️  PyMuPDF extraction failed: {pymupdf_error}")
        
        # Fallback to legacy extraction if PyMuPDF fails
        print("🔄 Falling back to legacy extraction...")
        try:
            legacy_result = extract_pdf_fields_legacy(pdf_path)
            if "error" not in legacy_result and legacy_result.get("fields") and len(legacy_result["fields"]) > 0:
                print(f"✅ Legacy extraction successful: {len(legacy_result['fields'])} fields")
                return legacy_result
        except Exception as legacy_error:
            print(f"⚠️  Legacy extraction failed: {legacy_error}")
        
        # Final fallback - create intelligent defaults
        print("🔄 Creating intelligent default fields...")
        return create_default_fields()
        
    except Exception as e:
        print(f"❌ Error in enhanced PDF extraction: {e}")
        import traceback
        traceback.print_exc()
        return create_default_fields()

def create_default_fields():
    """Create default fields when extraction fails"""
    default_fields = [
        {'name': 'Full Name', 'type': 'text', 'assigned_to': 'user1'},
        {'name': 'Email Address', 'type': 'email', 'assigned_to': 'user1'},
        {'name': 'Phone Number', 'type': 'tel', 'assigned_to': 'user1'},
        {'name': 'Date', 'type': 'date', 'assigned_to': 'user1'},
        {'name': 'Address', 'type': 'text', 'assigned_to': 'user1'},
        {'name': 'Employee ID', 'type': 'text', 'assigned_to': 'user1'},
        {'name': 'Department', 'type': 'text', 'assigned_to': 'user1'},
        {'name': 'Position/Title', 'type': 'text', 'assigned_to': 'user1'},
        {'name': 'Manager Name', 'type': 'text', 'assigned_to': 'user2'},
        {'name': 'Manager Signature', 'type': 'signature', 'assigned_to': 'user2'},
        {'name': 'HR Approval', 'type': 'text', 'assigned_to': 'user2'},
        {'name': 'Approval Date', 'type': 'date', 'assigned_to': 'user2'},
        {'name': 'Additional Notes', 'type': 'textarea', 'assigned_to': 'user2'},
    ]
    
    fields = []
    for i, field_data in enumerate(default_fields):
        fields.append({
            'id': f'default_{i}',
            'name': field_data['name'],
            'type': field_data['type'],
            'value': '',
            'position': {
                'x': 100 + (i % 2) * 250,
                'y': 700 - (i // 2) * 60,
                'width': 200,
                'height': 30 if field_data['type'] != 'textarea' else 60
            },
            'assigned_to': field_data['assigned_to'],
            'page': 0,
            'source': 'defaults'
        })
    
    return {"fields": fields}

def safe_get_object(obj_ref):
    """Safely get object from reference, handling IndirectObject"""
    try:
        if hasattr(obj_ref, 'get_object'):
            return obj_ref.get_object()
        return obj_ref
    except Exception as e:
        print(f"⚠️  Error getting object: {e}")
        return None

def safe_get_value(obj, key, default=None):
    """Safely get value from PDF object"""
    try:
        if obj is None:
            return default
            
        # Handle IndirectObject
        if hasattr(obj, 'get_object'):
            obj = obj.get_object()
            
        if obj and hasattr(obj, 'get'):
            return obj.get(key, default)
        elif obj and isinstance(obj, dict):
            return obj.get(key, default)
        return default
    except Exception as e:
        print(f"⚠️  Error getting value for key {key}: {e}")
        return default

def safe_check_key(obj, key):
    """Safely check if key exists in PDF object"""
    try:
        if obj is None:
            return False
            
        # Handle IndirectObject
        if hasattr(obj, 'get_object'):
            obj = obj.get_object()
            
        if obj and hasattr(obj, '__contains__'):
            return key in obj
        elif obj and isinstance(obj, dict):
            return key in obj
        return False
    except Exception as e:
        print(f"⚠️  Error checking key {key}: {e}")
        return False

def extract_name_from_annotation_content(annot, page_num: int, index: int) -> str:
    """Extract meaningful name from annotation content"""
    try:
        # Try to get the actual field name from different annotation properties
        field_name = None
        
        # Method 1: Try to get field name from /T (Title/Name)
        field_name = safe_get_value(annot, '/T')
        if field_name:
            clean_name = str(field_name).strip()
            if len(clean_name) > 0 and clean_name != 'None':
                return clean_name.replace(' ', '_').replace(':', '').replace('*', '')
        
        # Method 2: Try to get contents
        contents = safe_get_value(annot, '/Contents')
        if contents and len(str(contents).strip()) > 0:
            content_str = str(contents).strip()
            if len(content_str) < 50 and content_str.replace(' ', '').replace('_', '').isalnum():
                return content_str.replace(' ', '_').replace(':', '').replace('*', '')
        
        # Method 3: Try alternate name field (/TU - User Name)
        alt_name = safe_get_value(annot, '/TU')
        if alt_name:
            clean_name = str(alt_name).strip()
            if len(clean_name) > 0 and clean_name != 'None':
                return clean_name.replace(' ', '_').replace(':', '').replace('*', '')
        
        # Method 4: Check annotation subtype for meaningful naming
        subtype = safe_get_value(annot, '/Subtype')
        if subtype:
            subtype_str = str(subtype).replace('/', '').lower()
            if subtype_str == 'widget':
                # This is a form field, try to create a meaningful name
                rect = safe_get_value(annot, '/Rect', [0, 0, 100, 20])
                if rect and len(rect) >= 4:
                    x, y = int(rect[0]), int(rect[1])
                    # Create name based on position and common field types
                    if y > 600:  # Upper part of page
                        return f"header_field_x{x}_y{y}"
                    elif y < 200:  # Lower part of page
                        return f"footer_field_x{x}_y{y}"
                    else:
                        return f"form_field_x{x}_y{y}"
        
        # Final fallback to position-based naming
        rect = safe_get_value(annot, '/Rect', [0, 0, 100, 20])
        if rect and len(rect) >= 4:
            x, y = int(rect[0]), int(rect[1])
            return f"field_x{x}_y{y}_p{page_num}"
        
        return f"field_{page_num}_{index}"
        
    except Exception as e:
        print(f"⚠️  Error extracting name from annotation: {e}")
        return f"field_{page_num}_{index}"

def extract_pdf_fields_legacy(pdf_path):
    """Legacy PDF field extraction method with comprehensive error handling"""
    fields = []
    
    try:
        print(f"🔍 Legacy analysis: {pdf_path}")
        
        # Check if file exists first
        if not os.path.exists(pdf_path):
            print(f"⚠️  PDF file not found: {pdf_path}")
            return {"fields": []}
        
        # Wrap the entire PDF processing in try-catch
        try:
            # Method 1: Extract actual PDF form fields using PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if pdf_reader.is_encrypted:
                    return {"error": "PDF is encrypted and cannot be processed"}
                
                print(f"📄 PDF has {len(pdf_reader.pages)} pages")
                
                # Method 1: Check for AcroForm fields
                root = safe_get_value(pdf_reader.trailer, '/Root')
                if root and safe_check_key(root, '/AcroForm'):
                    acro_form_ref = safe_get_value(root, '/AcroForm')
                    acro_form = safe_get_object(acro_form_ref)
                    
                    if acro_form:
                        print("✅ Found AcroForm in PDF")
                        
                        if safe_check_key(acro_form, '/Fields'):
                            form_fields_ref = safe_get_value(acro_form, '/Fields')
                            if form_fields_ref:
                                form_fields = safe_get_object(form_fields_ref)
                                
                                if form_fields and hasattr(form_fields, '__len__'):
                                    print(f"📋 Found {len(form_fields)} form fields in AcroForm")
                                    
                                    for i, field_ref in enumerate(form_fields):
                                        try:
                                            # Handle indirect object reference for individual fields
                                            field_obj = safe_get_object(field_ref)
                                            
                                            if not field_obj:
                                                continue
                                            
                                            field_name = safe_get_value(field_obj, '/T', f'acro_field_{i}')
                                            field_type = safe_get_value(field_obj, '/FT', '/Tx')
                                            field_value = safe_get_value(field_obj, '/V', '')
                                            
                                            # Store the original field name for exact matching
                                            original_field_name = str(field_name) if field_name else f'acro_field_{i}'
                                            
                                            print(f"   📋 Processing field: '{original_field_name}' (type: {field_type})")
                                            
                                            # Determine field type more accurately
                                            if field_type == '/Tx':
                                                field_input_type = 'text'
                                            elif field_type == '/Btn':
                                                # Check button flags for checkbox vs radio
                                                flags = safe_get_value(field_obj, '/Ff', 0)
                                                if flags and (flags & 65536):  # Checkbox flag
                                                    field_input_type = 'checkbox'
                                                else:
                                                    field_input_type = 'radio'
                                            elif field_type == '/Ch':
                                                field_input_type = 'select'
                                            elif field_type == '/Sig':
                                                field_input_type = 'signature'
                                            else:
                                                field_input_type = 'text'
                                            
                                            # Get field position
                                            rect = safe_get_value(field_obj, '/Rect')
                                            if rect and len(rect) >= 4:
                                                x, y, width, height = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
                                            else:
                                                x, y, width, height = 100 + (i % 3) * 200, 700 - (i // 3) * 50, 180, 25
                                            
                                            # Get additional field properties
                                            flags = safe_get_value(field_obj, '/Ff', 0) or 0
                                            is_required = (flags & 2) != 0
                                            is_readonly = (flags & 1) != 0
                                            
                                            # Determine likely user assignment based on field name
                                            field_name_lower = original_field_name.lower()
                                            if any(keyword in field_name_lower for keyword in ['signature', 'sign', 'approve', 'manager', 'supervisor', 'hr']):
                                                assigned_to = 'user2'
                                            else:
                                                assigned_to = 'user1'
                                            
                                            field_info = {
                                                'id': f"legacy_{original_field_name}_{i}",  # Use original field name as ID for exact matching
                                                'name': original_field_name,  # Keep original name for display and matching
                                                'type': field_input_type,
                                                'value': str(field_value) if field_value else '',
                                                'position': {'x': float(x), 'y': float(y), 'width': float(width), 'height': float(height)},
                                                'assigned_to': assigned_to,
                                                'page': 0,
                                                'source': 'acroform_legacy',
                                                'pdf_field_name': original_field_name,  # Store for exact matching
                                                'is_required': is_required,
                                                'is_readonly': is_readonly
                                            }
                                            
                                            fields.append(field_info)
                                            print(f"   ✅ Added field: {original_field_name} ({field_input_type}) → {assigned_to}")
                                            
                                        except Exception as field_error:
                                            print(f"   ⚠️  Error processing field {i}: {field_error}")
                                            continue
                            
                # Method 2: Try to extract from page annotations
                for page_num, page in enumerate(pdf_reader.pages):
                    if safe_check_key(page, '/Annots'):
                        annotations_ref = safe_get_value(page, '/Annots')
                        if annotations_ref:
                            annotations = safe_get_object(annotations_ref)
                        
                            if annotations and hasattr(annotations, '__len__'):
                                print(f"📝 Page {page_num + 1}: Found {len(annotations)} annotations")
                                
                                for j, annot_ref in enumerate(annotations):
                                    try:
                                        annot = safe_get_object(annot_ref)
                                        
                                        if not annot:
                                            continue
                                        
                                        subtype = safe_get_value(annot, '/Subtype')
                                        print(f"   📝 Annotation {j}: subtype='{subtype}'")
                                        
                                        if subtype == '/Widget':
                                            # This is a form field annotation
                                            # Try multiple ways to get the field name
                                            annot_name = None
                                            
                                            # Method 1: Direct field name
                                            annot_name = safe_get_value(annot, '/T')
                                            
                                            # Method 2: Try alternate name fields
                                            if not annot_name:
                                                annot_name = safe_get_value(annot, '/TU')  # User name
                                            if not annot_name:
                                                annot_name = safe_get_value(annot, '/TM')  # Mapping name
                                            
                                            # Method 3: Try to extract from appearance or content
                                            if not annot_name:
                                                annot_name = extract_name_from_annotation_content(annot, page_num, j)
                                            
                                            # Method 4: Generate meaningful name based on position and type
                                            if not annot_name:
                                                annot_rect = safe_get_value(annot, '/Rect', [0, 0, 100, 20])
                                                if annot_rect and len(annot_rect) >= 4:
                                                    x, y = int(annot_rect[0]), int(annot_rect[1])
                                                    annot_name = f"field_x{x}_y{y}_p{page_num}"
                                                else:
                                                    annot_name = f"field_{page_num}_{j}"
                                            
                                            annot_rect = safe_get_value(annot, '/Rect', [0, 0, 100, 20])
                                            
                                            if annot_rect and len(annot_rect) >= 4:
                                                field_info = {
                                                    'id': f"annot_{annot_name}_{page_num}_{j}",
                                                    'name': str(annot_name),
                                                    'type': 'text',
                                                    'value': '',
                                                    'position': {
                                                        'x': float(annot_rect[0]),
                                                        'y': float(annot_rect[1]),
                                                        'width': float(annot_rect[2] - annot_rect[0]),
                                                        'height': float(annot_rect[3] - annot_rect[1])
                                                    },
                                                    'assigned_to': 'user1',
                                                    'page': page_num,
                                                    'source': 'annotation_legacy',
                                                    'pdf_field_name': str(annot_name)
                                                }
                                                
                                                fields.append(field_info)
                                                print(f"   📝 Added annotation field: {annot_name}")
                                            
                                    except Exception as annot_error:
                                        print(f"   ⚠️  Error processing annotation {j}: {annot_error}")
                                        continue
                                
                if not fields:
                    print("ℹ️  No form fields found in PDF structure")
                    
        except Exception as pdf_processing_error:
            print(f"❌ Error during PDF processing: {pdf_processing_error}")
            import traceback
            traceback.print_exc()
            return {"fields": []}
        
        print(f"✅ Legacy extraction found {len(fields)} fields")
        for field in fields:
            print(f"   - {field['name']} ({field['type']}) → {field['assigned_to']} [{field['source']}]")
            
    except Exception as e:
        print(f"❌ Error in legacy PDF extraction: {e}")
        import traceback
        traceback.print_exc()
        return {"fields": []}
    
    return {"fields": fields}

def convert_pdf_to_image(pdf_path, page_num=0):
    """Convert PDF page to image for display using PyMuPDF"""
    try:
        return pdf_processor.convert_pdf_to_image(pdf_path, page_num)
    except Exception as e:
        print(f"Error converting PDF to image: {e}")
        return "/static/placeholder-pdf.png"

def generate_completed_pdf(document):
    """Generate a completed PDF with all field values filled"""
    try:
        print(f"🎯 Generating completed PDF for document: {document['name']}")
        print(f"📊 Document has keys: {list(document.keys())}")
        
        # Debug: print document data
        if 'pdf_fields' in document:
            print(f"📋 PDF fields count: {len(document['pdf_fields'])}")
            for field in document['pdf_fields'][:3]:  # Show first 3 fields
                print(f"   - {field.get('name', 'unnamed')}: '{field.get('value', '')}' → {field.get('assigned_to', 'unassigned')}")
        
        if 'user1_data' in document:
            print(f"👤 User 1 data: {list(document['user1_data'].keys())}")
            
        if 'user2_data' in document:
            print(f"👥 User 2 data: {list(document['user2_data'].keys())}")
        
        # Check if we have the original PDF file
        if 'file_path' not in document or not os.path.exists(document['file_path']):
            print("❌ Original PDF file not found, generating summary PDF")
            return generate_summary_pdf(document)
        
        print(f"📄 Original PDF found: {document['file_path']}")
        
        # Create output path
        output_filename = f"completed_{document['id']}_{document['name']}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        print(f"📁 Output path: {output_path}")
        
        # Try Force Visible method first for guaranteed visibility
        print("🔧 Attempting to fill original PDF with FORCE VISIBLE method...")
        if pdf_processor.fill_pdf_with_force_visible(document['file_path'], document, output_path):
            print(f"✅ Successfully filled original PDF with FORCE VISIBLE method: {output_path}")
            return output_path
        
        # Fallback to advanced filling
        print("🔧 Attempting to fill with legacy method...")
        if fill_pdf_fields_advanced(document['file_path'], document, output_path):
            print(f"✅ Successfully filled original PDF: {output_path}")
            return output_path
        
        # Final fallback: create overlay PDF
        print("🔧 Attempting to create overlay PDF...")
        if pdf_processor.create_overlay_pdf(document['file_path'], document.get('pdf_fields', []), output_path):
            print(f"✅ Successfully created overlay PDF: {output_path}")
            return output_path
        else:
            print("⚠️  Could not fill original PDF, generating summary PDF instead")
            return generate_summary_pdf(document)
            
    except Exception as e:
        print(f"❌ Error generating completed PDF: {e}")
        import traceback
        traceback.print_exc()
        print("🔄 Falling back to summary PDF generation...")
        return generate_summary_pdf(document)

# Section 5 Widget Positions - Adjusted 10 right, 10 down
SECTION5_WIDGET_POSITIONS = [
    {"field": "account_holder_name_affidavit", "x": 155, "y": 145, "width": 250, "height": 25},
    {"field": "household_member_names_no_income", "x": 45, "y": 265, "width": 450, "height": 80},
    {"field": "affidavit_signature", "x": 40, "y": 490, "width": 200, "height": 30},
    {"field": "printed_name_affidavit", "x": 315, "y": 490, "width": 230, "height": 25},
    {"field": "date_affidavit", "x": 50, "y": 535, "width": 150, "height": 25},
    {"field": "telephone_affidavit", "x": 315, "y": 535, "width": 150, "height": 25}
]

def fill_section5_with_exact_positions(doc, user2_data):
    """Fill Section 5 fields using exact widget positions that worked perfectly"""
    try:
        import fitz
        
        # Find the Zero Income Affidavit page (usually page 5)
        affidavit_page = None
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text().lower()
            if "zero income affidavit" in text or "income affidavit" in text:
                affidavit_page = page_num
                break
        
        if affidavit_page is None:
            # Default to last page
            affidavit_page = len(doc) - 1
        
        page = doc[affidavit_page]
        
        # Map user2_data to Section 5 fields
        section5_mapping = {
            "account_holder_name_affidavit": user2_data.get("account_holder_name_affidavit", ""),
            "household_member_names_no_income": user2_data.get("household_member_names_no_income", ""),
            "affidavit_signature": user2_data.get("affidavit_signature", ""),
            "printed_name_affidavit": user2_data.get("printed_name_affidavit", ""),
            "date_affidavit": user2_data.get("date_affidavit", ""),
            "telephone_affidavit": user2_data.get("telephone_affidavit", "")
        }
        
        filled_count = 0
        
        # Fill each Section 5 field at exact position
        for pos in SECTION5_WIDGET_POSITIONS:
            field_name = pos["field"]
            field_value = section5_mapping.get(field_name, "")
            
            if field_value:
                x, y, width, height = pos["x"], pos["y"], pos["width"], pos["height"]
                rect = fitz.Rect(x, y, x + width, y + height)
                
                # Determine font size based on field type
                if field_name == "household_member_names_no_income":
                    fontsize = 9  # Smaller for multi-line text
                else:
                    fontsize = 11
                
                # Add the field value at exact position
                text_annot = page.add_freetext_annot(
                    rect,
                    field_value,
                    fontsize=fontsize,
                    fontname="helv",
                    text_color=(0, 0, 0),
                    fill_color=(1, 1, 1),  # White background
                    border_color=(0, 0, 0)
                )
                text_annot.update()
                filled_count += 1
                print(f"✅ Section 5 field positioned: {field_name} = {field_value}")
        
        print(f"📄 Section 5: Filled {filled_count} fields using exact positions on page {affidavit_page + 1}")
        return filled_count > 0
        
    except Exception as e:
        print(f"❌ Error filling Section 5 with exact positions: {e}")
        return False

def fill_pdf_fields_advanced(pdf_path, document, output_path):
    """Advanced PDF field filling with better field matching and Section 5 positioning"""
    try:
        with open(pdf_path, 'rb') as input_file:
            pdf_reader = PyPDF2.PdfReader(input_file)
            pdf_writer = PyPDF2.PdfWriter()
            
            print(f"📄 Processing PDF with {len(pdf_reader.pages)} pages")
            
            # Create a mapping of field names to values from our extracted fields
            field_mapping = {}
            
            # Map PDF field values using the original field names/IDs from extraction
            if 'pdf_fields' in document:
                for field in document['pdf_fields']:
                    if field.get('value'):
                        # Use the original field name from the PDF extraction
                        original_name = field['name']
                        field_id = field.get('id', '')
                        field_value = field['value']
                        pdf_field_name = field.get('pdf_field_name', original_name)
                        
                        # Map using exact field names first (highest priority)
                        field_mapping[pdf_field_name] = field_value
                        field_mapping[original_name] = field_value
                        field_mapping[field_id] = field_value
                        
                        # Also map lowercase versions for fallback
                        field_mapping[pdf_field_name.lower()] = field_value
                        field_mapping[original_name.lower()] = field_value
                        
                        print(f"📝 Mapping field: '{pdf_field_name}' = '{field_value}'")
            
            print(f"📋 Created {len(field_mapping)} field mappings")
            filled_count = 0
            
            # Method 1: Try to fill using AcroForm fields directly
            if '/AcroForm' in pdf_reader.trailer.get('/Root', {}):
                acro_form = pdf_reader.trailer['/Root']['/AcroForm']
                print("✅ Found AcroForm in PDF")
                
                if '/Fields' in acro_form:
                    form_fields = acro_form['/Fields']
                    print(f"📋 Found {len(form_fields)} form fields in AcroForm")
                    
                    for i, field_ref in enumerate(form_fields):
                        try:
                            field_obj = field_ref.get_object()
                            if '/T' in field_obj:
                                field_name = str(field_obj['/T'])
                                print(f"🔍 Processing form field: '{field_name}'")
                                
                                # Look for a matching value in our mapping
                                field_value = None
                                
                                # Try exact match first
                                if field_name in field_mapping:
                                    field_value = field_mapping[field_name]
                                # Try lowercase match
                                elif field_name.lower() in field_mapping:
                                    field_value = field_mapping[field_name.lower()]
                                # Try partial matches
                                else:
                                    for mapped_name, mapped_value in field_mapping.items():
                                        if (mapped_name.lower() in field_name.lower() or 
                                            field_name.lower() in mapped_name.lower()):
                                            field_value = mapped_value
                                            break
                                
                                if field_value:
                                    try:
                                        # Fill the field value
                                        field_obj.update({
                                            PyPDF2.generic.NameObject('/V'): 
                                            PyPDF2.generic.TextStringObject(str(field_value))
                                        })
                                        filled_count += 1
                                        print(f"✅ Filled field '{field_name}' with '{field_value}'")
                                    except Exception as e:
                                        print(f"⚠️  Could not fill field '{field_name}': {e}")
                                else:
                                    print(f"⭕ No value found for field '{field_name}'")
                        except Exception as e:
                            print(f"⚠️  Error processing field {i}: {e}")
            
            # Method 2: Also try annotation-based approach for additional coverage
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                
                if '/Annots' in page:
                    annotations = page['/Annots']
                    for annotation in annotations:
                        try:
                            annotation_obj = annotation.get_object()
                            if '/T' in annotation_obj and '/Subtype' in annotation_obj:
                                subtype = annotation_obj['/Subtype']
                                if subtype == '/Widget':  # Form field widget
                                    field_name = str(annotation_obj['/T'])
                                    
                                    # Skip if we already filled this field
                                    if any(field_name in str(filled) for filled in range(filled_count)):
                                        continue
                                    
                                    # Look for value
                                    field_value = None
                                    if field_name in field_mapping:
                                        field_value = field_mapping[field_name]
                                    elif field_name.lower() in field_mapping:
                                        field_value = field_mapping[field_name.lower()]
                                    
                                    if field_value:
                                        try:
                                            annotation_obj.update({
                                                PyPDF2.generic.NameObject('/V'): 
                                                PyPDF2.generic.TextStringObject(str(field_value))
                                            })
                                            filled_count += 1
                                            print(f"✅ Filled annotation field '{field_name}' with '{field_value}'")
                                        except Exception as e:
                                            print(f"⚠️  Could not fill annotation field '{field_name}': {e}")
                        except Exception as e:
                            continue
                
                pdf_writer.add_page(page)
            
            # Write the filled PDF
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            print(f"✅ Successfully filled {filled_count} fields in original PDF")
            
            # Now add Section 5 fields using exact positions
            try:
                import fitz
                if 'user2_data' in document and document['user2_data']:
                    print("🧾 Adding Section 5 fields with exact positions...")
                    
                    # Open the filled PDF with PyMuPDF for Section 5 positioning
                    fitz_doc = fitz.open(output_path)
                    section5_success = fill_section5_with_exact_positions(fitz_doc, document['user2_data'])
                    
                    if section5_success:
                        # Save the updated PDF with Section 5 fields
                        fitz_doc.save(output_path)
                        print("✅ Section 5 fields added successfully")
                    
                    fitz_doc.close()
            except Exception as e:
                print(f"⚠️  Could not add Section 5 positioning: {e}")
            
            # Only consider it successful if we actually filled some fields
            if filled_count > 0:
                return True
            else:
                print("⚠️  No fields were actually filled in original PDF")
                return False
                
    except Exception as e:
        print(f"❌ Error in fill_pdf_fields_advanced: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_summary_pdf(document):
    """Generate a summary PDF when original PDF filling fails"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        output_filename = f"summary_{document['id']}_{document['name']}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.darkblue,
            spaceAfter=20
        )
        story.append(Paragraph(f"Completed Document: {document['name']}", title_style))
        story.append(Spacer(1, 20))
        
        # Document info
        info_data = [
            ['Document ID:', document['id']],
            ['Status:', document.get('status', 'Completed')],
            ['Completed:', document.get('completed_at', 'Recently')[:10] if document.get('completed_at') else 'Recently']
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # User 1 Information
        if document.get('user1_data'):
            story.append(Paragraph("User 1 Information", styles['Heading2']))
            user1_data = []
            for key, value in document['user1_data'].items():
                if value:
                    user1_data.append([key.replace('_', ' ').title(), str(value)])
            
            if user1_data:
                user1_table = Table(user1_data, colWidths=[2*inch, 4*inch])
                user1_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(user1_table)
                story.append(Spacer(1, 20))
        
        # PDF Fields
        if document.get('pdf_fields'):
            story.append(Paragraph("Completed Form Fields", styles['Heading2']))
            
            # Add header row
            field_data = [['Field Name', 'Value', 'Completed By']]
            
            for field in document['pdf_fields']:
                if field.get('value'):
                    user_label = "User 1" if field['assigned_to'] == 'user1' else "User 2"
                    field_data.append([
                        field['name'],
                        field['value'],
                        user_label
                    ])
            
            if len(field_data) > 1:  # More than just header
                field_table = Table(field_data, colWidths=[2.5*inch, 3*inch, 1*inch])
                field_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                story.append(field_table)
                story.append(Spacer(1, 20))
            else:
                story.append(Paragraph("No field values were provided.", styles['Normal']))
                story.append(Spacer(1, 20))
        
        # User 2 Information
        if document.get('user2_data'):
            story.append(Paragraph("User 2 Information", styles['Heading2']))
            user2_data = []
            for key, value in document['user2_data'].items():
                if value and key != 'signature':
                    user2_data.append([key.replace('_', ' ').title(), str(value)])
            
            if user2_data:
                user2_table = Table(user2_data, colWidths=[2*inch, 4*inch])
                user2_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.orange),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(user2_table)
        
        # Build PDF
        doc.build(story)
        print(f"✅ Generated summary PDF: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error generating summary PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def fill_pdf_fields(pdf_path, field_data, output_path):
    """Legacy PDF field filling function"""
    return fill_pdf_fields_advanced(pdf_path, {'pdf_fields': [], 'user1_data': field_data, 'user2_data': {}}, output_path)

@app.route('/')
def index():
    """Landing page - React app for marketing site"""
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page for authenticated users"""
    documents = get_documents(user_id=current_user.id)
    return render_template('dashboard.html', documents=documents)

@app.route('/start-workflow')
@login_required
def start_workflow():
    """Start new PDF workflow"""
    return redirect(url_for('user1_interface'))

@app.route('/user1', methods=['GET', 'POST'])
@login_required
def user1_interface():
    """User 1 interface - uses homeworks.pdf automatically"""
    if request.method == 'POST':
        # Download homworks.pdf from Supabase instead of local file
        document_id = str(uuid.uuid4())
        filename = 'homworks.pdf'
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_{filename}")
        
        # Try to download from Supabase first
        from supabase_api import get_supabase_api
        supabase_api = get_supabase_api()
        
        pdf_loaded = False
        
        if supabase_api.is_available():
            print("🌐 Attempting to download homworks.pdf from Supabase...")
            pdf_loaded = supabase_api.download_pdf_to_file('homworks.pdf', file_path, 'pdfs')
        
        # Fallback to local file if Supabase fails
        if not pdf_loaded:
            print("📁 Trying local homworks.pdf file...")
            homeworks_pdf_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
            
            if os.path.exists(homeworks_pdf_path):
                # Copy the local homworks.pdf to the uploads directory
                import shutil
                shutil.copy2(homeworks_pdf_path, file_path)
                print("✅ Using local homworks.pdf file")
                pdf_loaded = True
        
        # Final fallback to embedded PDF for deployment
        if not pdf_loaded:
            try:
                print("📦 Using embedded homworks.pdf...")
                from embedded_homworks import save_homworks_pdf_to_file
                save_homworks_pdf_to_file(file_path)
                print("✅ Using embedded homworks.pdf")
                pdf_loaded = True
            except ImportError:
                print("❌ Embedded PDF module not found")
        
        if not pdf_loaded:
            flash('homworks.pdf not found (tried Supabase, local, and embedded)', 'error')
            return redirect(request.url)
        
        # Get form data from User 1 (sections 1-5)
        user1_data = {
            # Section 1: Property Information
            'property_address': request.form.get('property_address', ''),
            'apartment_number': request.form.get('apartment_number', ''),
            'city': request.form.get('city', ''),
            'state': request.form.get('state', ''),
            'zip_code': request.form.get('zip_code', ''),
            'apartments_count': request.form.get('apartments_count', ''),
            'dwelling_type': request.form.get('dwelling_type', ''),
            
            # Section 2: Applicant and Energy Information
            'first_name': request.form.get('first_name', ''),
            'last_name': request.form.get('last_name', ''),
            'telephone': request.form.get('telephone', ''),
            'email': request.form.get('email', ''),
            'heating_fuel': request.form.get('heating_fuel', ''),
            'applicant_type': request.form.get('applicant_type', ''),
            'electric_utility': request.form.get('electric_utility', ''),
            'gas_utility': request.form.get('gas_utility', ''),
            'electric_account': request.form.get('electric_account', ''),
            'gas_account': request.form.get('gas_account', ''),
            
            # Section 3: Qualification Information
            'qualification_option': request.form.get('qualification_option', ''),
            'utility_program': request.form.getlist('utility_program'),
            'documentation': request.form.getlist('documentation'),
            'household_size': request.form.get('household_size', ''),
            'adults_count': request.form.get('adults_count', ''),
            'annual_income': request.form.get('annual_income', ''),
            
            # Section 4: Authorization
            'user2_name': request.form.get('user2_name', ''),  # User 2's name for signature
            'user2_email': request.form.get('user2_email', ''),  # User 2's email for invitations
            'requires_section5': request.form.get('requires_section5', ''),  # Whether User 2 needs Section 5
            'owner_name': request.form.get('owner_name', ''),
            'owner_address': request.form.get('owner_address', ''),
            'owner_telephone': request.form.get('owner_telephone', ''),
            'owner_email': request.form.get('owner_email', '')
            
            # Note: Section 5 (Zero Income Affidavit) fields will be completed by User 2
        }
            
        # Extract PDF fields
        pdf_analysis = extract_pdf_fields(file_path)
        if "error" in pdf_analysis:
            flash(f'Error processing PDF: {pdf_analysis["error"]}', 'error')
            return redirect(request.url)
        
        # Map form data to PDF fields and assign User 1/User 2
        def map_form_data_to_pdf_fields(form_data, pdf_fields):
            """Map the sectioned form data to PDF fields using exact field matching"""
            
            # Explicit field mappings to prevent misplacement
            EXACT_FIELD_MAPPINGS = {
                # Section 1: Property Information
                'property_address': 'Property Address',
                'apartment_number': 'Apartment Number', 
                'city': 'City',
                'state': 'State',
                'zip_code': 'ZIP Code',
                'apartments_count': 'Num Of Apt1',
                
                # Section 2: Applicant Information
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'telephone': 'phone2',  # Use specific phone field for applicant
                'email': 'email2',      # Use specific email field for applicant
                
                # Section 3: Qualification
                'household_size': 'People In Household4',
                'adults_count': 'People In Household Overage4', 
                'annual_income': 'Annual Income4',
                
                # Section 4: Authorization (User 2)
                'applicant_signature': 'signature3',           # Actual signature field name
                'authorization_date': 'date3',                 # Use specific date field for applicant
                
                # Property Owner Info  
                'owner_name': 'Landlord Name3',
                'owner_address': 'Address3', 
                'owner_telephone': 'phone3',                   # Use specific phone field for owner
                'owner_email': 'email3',                       # Use specific email field for owner
                'owner_signature': 'property_ower_sig3',       # Actual property owner signature field
                'owner_signature_date': 'date_property_mang3', # Use specific date field for owner
                
                # Utility accounts
                'electric_account': 'Elec Acct Num2',
                'gas_account': 'Gas Acct Num2',
                
                # Utility company names (commonly missing from mappings)
                'electric_utility': 'Electric Utility2',
                'gas_utility': 'Gas Utility2'
            }
            
            # User assignment rules
            user1_fields = [
                'property_address', 'apartment_number', 'city', 'state', 'zip_code',
                'apartments_count', 'dwelling_type', 'first_name', 'last_name',
                'telephone', 'email', 'heating_fuel', 'applicant_type',
                'electric_utility', 'gas_utility', 'electric_account', 'gas_account',
                'qualification_option', 'household_size', 'adults_count', 'annual_income',
                'owner_name', 'owner_address', 'owner_telephone', 'owner_email'
            ]
            
            user2_section4_fields = [
                'applicant_signature', 'authorization_date', 'owner_signature', 'owner_signature_date'
            ]
            
            user2_section5_fields = [
                'account_holder_name_affidavit', 'household_member_names_no_income', 'affidavit_signature', 
                'printed_name_affidavit', 'date_affidavit', 'telephone_affidavit', 'affidavit_confirmation'
            ]
            
            # Clear all existing assignments
            for field in pdf_fields:
                field['assigned_to'] = None
                field['value'] = ''
            
            # Initialize field matching counter
            matched_fields = 0
            
            # Handle special case: multiple Date fields - use position-based mapping
            date_fields = [f for f in pdf_fields if f['name'] == 'Date']
            date_fields.sort(key=lambda f: f['position']['y'])  # Sort by Y position
            
            # Map authorization_date to Date field near Applicant Signature (y ~471)
            authorization_date_value = form_data.get('authorization_date')
            if authorization_date_value:
                for field in date_fields:
                    if 460 <= field['position']['y'] <= 480:  # Authorization area
                        field['value'] = str(authorization_date_value)
                        field['assigned_to'] = 'user2'
                        print(f"   ✅ Position-based match: authorization_date → Date field at ({field['position']['x']:.0f}, {field['position']['y']:.0f})")
                        matched_fields += 1
                        break
            
            # Map owner_signature_date to Date field near Property Owner Signature (y ~643)
            owner_date_value = form_data.get('owner_signature_date')
            if owner_date_value:
                for field in date_fields:
                    if field['position']['y'] > 630:  # Property owner area
                        field['value'] = str(owner_date_value)
                        field['assigned_to'] = 'user2'
                        print(f"   ✅ Position-based match: owner_signature_date → Date field at ({field['position']['x']:.0f}, {field['position']['y']:.0f})")
                        matched_fields += 1
                        break
            
            # DEBUG: Show all form data received
            print(f"\n🔍 DEBUG: Form data received ({len(form_data)} fields):")
            for key, value in form_data.items():
                print(f"   📝 {key}: {value}")
            
            # DEBUG: Show all PDF field names extracted
            print(f"\n🔍 DEBUG: PDF field names extracted ({len(pdf_fields)} fields):")
            for field in pdf_fields[:10]:  # Show first 10
                print(f"   📄 {field['name']} (type: {field.get('type', 'unknown')})")
            if len(pdf_fields) > 10:
                print(f"   ... and {len(pdf_fields) - 10} more fields")
            
            # DEBUG: Show mapping dictionary keys
            print(f"\n🔍 DEBUG: EXACT_FIELD_MAPPINGS keys ({len(EXACT_FIELD_MAPPINGS)} mappings):")
            for key in list(EXACT_FIELD_MAPPINGS.keys())[:10]:
                print(f"   🗝️  {key} → {EXACT_FIELD_MAPPINGS[key]}")
            if len(EXACT_FIELD_MAPPINGS) > 10:
                print(f"   ... and {len(EXACT_FIELD_MAPPINGS) - 10} more mappings")
            
            # Map form data to PDF fields using exact matching (excluding Date fields which are handled above)
            print(f"\n🔍 DEBUG: Starting field mapping process...")
            mapping_attempts = 0
            successful_mappings = 0
            
            for form_field, form_value in form_data.items():
                if not form_value:
                    print(f"   ⭕ Skipping empty field: {form_field}")
                    continue
                
                # Skip Date fields as they're handled above with position-based logic
                if form_field in ['authorization_date', 'owner_signature_date']:
                    print(f"   ⏭️  Skipping date field: {form_field}")
                    continue
                
                mapping_attempts += 1
                    
                # Get the exact PDF field name
                pdf_field_name = EXACT_FIELD_MAPPINGS.get(form_field)
                
                if not pdf_field_name:
                    print(f"   ❌ No mapping found for form field: {form_field}")
                    continue
                
                print(f"   🔍 Mapping {form_field} → {pdf_field_name}")
                
                if pdf_field_name:
                    # Find the PDF field with exact name match
                    field_found = False
                    for field in pdf_fields:
                        if field['name'] == pdf_field_name:
                            field['value'] = str(form_value)
                            
                            # Assign to correct user
                            if form_field in user1_fields:
                                field['assigned_to'] = 'user1'
                            elif form_field in user2_section4_fields or form_field in user2_section5_fields:
                                field['assigned_to'] = 'user2'
                                if 'signature' in form_field:
                                    field['type'] = 'signature'
                            else:
                                field['assigned_to'] = 'user1'  # Default to user1
                            
                            # CRITICAL: Set pdf_field_name for PDFProcessor to find the field
                            field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                            
                            print(f"   ✅ Exact match: {form_field} → {pdf_field_name} (value: {form_value})")
                            matched_fields += 1
                            field_found = True
                            break
                    
                    if not field_found:
                        print(f"   ⚠️  PDF field not found for: {form_field} → {pdf_field_name}")
                    else:
                        successful_mappings += 1
                        
            print(f"\n📊 DEBUG: Field mapping summary:")
            print(f"   🔢 Total form fields with values: {mapping_attempts}")
            print(f"   ✅ Successful mappings: {successful_mappings}")
            print(f"   ❌ Failed mappings: {mapping_attempts - successful_mappings}")
            
            # Handle special cases (radio buttons, checkboxes with specific values)
            print(f"\n🔍 DEBUG: Handling special cases...")
            special_case_matches = 0
            
            for form_field, form_value in form_data.items():
                if not form_value:
                    continue
                    
                # Skip fields already handled
                if EXACT_FIELD_MAPPINGS.get(form_field):
                    continue
                    
                matched = False
                
                # Handle dwelling type
                if form_field == 'dwelling_type':
                    dwelling_mappings = {
                        'single_family': 'Single Family Home (Checkbox)',
                        'apartment': 'Apartment (Checkbox)', 
                        'condominium': 'Condominium (Checkbox)'
                    }
                    target_field = dwelling_mappings.get(form_value)
                    if target_field:
                        for field in pdf_fields:
                            if field['name'] == target_field:
                                field['value'] = 'true'
                                field['assigned_to'] = 'user1'
                                field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                                matched = True
                                special_case_matches += 1
                                print(f"   ✅ Dwelling type: {form_value} → {target_field}")
                                break
                
                # Handle heating fuel
                elif form_field == 'heating_fuel':
                    fuel_mappings = {
                        'electric': 'Electric Heat (Radio Button)',
                        'natural_gas': 'Gas Heat (Radio Button)',
                        'oil': 'Oil Heat (Radio Button)', 
                        'propane': 'Propane Heat (Radio Button)'
                    }
                    target_field = fuel_mappings.get(form_value)
                    if target_field:
                        for field in pdf_fields:
                            if field['name'] == target_field:
                                field['value'] = 'true'
                                field['assigned_to'] = 'user1'
                                field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                                matched = True
                                special_case_matches += 1
                                print(f"   ✅ Heating fuel: {form_value} → {target_field}")
                                break
                
                # Handle applicant type
                elif form_field == 'applicant_type':
                    type_mappings = {
                        'property_owner': 'Property Owner (Radio Button)',
                        'renter_tenant': 'Renter (Radio Button)'
                    }
                    target_field = type_mappings.get(form_value)
                    if target_field:
                        for field in pdf_fields:
                            if field['name'] == target_field:
                                field['value'] = 'true'
                                field['assigned_to'] = 'user1'
                                field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                                matched = True
                                special_case_matches += 1
                                print(f"   ✅ Applicant type: {form_value} → {target_field}")
                                break
                
                if not matched:
                    print(f"   ❓ Unmatched form field: {form_field} = {form_value}")
            
            # Handle qualification option checkboxes (Options A, B, C, D)
            print(f"\n🔍 DEBUG: Handling qualification checkboxes...")
            
            # Option A: Utility programs
            utility_programs = form_data.get('utility_program', [])
            if utility_programs:
                print(f"   📋 Option A - Utility programs selected: {utility_programs}")
                program_mappings = {
                    'electric_discount': 'Elec Discount4 (Checkbox)',
                    'matching_payment': 'Matching Payment Eversource4 (Checkbox)',  
                    'low_income_discount': 'Low Income Program (Checkbox)',
                    'bill_forgiveness': 'Bill Forgiveness Program (Checkbox)',
                    'matching_payment_united': 'Matching Pay United4 (Checkbox)'
                }
                
                for program in utility_programs:
                    target_field = program_mappings.get(program)
                    if target_field:
                        for field in pdf_fields:
                            if field['name'] == target_field:
                                field['value'] = 'true'
                                field['assigned_to'] = 'user1'
                                field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                                special_case_matches += 1
                                print(f"   ✅ Utility program: {program} → {target_field}")
                                break
            
            # Option B: Documentation
            documentation = form_data.get('documentation', [])
            if documentation:
                print(f"   📋 Option B - Documentation selected: {documentation}")
                doc_mappings = {
                    'ebt_award': 'EBT (Food Stamps) (Checkbox)',
                    'energy_assistance': 'Energy Award Letter4 (Checkbox)',
                    'section_8': 'Section Eight4 (Checkbox)'
                }
                
                for doc in documentation:
                    target_field = doc_mappings.get(doc)
                    if target_field:
                        for field in pdf_fields:
                            if field['name'] == target_field:
                                field['value'] = 'true'
                                field['assigned_to'] = 'user1'
                                field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                                special_case_matches += 1
                                print(f"   ✅ Documentation: {doc} → {target_field}")
                                break
            
            # Option D: Multifamily
            if form_data.get('qualification_option') == 'option_d':
                print(f"   📋 Option D - Multifamily selected")
                for field in pdf_fields:
                    if field['name'] == 'Multifam4 (Checkbox)':
                        field['value'] = 'true'
                        field['assigned_to'] = 'user1'
                        field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                        special_case_matches += 1
                        print(f"   ✅ Multifamily option selected")
                        break
            
            # Ensure all unassigned fields go to user1
            for field in pdf_fields:
                if field.get('assigned_to') is None:
                    field['assigned_to'] = 'user1'
            
            total_mappings = successful_mappings + special_case_matches
            print(f"📊 FINAL Field mapping summary:")
            print(f"   ✅ Exact mappings: {successful_mappings}")
            print(f"   🔧 Special case mappings: {special_case_matches}")
            print(f"   📊 Total successful mappings: {total_mappings}")
            print(f"   ❌ Total failed mappings: {mapping_attempts - successful_mappings}")
            
            if total_mappings == 0:
                print(f"   🚨 CRITICAL: NO FIELDS WERE MAPPED! This will cause download issues.")
                print(f"   💡 Check that form field names match EXACT_FIELD_MAPPINGS keys")
                print(f"   💡 Check that PDF field names match EXACT_FIELD_MAPPINGS values")
            return pdf_fields
        
        # Apply the field mapping
        pdf_analysis['fields'] = map_form_data_to_pdf_fields(user1_data, pdf_analysis['fields'])
        
        # Process PDF fields data from User 1 (for any manual overrides)
        pdf_fields_data = request.form.get('pdf_fields')
        print(f"📋 PDF fields data received: {pdf_fields_data is not None}")
        
        if pdf_fields_data:
            try:
                # Parse the PDF fields JSON data from frontend
                frontend_fields = json.loads(pdf_fields_data)
                print(f"📊 Parsed {len(frontend_fields)} fields from frontend")
                
                # Debug: Show what we received
                for i, field in enumerate(frontend_fields[:3]):  # Show first 3
                    print(f"   Frontend field {i+1}: {field.get('name', 'unnamed')} = '{field.get('value', '')}' → {field.get('assigned_to', 'unassigned')}")
                
                # Update the extracted fields with User 1's assignments and values
                for frontend_field in frontend_fields:
                    # Find corresponding field in extracted fields
                    for extracted_field in pdf_analysis['fields']:
                        if extracted_field['id'] == frontend_field['id']:
                            # Update assignment and value
                            extracted_field['assigned_to'] = frontend_field.get('assigned_to', extracted_field['assigned_to'])
                            extracted_field['value'] = frontend_field.get('value', '')
                            if frontend_field.get('value'):
                                print(f"✅ User 1 filled '{extracted_field['name']}': '{frontend_field['value']}'")
                            break
                    else:
                        # This is a custom field added by User 1
                        pdf_analysis['fields'].append(frontend_field)
                        if frontend_field.get('value'):
                            print(f"✅ User 1 added custom field '{frontend_field['name']}': '{frontend_field['value']}'")
                
                print(f"📊 Final field summary:")
                for field in pdf_analysis['fields']:
                    if field.get('value'):
                        print(f"   ✅ {field['name']}: '{field['value']}' → {field['assigned_to']}")
                    else:
                        print(f"   ⭕ {field['name']}: (empty) → {field['assigned_to']}")
                        
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing PDF fields JSON: {e}")
        else:
            print("⚠️  No PDF fields data received from User 1")
        
        # Add to mock data
        new_document = {
            'id': document_id,
            'name': filename,
            'status': 'Pending User 2',
            'lastUpdated': 'Just now',
            'created_at': datetime.now().isoformat(),
            'created_by': current_user.id if current_user.is_authenticated else None,
            'user1_data': user1_data,
            'file_path': file_path,
            'pdf_fields': pdf_analysis['fields'],
            'field_assignments': {field['id']: field['assigned_to'] for field in pdf_analysis['fields']}
        }
        
        print(f"📄 Adding new document to MOCK_DOCUMENTS:")
        print(f"   📋 Document ID: {document_id}")
        print(f"   📋 Document name: {filename}")
        print(f"   📋 PDF fields count: {len(pdf_analysis['fields'])}")
        
        # Show field values being saved
        fields_with_values = [f for f in pdf_analysis['fields'] if f.get('value')]
        fields_without_values = [f for f in pdf_analysis['fields'] if not f.get('value')]
        
        print(f"   ✅ Fields with values: {len(fields_with_values)}")
        for field in fields_with_values:
            print(f"      - {field['name']}: '{field['value']}' → {field['assigned_to']}")
        
        print(f"   ⭕ Fields without values: {len(fields_without_values)}")
        for field in fields_without_values:
            print(f"      - {field['name']}: (empty) → {field['assigned_to']}")
        
        MOCK_DOCUMENTS.append(new_document)
        
        # Send invitation email to User 2 immediately
        user2_email = user1_data.get('user2_email')
        if user2_email and is_email_configured():
            try:
                # Generate invitation URL
                invitation_url = url_for('user2_interface', document_id=document_id, _external=True)
                
                # Send invitation email
                success = send_document_invitation_email(
                    document_data=new_document,
                    recipient_email=user2_email,
                    sender_name=user1_data.get('user2_name', 'User 1'),
                    invitation_url=invitation_url
                )
                
                if success:
                    # Update document to mark invitation as sent
                    new_document['invitation_sent'] = True
                    new_document['invitation_sent_at'] = datetime.now().isoformat()
                    flash(f'Application completed and invitation sent to {user2_email}!', 'success')
                else:
                    flash('Application completed but failed to send invitation email.', 'warning')
                    
            except Exception as e:
                print(f"Error sending invitation email: {e}")
                flash('Application completed but failed to send invitation email.', 'warning')
        else:
            if not user2_email:
                flash('Application completed but no email address provided for User 2.', 'warning')
            else:
                flash('Application completed but email service not configured.', 'warning')
            
            return redirect(url_for('dashboard'))
    
    # For GET request, load homworks.pdf and extract fields for form display
    # Try to download from Supabase first
    from supabase_api import get_supabase_api
    supabase_api = get_supabase_api()
    
    temp_pdf_path = None
    pdf_loaded = False
    
    if supabase_api.is_available():
        print("🌐 Attempting to download homworks.pdf from Supabase for form display...")
        # Create a temporary file for PDF analysis
        import tempfile
        temp_pdf_path = tempfile.mktemp(suffix='.pdf')
        pdf_loaded = supabase_api.download_pdf_to_file('homworks.pdf', temp_pdf_path, 'pdfs')
    
    # Fallback to local file if Supabase fails
    if not pdf_loaded:
        print("📁 Falling back to local homworks.pdf file for form display...")
        homeworks_pdf_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        
        if os.path.exists(homeworks_pdf_path):
            temp_pdf_path = homeworks_pdf_path
            print("✅ Using local homworks.pdf file for form display")
            pdf_loaded = True
    
    # Final fallback to embedded PDF for deployment
    if not pdf_loaded:
        try:
            print("📦 Using embedded homworks.pdf for form display...")
            from embedded_homworks import save_homworks_pdf_to_file
            import tempfile
            # Create a temporary file for the embedded PDF
            temp_pdf_path = tempfile.mktemp(suffix='.pdf')
            save_homworks_pdf_to_file(temp_pdf_path)
            print("✅ Using embedded homworks.pdf for form display")
            pdf_loaded = True
        except ImportError:
            print("❌ Embedded PDF module not found")
    
    if not pdf_loaded:
        flash('homworks.pdf not found (tried Supabase, local, and embedded)', 'error')
        return redirect(url_for('dashboard'))
    
    # Extract PDF fields for form structure
    pdf_analysis = extract_pdf_fields(temp_pdf_path)
    if "error" in pdf_analysis:
        flash(f'Error processing PDF: {pdf_analysis["error"]}', 'error')
        return redirect(url_for('dashboard'))
    
    # Clean up temporary file if we created one
    # Check if it's a temporary file (not the local homeworks.pdf)
    is_temp_file = pdf_loaded and temp_pdf_path and (
        'homeworks_pdf_path' not in locals() or temp_pdf_path != locals().get('homeworks_pdf_path')
    )
    if is_temp_file:
        try:
            os.remove(temp_pdf_path)
        except:
            pass  # Ignore cleanup errors
    
    return render_template('user1_enhanced.html', pdf_fields=pdf_analysis.get('fields', []))

@app.route('/send-invitation/<document_id>', methods=['POST'])
@login_required
def send_invitation(document_id):
    """Send email invitation to User 2 to complete document"""
    has_access, document = check_document_access(document_id, current_user.id)
    
    if not has_access:
        flash('Document not found or access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if user is the document owner
    if document.get('status') == 'Signed & Sent':
        flash('This document has already been completed.', 'info')
        return redirect(url_for('dashboard'))
    
    # Get the User 2 email from the document
    user2_email = document.get('user1_data', {}).get('user2_email')
    if not user2_email:
        flash('No recipient email address found. Please check the document configuration.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if email is configured
    if not is_email_configured():
        flash('Email service is not configured. Cannot send invitation.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Get sender information
        sender_name = document.get('user1_data', {}).get('name', 'PDFCollab User')
        
        # Generate invitation URL
        invitation_url = url_for('user2_interface', document_id=document_id, _external=True)
        
        # Send invitation email
        success = send_document_invitation_email(
            document_data=document,
            recipient_email=user2_email,
            sender_name=sender_name,
            invitation_url=invitation_url
        )
        
        if success:
            flash(f'Invitation email sent successfully to {user2_email}!', 'success')
            
            # Update document to mark invitation as sent
            for doc in MOCK_DOCUMENTS:
                if doc['id'] == document_id:
                    doc['invitation_sent'] = True
                    doc['invitation_sent_at'] = datetime.now().isoformat()
                    break
        else:
            flash(f'Failed to send invitation email to {user2_email}. Please try again.', 'error')
            
    except Exception as e:
        app.logger.error(f"Failed to send invitation: {e}")
        flash('Failed to send invitation email. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/user2/<document_id>', methods=['GET', 'POST'])
def user2_interface(document_id):
    """User 2 interface - handles Section 4 (Authorization) always, Section 5 conditionally"""
    user_id = current_user.id if current_user.is_authenticated else None
    has_access, document = check_document_access(document_id, user_id)
    
    if not has_access:
        # For unauthenticated users (User 2), show a simple error page instead of redirecting to dashboard
        if not current_user.is_authenticated:
            return render_template('error.html', 
                                 error_title='Document Not Found',
                                 error_message='The requested document could not be found or may have been removed.')
        flash('Document not found or access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if Section 5 is required based on User 1's selection
    requires_section5 = document.get('user1_data', {}).get('requires_section5') == 'yes'
    
    if request.method == 'POST':
        # Get User 2's contact information
        user2_data = {
            'name': request.form.get('user2_name', ''),
            'email': request.form.get('user2_email', ''),
            'date_signed': datetime.now().isoformat()
        }
        
        print(f"👤 User 2 contact info: name='{user2_data['name']}', email='{user2_data['email']}'")
        
        # Collect Section 4 (Authorization) fields - ALWAYS required for User 2
        section4_fields = {
            'applicant_signature': request.form.get('applicant_signature', ''),
            'authorization_date': request.form.get('authorization_date', ''),
            'owner_signature': request.form.get('owner_signature', ''),
            'owner_signature_date': request.form.get('owner_signature_date', '')
        }
        
        # Add Section 4 fields to user2_data
        for key, value in section4_fields.items():
            if value:
                user2_data[key] = value
                print(f"✅ Section 4 field '{key}': '{value}'")
            else:
                print(f"⭕ Section 4 field '{key}': empty")
        
        # Collect Section 5 (Zero Income Affidavit) fields - ONLY if required
        if requires_section5:
            section5_fields = {
                'account_holder_name_affidavit': request.form.get('account_holder_name_affidavit', ''),
                'household_member_names_no_income': request.form.get('household_member_names_no_income', ''),
                'affidavit_signature': request.form.get('affidavit_signature', ''),
                'printed_name_affidavit': request.form.get('printed_name_affidavit', ''),
                'date_affidavit': request.form.get('date_affidavit', ''),
                'telephone_affidavit': request.form.get('telephone_affidavit', ''),
                'affidavit_confirmation': request.form.get('affidavit_confirmation', '')
            }
            
            # Add Section 5 fields to user2_data
            for key, value in section5_fields.items():
                if value:
                    user2_data[key] = value
                    print(f"✅ Section 5 field '{key}': '{value}'")
                else:
                    print(f"⭕ Section 5 field '{key}': empty")
        else:
            print("ℹ️ Section 5 not required for this document")
        
        # Process User 2's PDF field values
        print(f"👥 Processing User 2 form for document: {document_id}")
        print(f"📊 Document has pdf_fields: {'pdf_fields' in document}")
        
        if 'pdf_fields' in document:
            print(f"📋 Found {len(document['pdf_fields'])} PDF fields in document")
            
            # FIRST: Fix signature fields that may be incorrectly assigned to user1
            signature_fields_fixed = 0
            for field in document['pdf_fields']:
                field_name = field.get('name', '')
                # Check if this is a signature field that should belong to user2
                if (('Applicant Signature' in field_name or 'Property Owner Signature' in field_name or 
                     field_name in ['signature3', 'property_ower_sig3']) and 
                    field.get('assigned_to') == 'user1'):
                    field['assigned_to'] = 'user2'
                    field['type'] = 'signature'
                    signature_fields_fixed += 1
                    print(f"🔧 Fixed assignment: '{field_name}' reassigned from user1 to user2")
            
            if signature_fields_fixed > 0:
                print(f"✅ Fixed {signature_fields_fixed} signature fields that were incorrectly assigned to user1")
            
            user2_fields = [f for f in document['pdf_fields'] if f['assigned_to'] == 'user2']
            print(f"📝 User 2 is assigned {len(user2_fields)} fields:")
            
            for field in user2_fields:
                print(f"   - {field['name']} ({field['id']}) → looking for form field 'field_{field['id']}'")
            
            for field in document['pdf_fields']:
                if field['assigned_to'] == 'user2':
                    # Get the field value from the form
                    field_value = request.form.get(f"field_{field['id']}", '')
                    print(f"🔍 Field '{field['name']}' ({field['id']}): form value = '{field_value}'")
                    
                    if field_value:
                        field['value'] = field_value
                        print(f"✅ User 2 filled field '{field['name']}': '{field_value}'")
                    else:
                        print(f"⭕ User 2 left field '{field['name']}' empty")
                        
                    # Special handling for signature fields - map to correct signature type
                    if field.get('type') == 'signature' or 'Signature' in field.get('name', ''):
                        field_name = field.get('name', '')
                        field['type'] = 'signature'  # Ensure type is set
                        # CRITICAL: Ensure pdf_field_name is set for PDF processor to find the field
                        if field_name == 'Applicant Signature' or 'Applicant' in field_name:
                            field['pdf_field_name'] = 'signature3'
                        elif field_name == 'Property Owner Signature' or 'Property Owner' in field_name:
                            field['pdf_field_name'] = 'property_ower_sig3'
                        else:
                            field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                        
                        field['assigned_to'] = 'user2'
                        
                        # Map Applicant Signature field
                        if ('Applicant' in field_name or field['pdf_field_name'] == 'signature3') and user2_data.get('applicant_signature'):
                            field['value'] = user2_data['applicant_signature']
                            print(f"🖋️  Applied Applicant signature to field '{field['name']}' (pdf_field: '{field['pdf_field_name']}'): '{user2_data['applicant_signature'][:20]}...'")
                        
                        # Map Property Owner Signature field  
                        elif ('Property Owner' in field_name or field['pdf_field_name'] == 'property_ower_sig3') and user2_data.get('owner_signature'):
                            field['value'] = user2_data['owner_signature']
                            print(f"🖋️  Applied Property Owner signature to field '{field['name']}' (pdf_field: '{field['pdf_field_name']}'): '{user2_data['owner_signature'][:20]}...'")
                        
                        else:
                            print(f"⚠️  Signature field '{field_name}' found but no matching signature data")
        else:
            print("❌ No pdf_fields found in document")
        
        # Also capture any legacy field names for backwards compatibility
        legacy_fields = {
            'manager': request.form.get('manager', ''),
            'hr_rep': request.form.get('hr_rep', ''),
            'benefits': request.form.get('benefits', ''),
            'notes': request.form.get('notes', ''),
            'manager_name': request.form.get('manager_name', ''),
            'hr_approval': request.form.get('hr_approval', ''),
            'approval_date': request.form.get('approval_date', ''),
            'hr_notes': request.form.get('hr_notes', '')
        }
        
        # Add non-empty legacy fields to user2_data
        for key, value in legacy_fields.items():
            if value:
                user2_data[key] = value
        
        # Handle supporting documents
        supporting_docs = []
        if 'supporting_docs' in request.files:
            for file in request.files.getlist('supporting_docs'):
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    support_path = os.path.join(app.config['UPLOAD_FOLDER'], f"support_{document_id}_{filename}")
                    file.save(support_path)
                    supporting_docs.append({'filename': filename, 'path': support_path})
        
        # Update document - CRITICAL: Save the updated pdf_fields too!
        updated_document = None
        for doc in MOCK_DOCUMENTS:
            if doc['id'] == document_id:
                doc.update({
                    'status': 'Signed & Sent',
                    'user2_data': user2_data,
                    'supporting_docs': supporting_docs,
                    'completed_at': datetime.now().isoformat(),
                    'lastUpdated': 'Just now',
                    'pdf_fields': document.get('pdf_fields', [])  # Save updated pdf_fields with signature data
                })
                updated_document = doc
                break
        
        # Send email notifications if document was updated
        if updated_document and is_email_configured():
            try:
                # Get email addresses from the document data
                user1_email = updated_document.get('user1_data', {}).get('email')
                user2_email = user2_data.get('email')
                
                # Debug logging
                app.logger.info(f"Email sending debug - User1 email: {user1_email}, User2 email: {user2_email}")
                print(f"🐛 DEBUG: User1 email: {user1_email}, User2 email: {user2_email}")
                
                email_sent = False
                
                # Send email to user1 (document owner)
                if user1_email:
                    success1 = send_document_completion_email(updated_document, user1_email)
                    if success1:
                        flash(f'Email notification sent to {user1_email}', 'success')
                        email_sent = True
                    else:
                        flash(f'Failed to send email to {user1_email}', 'error')
                else:
                    flash('No email address found for document owner', 'warning')
                
                # Send email to user2 (signer)
                if user2_email:
                    success2 = send_document_completion_email(updated_document, user2_email)
                    if success2:
                        flash(f'Email notification sent to {user2_email}', 'success')
                        email_sent = True
                    else:
                        flash(f'Failed to send email to {user2_email}', 'error')
                else:
                    flash('No email address found for document signer', 'warning')
                
                if not email_sent:
                    flash('No emails were sent - no valid email addresses found', 'warning')
                    
            except Exception as e:
                app.logger.error(f"Failed to send email notifications: {e}")
                flash('Document completed successfully, but email notifications failed to send.', 'warning')
        elif not is_email_configured():
            flash('Document completed successfully. Email notifications are not configured.', 'info')
        else:
            flash('Document completed successfully. No email configuration found.', 'info')
        
        return redirect(url_for('completion_page', document_id=document_id))
    
    return render_template('user2_enhanced.html', 
                         document=document, 
                         requires_section5=requires_section5)

@app.route('/complete/<document_id>')
def completion_page(document_id):
    """Completion page - matches your React CompletionPage component"""
    user_id = current_user.id if current_user.is_authenticated else None
    has_access, document = check_document_access(document_id, user_id)
    
    if not has_access:
        # For unauthenticated users (User 2), show a simple error page instead of redirecting to dashboard
        if not current_user.is_authenticated:
            return render_template('error.html', 
                                 error_title='Document Not Found',
                                 error_message='The requested document could not be found or may have been removed.')
        flash('Document not found or access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('completion.html', document=document)

@app.route('/download/<document_id>')
def download_document(document_id):
    """Download completed PDF document"""
    print(f"🔽 Download request for document: {document_id}")
    
    user_id = current_user.id if current_user.is_authenticated else None
    has_access, document = check_document_access(document_id, user_id)
    
    if not has_access:
        print(f"❌ Document not found or access denied: {document_id}")
        if not current_user.is_authenticated:
            return render_template('error.html', 
                                 error_title='Document Not Found',
                                 error_message='The requested document could not be found or may have been removed.')
        flash('Document not found or access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    print(f"📋 Document found: {document.get('name', 'unknown')}")
    print(f"📊 Document data keys: {list(document.keys())}")
    
    # Debug: Show field values at download time
    if 'pdf_fields' in document:
        fields_with_values = [f for f in document['pdf_fields'] if f.get('value')]
        fields_without_values = [f for f in document['pdf_fields'] if not f.get('value')]
        
        print(f"📋 At download time - Fields with values: {len(fields_with_values)}")
        for field in fields_with_values:
            print(f"   ✅ {field['name']}: '{field['value']}' → {field['assigned_to']}")
        
        print(f"📋 At download time - Fields without values: {len(fields_without_values)}")
        for field in fields_without_values:
            print(f"   ⭕ {field['name']}: (empty) → {field['assigned_to']}")
    else:
        print("❌ No pdf_fields in document at download time")
    
    try:
        # Generate the completed PDF
        print("🎯 Starting PDF generation...")
        output_path = generate_completed_pdf(document)
        
        if output_path and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ PDF generated successfully: {output_path} ({file_size} bytes)")
            
            # Validate PDF before sending
            try:
                with open(output_path, 'rb') as f:
                    header = f.read(10)
                    if not header.startswith(b'%PDF'):
                        print(f"❌ Invalid PDF header: {header}")
                        flash('Generated PDF appears to be corrupted. Please try again.', 'error')
                        return redirect(url_for('completion_page', document_id=document_id))
                    
                    # Check if file is readable and has content
                    f.seek(0, 2)  # Go to end of file
                    actual_size = f.tell()
                    print(f"📄 PDF validation: Header OK, actual file size: {actual_size} bytes")
                    
                    if actual_size == 0:
                        print("❌ PDF file is empty!")
                        flash('Generated PDF is empty. Please try again.', 'error')
                        return redirect(url_for('completion_page', document_id=document_id))
                        
            except Exception as e:
                print(f"❌ Error validating PDF: {e}")
                flash('Error validating generated PDF. Please try again.', 'error')
                return redirect(url_for('completion_page', document_id=document_id))
            
            print("📤 Sending PDF file for download...")
            
            # Return the file for download with improved headers
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f"completed_{document['name']}",
                mimetype='application/pdf'
            )
        else:
            print("❌ PDF generation failed - no output file")
            flash('Error generating PDF. Please try again.', 'error')
            return redirect(url_for('completion_page', document_id=document_id))
            
    except Exception as e:
        print(f"❌ Error in download_document: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error generating PDF download: {str(e)}', 'error')
        return redirect(url_for('completion_page', document_id=document_id))

@app.route('/api/pdf-fields/<document_id>')
def get_pdf_fields(document_id):
    """API endpoint to get PDF fields for a document"""
    document = get_document_by_id(document_id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    if 'pdf_fields' in document:
        return jsonify({
            'fields': document['pdf_fields'],
            'assignments': document.get('field_assignments', {})
        })
    
    # If no fields extracted yet, try to extract them
    if 'file_path' in document:
        pdf_analysis = extract_pdf_fields(document['file_path'])
        if 'error' in pdf_analysis:
            return jsonify({'error': pdf_analysis['error']}), 500
        
        # Update document with fields
        document['pdf_fields'] = pdf_analysis['fields']
        document['field_assignments'] = {field['id']: field['assigned_to'] for field in pdf_analysis['fields']}
        
        return jsonify({
            'fields': document['pdf_fields'],
            'assignments': document['field_assignments']
        })
    
    return jsonify({'error': 'No PDF file found'}), 404

@app.route('/api/assign-field/<document_id>', methods=['POST'])
def assign_field(document_id):
    """API endpoint to assign a field to a user"""
    document = get_document_by_id(document_id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    field_id = data.get('field_id')
    assigned_to = data.get('assigned_to')
    
    if not field_id or not assigned_to:
        return jsonify({'error': 'Missing field_id or assigned_to'}), 400
    
    if assigned_to not in ['user1', 'user2']:
        return jsonify({'error': 'Invalid assigned_to value'}), 400
    
    # Update field assignment
    if 'field_assignments' not in document:
        document['field_assignments'] = {}
    
    document['field_assignments'][field_id] = assigned_to
    
    # Also update the field in pdf_fields if it exists
    if 'pdf_fields' in document:
        for field in document['pdf_fields']:
            if field['id'] == field_id:
                field['assigned_to'] = assigned_to
                break
    
    return jsonify({'success': True, 'field_id': field_id, 'assigned_to': assigned_to})

@app.route('/api/update-field/<document_id>', methods=['POST'])
def update_field_value(document_id):
    """API endpoint to update a field value"""
    document = get_document_by_id(document_id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    field_id = data.get('field_id')
    value = data.get('value')
    
    if not field_id:
        return jsonify({'error': 'Missing field_id'}), 400
    
    # Update field value
    if 'pdf_fields' in document:
        for field in document['pdf_fields']:
            if field['id'] == field_id:
                field['value'] = value
                break
    
    return jsonify({'success': True, 'field_id': field_id, 'value': value})

@app.route('/api/extract-fields', methods=['POST'])
def extract_fields_api():
    """API endpoint to extract fields from uploaded PDF"""
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400
    
    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{uuid.uuid4()}_{filename}")
        file.save(temp_path)
        
        # Extract PDF fields
        pdf_analysis = extract_pdf_fields(temp_path)
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass
        
        if "error" in pdf_analysis:
            return jsonify({'error': pdf_analysis['error']}), 500
        
        return jsonify({
            'fields': pdf_analysis['fields'],
            'message': f'Successfully extracted {len(pdf_analysis["fields"])} fields from PDF'
        })
        
    except Exception as e:
        # Clean up temporary file on error
        try:
            if 'temp_path' in locals():
                os.remove(temp_path)
        except:
            pass
        
        print(f"Error in extract_fields_api: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500

@app.route('/api/pdf-preview/<document_id>')
def get_pdf_preview(document_id):
    """API endpoint to get PDF preview image"""
    document = get_document_by_id(document_id)
    if not document or 'file_path' not in document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Convert PDF to image
    image_url = convert_pdf_to_image(document['file_path'])
    
    # Get PDF info
    pdf_info = pdf_processor.get_pdf_info(document['file_path'])
    
    return jsonify({
        'preview_url': image_url,
        'page_count': pdf_info.get('page_count', 1),
        'pdf_info': pdf_info
    })

@app.route('/api/pdf-preview-upload', methods=['POST'])
def get_pdf_preview_upload():
    """API endpoint to get PDF preview image from uploaded file"""
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400
    
    file = request.files['pdf_file']
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Get page number from form data (default to None for auto-select)
    page_num = request.form.get('page_num', None)
    if page_num is not None:
        try:
            page_num = int(page_num)
        except ValueError:
            page_num = None
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"preview_{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Convert PDF to image (specific page or auto-select)
        image_url = convert_pdf_to_image(file_path, page_num)
        
        # Get PDF info
        pdf_info = pdf_processor.get_pdf_info(file_path)
        
        # Determine which page was actually rendered
        actual_page = 0  # Default
        if page_num is not None:
            actual_page = min(page_num, pdf_info.get('page_count', 1) - 1)
        else:
            # Find page with most widgets (auto-select logic)
            import fitz
            doc = fitz.open(file_path)
            max_widgets = 0
            for p_num in range(len(doc)):
                page = doc[p_num]
                widgets = list(page.widgets())
                if len(widgets) > max_widgets:
                    max_widgets = len(widgets)
                    actual_page = p_num
            doc.close()
        
        # Clean up temporary file (optional - could keep for later use)
        # os.remove(file_path)
        
        return jsonify({
            'preview_url': image_url,
            'page_count': pdf_info.get('page_count', 1),
            'current_page': actual_page + 1,  # 1-indexed for display
            'pdf_info': pdf_info,
            'filename': filename,
            'file_path': file_path  # Keep for subsequent page requests
        })
        
    except Exception as e:
        print(f"Error generating PDF preview: {e}")
        return jsonify({'error': f'Failed to generate PDF preview: {str(e)}'}), 500

@app.route('/api/pdf-page/<path:file_path>/<int:page_num>')
def get_pdf_page(file_path, page_num):
    """API endpoint to get a specific page of an already uploaded PDF"""
    try:
        # Security check - ensure file path is within uploads directory
        if not file_path.startswith('uploads/'):
            return jsonify({'error': 'Invalid file path'}), 400
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'PDF file not found'}), 404
        
        # Convert specific page to image
        image_url = convert_pdf_to_image(file_path, page_num - 1)  # Convert to 0-indexed
        
        # Get PDF info
        pdf_info = pdf_processor.get_pdf_info(file_path)
        
        return jsonify({
            'preview_url': image_url,
            'page_count': pdf_info.get('page_count', 1),
            'current_page': page_num,
            'pdf_info': pdf_info
        })
        
    except Exception as e:
        print(f"Error generating PDF page: {e}")
        return jsonify({'error': f'Failed to generate PDF page: {str(e)}'}), 500

@app.route('/api/save-fields/<document_id>', methods=['POST'])
def save_fields(document_id):
    """API endpoint to save PDF fields"""
    try:
        document = get_document_by_id(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        data = request.get_json()
        fields = data.get('fields', [])
        
        if USE_DATABASE and db:
            # Save to database
            success = db.save_pdf_fields(document_id, fields)
            if success:
                return jsonify({'success': True, 'message': f'Saved {len(fields)} fields'})
            else:
                return jsonify({'error': 'Failed to save fields to database'}), 500
        else:
            # Update mock data
            for doc in MOCK_DOCUMENTS:
                if doc['id'] == document_id:
                    doc['pdf_fields'] = fields
                    doc['field_assignments'] = {field['id']: field['assigned_to'] for field in fields}
                    break
            
            return jsonify({'success': True, 'message': f'Saved {len(fields)} fields'})
            
    except Exception as e:
        print(f"Error saving fields: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to save fields: {str(e)}'}), 500

@app.route('/api/pdf-editor/<document_id>')
def pdf_editor_page(document_id):
    """PDF Editor page"""
    document = get_document_by_id(document_id)
    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('pdf_editor.html', document=document)

@app.route('/api/field-config/<document_id>/<field_id>', methods=['GET', 'POST'])
def field_configuration(document_id, field_id):
    """Get or save field configuration"""
    if request.method == 'GET':
        if USE_DATABASE and db:
            config = db.get_field_configuration(document_id, field_id)
            return jsonify(config or {})
        return jsonify({})
    
    elif request.method == 'POST':
        data = request.get_json()
        if USE_DATABASE and db:
            success = db.save_field_configuration(document_id, field_id, data)
            return jsonify({'success': success})
        return jsonify({'success': True})

@app.route('/api/update-field-position/<field_id>', methods=['POST'])
def update_field_position_api(field_id):
    """Update field position via API"""
    try:
        data = request.get_json()
        position = data.get('position', {})
        
        if USE_DATABASE and db:
            success = db.update_field_position(field_id, position)
            return jsonify({'success': success})
        else:
            # Update in mock data
            for doc in MOCK_DOCUMENTS:
                for field in doc.get('pdf_fields', []):
                    if field['id'] == field_id:
                        field['position'] = position
                        return jsonify({'success': True})
            
            return jsonify({'error': 'Field not found'}), 404
            
    except Exception as e:
        print(f"Error updating field position: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/preview/<document_id>')
def preview_document(document_id):
    """Preview document page"""
    document = get_document_by_id(document_id)
    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('preview.html', document=document)

@app.route('/api/debug-pdf/<document_id>')
def debug_pdf_extraction(document_id):
    """Debug endpoint to test PDF field extraction"""
    document = get_document_by_id(document_id)
    if not document or 'file_path' not in document:
        return jsonify({'error': 'Document not found'}), 404
    
    file_path = document['file_path']
    
    # Test both extraction methods
    results = {
        'file_path': file_path,
        'file_exists': os.path.exists(file_path),
        'extraction_results': {}
    }
    
    # Test PyMuPDF extraction
    try:
        pymupdf_result = pdf_processor.extract_fields_with_pymupdf(file_path)
        results['extraction_results']['pymupdf'] = pymupdf_result
    except Exception as e:
        results['extraction_results']['pymupdf'] = {'error': str(e)}
    
    # Test legacy extraction
    try:
        legacy_result = extract_pdf_fields_legacy(file_path)
        results['extraction_results']['legacy'] = legacy_result
    except Exception as e:
        results['extraction_results']['legacy'] = {'error': str(e)}
    
    # Get PDF info
    try:
        pdf_info = pdf_processor.get_pdf_info(file_path)
        results['pdf_info'] = pdf_info
    except Exception as e:
        results['pdf_info'] = {'error': str(e)}
    
    return jsonify(results)

@app.route('/debug-fields')
def debug_fields_page():
    """Debug page for testing PDF field extraction"""
    return render_template('debug_fields.html')

@app.route('/realtime-editor')
def realtime_pdf_editor():
    """Redirect to real-time PDF editor"""
    document_id = request.args.get('document_id')
    if document_id:
        return redirect(url_for('realtime.realtime_editor', document_id=document_id))
    return redirect(url_for('realtime.realtime_editor'))

if __name__ == '__main__':
    print("🚀 PDF Collaborator Flask App Starting...")
    print("📊 Using database with real-time features")
    print("🌐 Access at: http://localhost:5006")
    print("🚀 PDF Collaborator running at: http://localhost:5006")
    
    # Use standard Flask development server
    app.run(debug=True, port=5006, host='0.0.0.0')