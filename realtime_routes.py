#!/usr/bin/env python3
"""
Real-time PDF Editor Routes and WebSocket Handlers
"""

from flask import Blueprint, render_template, request, jsonify, send_file, session
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime, timedelta
import tempfile
from typing import List, Dict, Any

# Import our modules
from models import db, Document, DocumentField, PDFConfiguration, RealTimeSession, FieldType, DocumentStatus, User, AuditLog
from realtime_pdf_processor import get_realtime_pdf_processor
from config import Config

# Create blueprint
realtime_bp = Blueprint('realtime', __name__, url_prefix='/realtime')

# Initialize SocketIO (will be attached to app in main app.py)
socketio = None

def init_socketio(app):
    """Initialize SocketIO with the Flask app"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
    
    # Register WebSocket event handlers
    register_websocket_handlers()
    
    return socketio

# Active sessions tracking
active_sessions = {}

@realtime_bp.route('/')
def realtime_editor():
    """Main real-time editor page"""
    document_id = request.args.get('document_id')
    document = None
    
    if document_id:
        document = Document.query.get(document_id)
        if not document:
            return render_template('error.html', message="Document not found"), 404
    
    return render_template('realtime_pdf_editor.html', document=document)

@realtime_bp.route('/api/documents/upload', methods=['POST'])
def upload_pdf():
    """Upload and process PDF for real-time editing"""
    try:
        if 'pdf' not in request.files:
            return jsonify({'success': False, 'message': 'No PDF file provided'}), 400
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'message': 'File must be a PDF'}), 400
        
        # Generate unique document ID and filename
        document_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, f"{document_id}_{filename}")
        
        # Save uploaded file
        file.save(file_path)
        
        # Process PDF with real-time processor
        processor = get_realtime_pdf_processor()
        
        # Extract PDF info
        pdf_info = processor.extract_pdf_info(file_path)
        if 'error' in pdf_info:
            os.remove(file_path)
            return jsonify({'success': False, 'message': f'PDF processing failed: {pdf_info["error"]}'}), 400
        
        # Detect fields
        field_detection = processor.detect_fields_with_positions(file_path)
        if 'error' in field_detection:
            os.remove(file_path)
            return jsonify({'success': False, 'message': f'Field detection failed: {field_detection["error"]}'}), 400
        
        # Create document in database
        document = Document(
            id=document_id,
            name=filename,
            original_filename=filename,
            file_path=file_path,
            status=DocumentStatus.DRAFT,
            created_by_id=1,  # TODO: Get actual user ID from session
            doc_metadata={'upload_info': 'Real-time editor upload'}
        )
        db.session.add(document)
        
        # Create PDF configuration
        pdf_config = PDFConfiguration(
            id=str(uuid.uuid4()),
            document_id=document_id,
            pdf_info=pdf_info,
            field_mapping=field_detection.get('field_mapping', {}),
            rendering_config={'default_zoom': 1.0, 'default_page': 1}
        )
        db.session.add(pdf_config)
        
        # Create document fields
        for field_data in field_detection.get('fields', []):
            try:
                # Validate field type
                field_type = FieldType.TEXT
                if field_data['type'] in [ft.value for ft in FieldType]:
                    field_type = FieldType(field_data['type'])
                
                field = DocumentField(
                    id=field_data['id'],
                    document_id=document_id,
                    name=field_data['name'],
                    pdf_field_name=field_data['pdf_field_name'],
                    field_type=field_type,
                    value=field_data.get('value', ''),
                    required=field_data.get('required', False),
                    assigned_to=field_data.get('assigned_to', 'user1'),
                    position=field_data['position'],
                    styling=field_data.get('styling', {})
                )
                db.session.add(field)
                
            except Exception as e:
                print(f"⚠️  Error creating field {field_data.get('name', 'unknown')}: {e}")
                continue
        
        # Commit to database
        db.session.commit()
        
        # Log audit entry
        audit_log = AuditLog(
            document_id=document_id,
            action='upload',
            new_value=f'Uploaded PDF with {len(field_detection.get("fields", []))} fields',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'document': {
                'id': document_id,
                'name': filename,
                'field_count': len(field_detection.get('fields', [])),
                'page_count': pdf_info.get('page_count', 1)
            }
        })
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Upload failed'}), 500

@realtime_bp.route('/api/documents/<document_id>')
def get_document(document_id):
    """Get document information"""
    try:
        document = Document.query.get_or_404(document_id)
        
        return jsonify({
            'id': document.id,
            'name': document.name,
            'original_filename': document.original_filename,
            'status': document.status.value if document.status else None,
            'created_at': document.created_at.isoformat() if document.created_at else None,
            'file_path': f'/api/documents/{document_id}/preview',  # Serve through API
            'metadata': document.doc_metadata
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@realtime_bp.route('/api/documents/<document_id>/fields')
def get_document_fields(document_id):
    """Get all fields for a document"""
    try:
        fields = DocumentField.query.filter_by(document_id=document_id).all()
        
        return jsonify([field.to_dict() for field in fields])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@realtime_bp.route('/api/documents/<document_id>/preview')
def get_document_preview(document_id):
    """Serve PDF file for preview"""
    try:
        document = Document.query.get_or_404(document_id)
        
        if not os.path.exists(document.file_path):
            return jsonify({'error': 'PDF file not found'}), 404
        
        return send_file(
            document.file_path,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=document.original_filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@realtime_bp.route('/api/documents/<document_id>/save', methods=['POST'])
def save_document(document_id):
    """Save document field changes"""
    try:
        data = request.get_json()
        fields_data = data.get('fields', [])
        
        # Update fields in database
        updated_count = 0
        for field_data in fields_data:
            field = DocumentField.query.get(field_data['id'])
            if field and field.document_id == document_id:
                # Update field properties
                if 'value' in field_data:
                    old_value = field.value
                    field.value = field_data['value']
                    field.mark_as_filled()
                    
                    # Log the change
                    audit_log = AuditLog(
                        document_id=document_id,
                        field_id=field.id,
                        action='update',
                        old_value=old_value,
                        new_value=field.value,
                        ip_address=request.remote_addr
                    )
                    db.session.add(audit_log)
                
                if 'name' in field_data:
                    field.name = field_data['name']
                if 'required' in field_data:
                    field.required = field_data['required']
                if 'assigned_to' in field_data:
                    field.assigned_to = field_data['assigned_to']
                if 'styling' in field_data:
                    field.styling = field_data['styling']
                
                updated_count += 1
        
        # Update document timestamp
        document = Document.query.get(document_id)
        if document:
            document.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated_fields': updated_count,
            'message': f'Successfully updated {updated_count} fields'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@realtime_bp.route('/api/documents/<document_id>/download')
def download_filled_pdf(document_id):
    """Generate and download filled PDF"""
    try:
        document = Document.query.get_or_404(document_id)
        fields = DocumentField.query.filter_by(document_id=document_id).all()
        
        # Prepare field values for PDF generation
        field_values = {}
        for field in fields:
            if field.value:
                field_values[field.id] = {
                    'value': field.value,
                    'pdf_field_name': field.pdf_field_name,
                    'type': field.field_type.value,
                    'name': field.name,
                    'position': field.position,
                    'styling': field.styling
                }
        
        # Generate filled PDF
        processor = get_realtime_pdf_processor()
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            output_path = temp_file.name
        
        success = processor.fill_pdf_realtime(
            document.file_path,
            field_values,
            output_path
        )
        
        if not success:
            if os.path.exists(output_path):
                os.remove(output_path)
            return jsonify({'error': 'PDF generation failed'}), 500
        
        # Log download
        audit_log = AuditLog(
            document_id=document_id,
            action='download',
            new_value='Generated filled PDF',
            ip_address=request.remote_addr
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return send_file(
            output_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"filled_{document.original_filename}"
        )
        
    except Exception as e:
        print(f"❌ Download error: {e}")
        return jsonify({'error': str(e)}), 500

# WebSocket Event Handlers
def register_websocket_handlers():
    """Register all WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Handle client connection"""
        try:
            document_id = request.args.get('documentId')
            session_id = request.args.get('sessionId')
            
            if not document_id or not session_id:
                return False
            
            # Join document room
            join_room(f"document_{document_id}")
            
            # Create or update session
            real_session = RealTimeSession.query.filter_by(
                id=session_id,
                document_id=document_id
            ).first()
            
            if not real_session:
                real_session = RealTimeSession(
                    id=session_id,
                    document_id=document_id,
                    session_data={'connected_at': datetime.utcnow().isoformat()}
                )
                db.session.add(real_session)
            else:
                real_session.last_activity = datetime.utcnow()
                real_session.is_active = True
            
            db.session.commit()
            
            # Track active session
            active_sessions[session_id] = {
                'document_id': document_id,
                'connected_at': datetime.utcnow(),
                'socket_id': request.sid
            }
            
            # Notify other users
            emit('user_joined', {
                'session_id': session_id,
                'document_id': document_id,
                'timestamp': datetime.utcnow().isoformat()
            }, room=f"document_{document_id}", include_self=False)
            
            print(f"✅ User connected: {session_id} to document {document_id}")
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        try:
            # Find and clean up session
            session_id = None
            for sid, session_data in active_sessions.items():
                if session_data.get('socket_id') == request.sid:
                    session_id = sid
                    break
            
            if session_id:
                session_data = active_sessions.pop(session_id, {})
                document_id = session_data.get('document_id')
                
                # Update session in database
                real_session = RealTimeSession.query.get(session_id)
                if real_session:
                    real_session.is_active = False
                    real_session.last_activity = datetime.utcnow()
                    db.session.commit()
                
                # Notify other users
                if document_id:
                    emit('user_left', {
                        'session_id': session_id,
                        'document_id': document_id,
                        'timestamp': datetime.utcnow().isoformat()
                    }, room=f"document_{document_id}")
                
                print(f"👋 User disconnected: {session_id}")
            
        except Exception as e:
            print(f"❌ Disconnection error: {e}")
    
    @socketio.on('field_update')
    def handle_field_update(data):
        """Handle real-time field updates"""
        try:
            field_id = data.get('fieldId')
            property_name = data.get('property')
            value = data.get('value')
            session_id = data.get('sessionId')
            
            if not all([field_id, property_name, session_id]):
                return
            
            # Update field in database
            field = DocumentField.query.get(field_id)
            if field:
                old_value = getattr(field, property_name, None)
                setattr(field, property_name, value)
                
                if property_name == 'value':
                    field.mark_as_filled()
                
                field.updated_at = datetime.utcnow()
                db.session.commit()
                
                # Broadcast update to other users in the same document
                emit('field_updated', {
                    'fieldId': field_id,
                    'property': property_name,
                    'value': value,
                    'sessionId': session_id,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=f"document_{field.document_id}", include_self=False)
                
                # Log the change
                audit_log = AuditLog(
                    document_id=field.document_id,
                    field_id=field_id,
                    action='realtime_update',
                    old_value=str(old_value) if old_value else None,
                    new_value=str(value),
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
                
                print(f"🔄 Field updated: {field_id}.{property_name} = {value}")
            
        except Exception as e:
            print(f"❌ Field update error: {e}")
            db.session.rollback()
    
    @socketio.on('field_focus')
    def handle_field_focus(data):
        """Handle field focus events for collaboration"""
        try:
            field_id = data.get('fieldId')
            session_id = data.get('sessionId')
            action = data.get('action')  # 'focus' or 'blur'
            
            if not all([field_id, session_id, action]):
                return
            
            # Get field to find document
            field = DocumentField.query.get(field_id)
            if field:
                # Broadcast focus event to other users
                emit('field_focus', {
                    'fieldId': field_id,
                    'sessionId': session_id,
                    'action': action,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=f"document_{field.document_id}", include_self=False)
                
                print(f"👁️  Field {action}: {field_id} by {session_id}")
            
        except Exception as e:
            print(f"❌ Field focus error: {e}")
    
    @socketio.on('request_document_state')
    def handle_document_state_request(data):
        """Send current document state to requesting client"""
        try:
            document_id = data.get('documentId')
            session_id = data.get('sessionId')
            
            if not document_id:
                return
            
            # Get current field states
            fields = DocumentField.query.filter_by(document_id=document_id).all()
            field_states = {}
            
            for field in fields:
                field_states[field.id] = {
                    'value': field.value,
                    'updated_at': field.updated_at.isoformat() if field.updated_at else None,
                    'filled_at': field.filled_at.isoformat() if field.filled_at else None
                }
            
            # Send state to requesting client
            emit('document_state', {
                'documentId': document_id,
                'fields': field_states,
                'timestamp': datetime.utcnow().isoformat()
            }, room=request.sid)
            
            print(f"📤 Sent document state for {document_id} to {session_id}")
            
        except Exception as e:
            print(f"❌ Document state error: {e}")

# Helper functions
def cleanup_inactive_sessions():
    """Clean up inactive sessions (called periodically)"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        inactive_sessions = RealTimeSession.query.filter(
            RealTimeSession.last_activity < cutoff_time,
            RealTimeSession.is_active == True
        ).all()
        
        for session in inactive_sessions:
            session.is_active = False
        
        db.session.commit()
        print(f"🧹 Cleaned up {len(inactive_sessions)} inactive sessions")
        
    except Exception as e:
        print(f"❌ Session cleanup error: {e}")

def get_active_users_for_document(document_id: str) -> List[Dict[str, Any]]:
    """Get list of active users for a document"""
    try:
        active_users = []
        
        for session_id, session_data in active_sessions.items():
            if session_data.get('document_id') == document_id:
                active_users.append({
                    'session_id': session_id,
                    'connected_at': session_data['connected_at'].isoformat(),
                    'socket_id': session_data['socket_id']
                })
        
        return active_users
        
    except Exception as e:
        print(f"❌ Error getting active users: {e}")
        return []