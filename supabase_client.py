import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv
import base64

load_dotenv()

class SupabaseManager:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(url, key)
    
    def create_document(self, document_id: str, name: str, file_path: str, owner_id: str, metadata: Dict[str, Any] = None) -> str:
        """Create a new document record"""
        if metadata is None:
            metadata = {}
            
        document_record = {
            'id': document_id,
            'name': name,
            'status': 'pending',
            'file_path': file_path,
            'original_filename': os.path.basename(file_path),
            'user1_data': metadata.get('user1_data', {}),
            'user2_data': metadata.get('user2_data', {}),
            'supporting_docs': metadata.get('supporting_docs', []),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        result = self.supabase.table('documents').insert(document_record).execute()
        
        # Create user-document relationship with owner role
        self.add_user_to_document(document_id, owner_id, 'owner', created_by=owner_id)
        
        # Log the creation
        self.log_action(document_id, owner_id, 'document_created', 
                       f"Document '{name}' created")
        
        return document_id
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        result = self.supabase.table('documents').select('*').eq('id', document_id).execute()
        
        if not result.data:
            return None
        
        document = result.data[0]
        
        # Get PDF fields
        document['pdf_fields'] = self.get_document_fields(document_id)
        
        return document
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents"""
        result = self.supabase.table('documents').select('*').order('created_at', desc=True).execute()
        
        documents = result.data
        
        # Add PDF fields to each document
        for document in documents:
            document['pdf_fields'] = self.get_document_fields(document['id'])
        
        return documents
    
    def update_document(self, document_id: str, updates: Dict[str, Any]) -> bool:
        """Update a document"""
        updates['updated_at'] = datetime.now().isoformat()
        
        result = self.supabase.table('documents').update(updates).eq('id', document_id).execute()
        
        # Log the update
        self.log_action(document_id, 'system', 'document_updated', 
                       f"Document updated: {list(updates.keys())}")
        
        return len(result.data) > 0
    
    def save_pdf_fields(self, document_id: str, fields: List[Dict[str, Any]]) -> bool:
        """Save PDF fields for a document"""
        # First, delete existing fields for this document
        self.supabase.table('pdf_fields').delete().eq('document_id', document_id).execute()
        
        # Prepare fields for insertion
        field_records = []
        for field in fields:
            position = field.get('position', {})
            
            field_record = {
                'id': field.get('id', str(uuid.uuid4())),
                'document_id': document_id,
                'field_name': field.get('name', ''),
                'field_type': field.get('type', 'text'),
                'field_value': field.get('value', ''),
                'assigned_to': field.get('assigned_to', 'user1'),
                'position_x': position.get('x', 0),
                'position_y': position.get('y', 0),
                'width': position.get('width', 0),
                'height': position.get('height', 0),
                'page_number': field.get('page', 0),
                'source': field.get('source', 'extracted'),
                'pdf_field_name': field.get('pdf_field_name', ''),
                'is_required': field.get('is_required', False),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            field_records.append(field_record)
        
        if field_records:
            result = self.supabase.table('pdf_fields').insert(field_records).execute()
            
            # Log the field save
            self.log_action(document_id, 'system', 'fields_saved', 
                           f"Saved {len(fields)} PDF fields")
            
            return len(result.data) > 0
        
        return True
    
    def get_document_fields(self, document_id: str) -> List[Dict[str, Any]]:
        """Get PDF fields for a document"""
        result = self.supabase.table('pdf_fields').select('*').eq('document_id', document_id).order('page_number').order('position_y').execute()
        
        fields = []
        for field in result.data:
            # Reconstruct position object
            field['position'] = {
                'x': field['position_x'],
                'y': field['position_y'],
                'width': field['width'],
                'height': field['height']
            }
            # Clean up individual position fields for API compatibility
            field['name'] = field['field_name']
            field['type'] = field['field_type']
            field['value'] = field['field_value']
            field['page'] = field['page_number']
            
            fields.append(field)
        
        return fields
    
    def update_field_value(self, field_id: str, value: str, user_type: str = 'user') -> bool:
        """Update a field value"""
        updates = {
            'field_value': value,
            'updated_at': datetime.now().isoformat()
        }
        
        result = self.supabase.table('pdf_fields').update(updates).eq('id', field_id).execute()
        
        if result.data:
            # Get document_id for logging
            field_result = self.supabase.table('pdf_fields').select('document_id').eq('id', field_id).execute()
            if field_result.data:
                self.log_action(field_result.data[0]['document_id'], user_type, 'field_updated', 
                               f"Field {field_id} updated to '{value}'")
        
        return len(result.data) > 0
    
    def update_field_assignment(self, field_id: str, assigned_to: str) -> bool:
        """Update field assignment"""
        updates = {
            'assigned_to': assigned_to,
            'updated_at': datetime.now().isoformat()
        }
        
        result = self.supabase.table('pdf_fields').update(updates).eq('id', field_id).execute()
        
        if result.data:
            # Get document_id for logging
            field_result = self.supabase.table('pdf_fields').select('document_id').eq('id', field_id).execute()
            if field_result.data:
                self.log_action(field_result.data[0]['document_id'], 'system', 'field_reassigned', 
                               f"Field {field_id} assigned to {assigned_to}")
        
        return len(result.data) > 0
    
    def update_field_position(self, field_id: str, position: Dict[str, float]) -> bool:
        """Update field position"""
        updates = {
            'position_x': position.get('x', 0),
            'position_y': position.get('y', 0),
            'width': position.get('width', 0),
            'height': position.get('height', 0),
            'updated_at': datetime.now().isoformat()
        }
        
        result = self.supabase.table('pdf_fields').update(updates).eq('id', field_id).execute()
        
        return len(result.data) > 0
    
    def save_field_configuration(self, document_id: str, field_id: str, configuration: Dict[str, Any]) -> bool:
        """Save field configuration"""
        config_id = str(uuid.uuid4())
        
        # Delete existing configuration
        self.supabase.table('field_configurations').delete().eq('document_id', document_id).eq('field_id', field_id).execute()
        
        # Insert new configuration
        config_record = {
            'id': config_id,
            'document_id': document_id,
            'field_id': field_id,
            'configuration': configuration,
            'created_at': datetime.now().isoformat()
        }
        
        result = self.supabase.table('field_configurations').insert(config_record).execute()
        
        return len(result.data) > 0
    
    def get_field_configuration(self, document_id: str, field_id: str) -> Optional[Dict[str, Any]]:
        """Get field configuration"""
        result = self.supabase.table('field_configurations').select('configuration').eq('document_id', document_id).eq('field_id', field_id).execute()
        
        if result.data:
            return result.data[0]['configuration']
        return None
    
    def log_action(self, document_id: str, user_type: str, action: str, details: str = None):
        """Log an action in the audit log"""
        log_record = {
            'document_id': document_id,
            'user_type': user_type,
            'action': action,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.supabase.table('audit_log').insert(log_record).execute()
    
    def get_audit_log(self, document_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        query = self.supabase.table('audit_log').select('*')
        
        if document_id:
            query = query.eq('document_id', document_id)
        
        result = query.order('timestamp', desc=True).limit(limit).execute()
        
        return result.data
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and all related data"""
        # Delete related data first (if not using CASCADE)
        self.supabase.table('pdf_fields').delete().eq('document_id', document_id).execute()
        self.supabase.table('field_configurations').delete().eq('document_id', document_id).execute()
        
        # Delete document
        result = self.supabase.table('documents').delete().eq('id', document_id).execute()
        
        # Log the deletion
        self.log_action(document_id, 'system', 'document_deleted', 
                       f"Document {document_id} deleted")
        
        return len(result.data) > 0
    
    def create_document_template(self, name: str, description: str, field_definitions: List[Dict[str, Any]]) -> str:
        """Create a document template"""
        template_id = str(uuid.uuid4())
        
        template_record = {
            'id': template_id,
            'name': name,
            'description': description,
            'field_definitions': field_definitions,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        result = self.supabase.table('document_templates').insert(template_record).execute()
        
        return template_id
    
    def get_document_templates(self) -> List[Dict[str, Any]]:
        """Get all document templates"""
        result = self.supabase.table('document_templates').select('*').order('created_at', desc=True).execute()
        
        return result.data
    
    def get_document_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a document template by ID"""
        result = self.supabase.table('document_templates').select('*').eq('id', template_id).execute()
        
        if result.data:
            return result.data[0]
        return None
    
    # User Authentication Methods
    def create_user(self, email: str, password_hash: str, name: str = None, role: str = 'user') -> Optional[str]:
        """Create a new user account"""
        try:
            user_data = {
                'email': email.lower().strip(),
                'password_hash': password_hash,
                'name': name,
                'role': role,
                'is_active': True,
                'email_verified': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('users').insert(user_data).execute()
            
            if result.data:
                user_id = result.data[0]['id']
                self.log_action(None, 'system', 'user_created', f"User '{email}' created with role '{role}'")
                return user_id
            return None
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        try:
            result = self.supabase.table('users').select('*').eq('email', email.lower().strip()).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            result = self.supabase.table('users').select('*').eq('id', user_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def update_user_login(self, user_id: str, ip_address: str = None) -> bool:
        """Update user's last login time and reset login attempts"""
        try:
            update_data = {
                'last_login': datetime.now().isoformat(),
                'login_attempts': 0,
                'locked_until': None,
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('users').update(update_data).eq('id', user_id).execute()
            
            # Log the login
            self.log_action(None, user_id, 'user_login', f"User logged in from {ip_address or 'unknown IP'}")
            
            return len(result.data) > 0
            
        except Exception as e:
            print(f"Error updating user login: {e}")
            return False
    
    def increment_login_attempts(self, user_id: str) -> bool:
        """Increment failed login attempts and lock account if necessary"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            attempts = user.get('login_attempts', 0) + 1
            update_data = {
                'login_attempts': attempts,
                'updated_at': datetime.now().isoformat()
            }
            
            # Lock account after 5 failed attempts for 15 minutes
            if attempts >= 5:
                from datetime import timedelta
                locked_until = datetime.now() + timedelta(minutes=15)
                update_data['locked_until'] = locked_until.isoformat()
                self.log_action(None, user_id, 'user_locked', f"User account locked after {attempts} failed attempts")
            
            result = self.supabase.table('users').update(update_data).eq('id', user_id).execute()
            return len(result.data) > 0
            
        except Exception as e:
            print(f"Error incrementing login attempts: {e}")
            return False
    
    def is_user_locked(self, user_id: str) -> bool:
        """Check if user account is currently locked"""
        try:
            user = self.get_user_by_id(user_id)
            if not user or not user.get('locked_until'):
                return False
            
            from dateutil.parser import parse
            locked_until = parse(user['locked_until'])
            return datetime.now() < locked_until.replace(tzinfo=None)
            
        except Exception as e:
            print(f"Error checking user lock status: {e}")
            return False
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update user profile information"""
        try:
            # Only allow updating certain fields
            allowed_fields = ['name', 'email']
            update_data = {key: value for key, value in profile_data.items() if key in allowed_fields}
            update_data['updated_at'] = datetime.now().isoformat()
            
            # If email is being updated, mark as unverified
            if 'email' in update_data:
                update_data['email'] = update_data['email'].lower().strip()
                update_data['email_verified'] = False
            
            result = self.supabase.table('users').update(update_data).eq('id', user_id).execute()
            
            if len(result.data) > 0:
                self.log_action(None, user_id, 'profile_updated', f"User profile updated")
                return True
            return False
            
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    def update_user_password(self, user_id: str, new_password_hash: str) -> bool:
        """Update user's password hash"""
        try:
            update_data = {
                'password_hash': new_password_hash,
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('users').update(update_data).eq('id', user_id).execute()
            
            if len(result.data) > 0:
                self.log_action(None, user_id, 'password_changed', "User password changed")
                return True
            return False
            
        except Exception as e:
            print(f"Error updating user password: {e}")
            return False
    
    def get_all_users(self, admin_user_id: str) -> List[Dict[str, Any]]:
        """Get all users (admin only)"""
        try:
            # Verify admin access
            admin = self.get_user_by_id(admin_user_id)
            if not admin or admin.get('role') != 'admin':
                return []
            
            result = self.supabase.table('users').select('id, email, name, role, is_active, created_at, last_login').order('created_at', desc=True).execute()
            return result.data
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def deactivate_user(self, admin_user_id: str, target_user_id: str) -> bool:
        """Deactivate a user account (admin only)"""
        try:
            # Verify admin access
            admin = self.get_user_by_id(admin_user_id)
            if not admin or admin.get('role') != 'admin':
                return False
            
            update_data = {
                'is_active': False,
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('users').update(update_data).eq('id', target_user_id).execute()
            
            if len(result.data) > 0:
                self.log_action(None, admin_user_id, 'user_deactivated', f"Admin deactivated user {target_user_id}")
                return True
            return False
            
        except Exception as e:
            print(f"Error deactivating user: {e}")
            return False
    
    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all documents accessible to a user"""
        try:
            # Get documents owned by user or shared with user
            result = self.supabase.table('documents').select('''
                *,
                user_documents!inner(role, can_edit, can_share)
            ''').eq('user_documents.user_id', user_id).execute()
            
            return result.data
            
        except Exception as e:
            print(f"Error getting user documents: {e}")
            return []
    
    def add_user_to_document(self, document_id: str, user_id: str, role: str, can_edit: bool = True, can_share: bool = False, created_by: str = None) -> bool:
        """Add a user to a document with specific role and permissions"""
        try:
            user_doc_data = {
                'user_id': user_id,
                'document_id': document_id,
                'role': role,
                'can_edit': can_edit,
                'can_share': can_share,
                'created_by': created_by,
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('user_documents').insert(user_doc_data).execute()
            
            if result.data:
                self.log_action(document_id, created_by or 'system', 'user_added_to_document', 
                              f"User {user_id} added to document with role {role}")
                return True
            return False
            
        except Exception as e:
            print(f"Error adding user to document: {e}")
            return False
    
    def create_document_invitation(self, document_id: str, invited_by: str, invited_email: str, role: str, expires_hours: int = 168) -> Optional[str]:
        """Create an invitation for someone to access a document"""
        try:
            import secrets
            from datetime import timedelta
            
            # Generate secure token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=expires_hours)
            
            # Check if user with this email exists
            existing_user = self.get_user_by_email(invited_email)
            
            invitation_data = {
                'document_id': document_id,
                'invited_by': invited_by,
                'invited_email': invited_email.lower().strip(),
                'invited_user_id': existing_user['id'] if existing_user else None,
                'role': role,
                'token': token,
                'expires_at': expires_at.isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('document_invitations').insert(invitation_data).execute()
            
            if result.data:
                self.log_action(document_id, invited_by, 'invitation_created', 
                              f"Invitation sent to {invited_email} for role {role}")
                return token
            return None
            
        except Exception as e:
            print(f"Error creating document invitation: {e}")
            return None
    
    def get_invitation_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get invitation details by token"""
        try:
            result = self.supabase.table('document_invitations').select('''
                *,
                documents(name, status),
                users!document_invitations_invited_by_fkey(name, email)
            ''').eq('token', token).execute()
            
            if result.data:
                invitation = result.data[0]
                # Check if invitation is expired
                from dateutil.parser import parse
                expires_at = parse(invitation['expires_at'])
                if datetime.now() > expires_at.replace(tzinfo=None):
                    return None
                return invitation
            return None
            
        except Exception as e:
            print(f"Error getting invitation by token: {e}")
            return None
    
    def accept_invitation(self, token: str, user_id: str) -> bool:
        """Accept a document invitation"""
        try:
            invitation = self.get_invitation_by_token(token)
            if not invitation or invitation.get('accepted_at'):
                return False
            
            # Add user to document
            success = self.add_user_to_document(
                invitation['document_id'],
                user_id,
                invitation['role'],
                can_edit=True,
                can_share=False,
                created_by=invitation['invited_by']
            )
            
            if success:
                # Mark invitation as accepted
                update_data = {
                    'accepted_at': datetime.now().isoformat(),
                    'invited_user_id': user_id
                }
                
                self.supabase.table('document_invitations').update(update_data).eq('token', token).execute()
                
                self.log_action(invitation['document_id'], user_id, 'invitation_accepted', 
                              f"User accepted invitation for role {invitation['role']}")
                return True
            return False
            
        except Exception as e:
            print(f"Error accepting invitation: {e}")
            return False
    
    # Template Document Methods
    def upload_template_document(self, name: str, description: str, file_path: str) -> Optional[str]:
        """Upload a PDF template document to the database"""
        try:
            # Read file as binary
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Get file info
            file_size = len(file_data)
            filename = os.path.basename(file_path)
            
            template_data = {
                'name': name,
                'description': description,
                'file_data': base64.b64encode(file_data).decode('utf-8'),
                'filename': filename,
                'file_size': file_size,
                'content_type': 'application/pdf',
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('template_documents').insert(template_data).execute()
            
            if len(result.data) > 0:
                template_id = result.data[0]['id']
                print(f"✅ Template document uploaded: {name} (ID: {template_id})")
                return template_id
            return None
            
        except Exception as e:
            print(f"Error uploading template document: {e}")
            return None
    
    def get_template_document(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a template document by ID"""
        try:
            result = self.supabase.table('template_documents').select('*').eq('id', template_id).eq('is_active', True).execute()
            
            if len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"Error getting template document: {e}")
            return None
    
    def get_active_templates(self) -> List[Dict[str, Any]]:
        """Get all active template documents"""
        try:
            result = self.supabase.table('template_documents').select('id, name, description, filename, file_size, created_at').eq('is_active', True).order('created_at', desc=True).execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting template documents: {e}")
            return []
    
    def get_template_file_data(self, template_id: str) -> Optional[bytes]:
        """Get the binary file data for a template document"""
        try:
            result = self.supabase.table('template_documents').select('file_data').eq('id', template_id).eq('is_active', True).execute()
            
            if len(result.data) > 0:
                file_data_b64 = result.data[0]['file_data']
                return base64.b64decode(file_data_b64)
            return None
            
        except Exception as e:
            print(f"Error getting template file data: {e}")
            return None