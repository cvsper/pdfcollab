"""
Custom decorators for access control and permissions
"""

from functools import wraps
from flask import flash, redirect, url_for, jsonify, request
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def document_access_required(f):
    """Decorator to check if user can access a specific document"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this document', 'error')
            return redirect(url_for('auth.login'))
        
        # Get document_id from URL parameters
        document_id = kwargs.get('document_id') or request.view_args.get('document_id')
        
        if not document_id:
            flash('Document not found', 'error')
            return redirect(url_for('dashboard'))
        
        # Import here to avoid circular imports
        from app import db
        
        # Check if user can access this document
        if not current_user.can_access_document(document_id, db):
            flash('Access denied. You do not have permission to view this document.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def document_edit_required(f):
    """Decorator to check if user can edit a specific document"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to edit this document', 'error')
            return redirect(url_for('auth.login'))
        
        # Get document_id from URL parameters
        document_id = kwargs.get('document_id') or request.view_args.get('document_id')
        
        if not document_id:
            flash('Document not found', 'error')
            return redirect(url_for('dashboard'))
        
        # Import here to avoid circular imports
        from app import db
        
        # Check if user can edit this document
        if not current_user.can_edit_document(document_id, db):
            flash('Access denied. You do not have permission to edit this document.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """Decorator to require specific role for document access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page', 'error')
                return redirect(url_for('auth.login'))
            
            # Get document_id from URL parameters
            document_id = kwargs.get('document_id') or request.view_args.get('document_id')
            
            if not document_id:
                flash('Document not found', 'error')
                return redirect(url_for('dashboard'))
            
            # Import here to avoid circular imports
            from app import db
            
            # Admins can access everything
            if current_user.is_admin():
                return f(*args, **kwargs)
            
            # Check user's role in this document
            user_role = current_user.get_role_in_document(document_id, db)
            
            if user_role != required_role:
                flash(f'Access denied. This page requires {required_role} role.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_auth_required(f):
    """Decorator for API endpoints requiring authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def api_admin_required(f):
    """Decorator for API endpoints requiring admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not current_user.is_admin():
            return jsonify({'error': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def api_document_access_required(f):
    """Decorator for API endpoints requiring document access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get document_id from URL parameters or request data
        document_id = (kwargs.get('document_id') or 
                      request.view_args.get('document_id') or
                      request.json.get('document_id') if request.is_json else None)
        
        if not document_id:
            return jsonify({'error': 'Document ID required'}), 400
        
        # Import here to avoid circular imports
        from app import db
        
        # Check if user can access this document
        if not current_user.can_access_document(document_id, db):
            return jsonify({'error': 'Access denied'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def check_document_ownership(document_id):
    """Helper function to check if current user owns a document"""
    if not current_user.is_authenticated:
        return False
    
    if current_user.is_admin():
        return True
    
    try:
        from app import db
        user_docs = db.get_user_documents(current_user.id)
        
        for doc in user_docs:
            if doc['id'] == document_id:
                user_doc_info = doc.get('user_documents', {})
                return user_doc_info.get('role') == 'owner'
        
        return False
    except Exception as e:
        print(f"Error checking document ownership: {e}")
        return False

def get_user_role_in_document(document_id):
    """Helper function to get user's role in a document"""
    if not current_user.is_authenticated:
        return None
    
    try:
        from app import db
        return current_user.get_role_in_document(document_id, db)
    except Exception as e:
        print(f"Error getting user role: {e}")
        return None