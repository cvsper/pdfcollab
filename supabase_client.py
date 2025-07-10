import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseManager:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(url, key)
    
    def create_document(self, document_data: Dict[str, Any]) -> str:
        """Create a new document record"""
        document_id = document_data.get('id', str(uuid.uuid4()))
        
        document_record = {
            'id': document_id,
            'name': document_data.get('name', ''),
            'status': document_data.get('status', 'pending'),
            'file_path': document_data.get('file_path'),
            'original_filename': document_data.get('original_filename'),
            'file_size': document_data.get('file_size'),
            'user1_data': document_data.get('user1_data', {}),
            'user2_data': document_data.get('user2_data', {}),
            'supporting_docs': document_data.get('supporting_docs', []),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        result = self.supabase.table('documents').insert(document_record).execute()
        
        # Log the creation
        self.log_action(document_id, 'system', 'document_created', 
                       f"Document '{document_data.get('name')}' created")
        
        return document_id
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        try:
            result = self.supabase.table('documents').select('*').eq('id', document_id).execute()
            
            if not result.data:
                return None
            
            document = result.data[0]
            
            # Get PDF fields with error handling
            try:
                document['pdf_fields'] = self.get_document_fields(document_id)
            except Exception as e:
                print(f"Error loading fields for document {document_id}: {e}")
                document['pdf_fields'] = []  # Fallback to empty list
            
            return document
        except Exception as e:
            print(f"Database error in get_document for document {document_id}: {e}")
            return None
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents"""
        try:
            result = self.supabase.table('documents').select('*').order('created_at', desc=True).execute()
            
            if not result.data:
                return []
            
            documents = result.data
            
            # Add PDF fields to each document
            for document in documents:
                try:
                    document['pdf_fields'] = self.get_document_fields(document['id'])
                except Exception as e:
                    print(f"Error loading fields for document {document['id']}: {e}")
                    document['pdf_fields'] = []  # Fallback to empty list
            
            return documents
        except Exception as e:
            print(f"Database error in get_all_documents: {e}")
            # Return empty list on database error
            return []
    
    def update_document(self, document_id: str, updates: Dict[str, Any]) -> bool:
        """Update a document"""
        try:
            updates['updated_at'] = datetime.now().isoformat()
            
            result = self.supabase.table('documents').update(updates).eq('id', document_id).execute()
            
            # Log the update
            self.log_action(document_id, 'system', 'document_updated', 
                           f"Document updated: {list(updates.keys())}")
            
            return len(result.data) > 0
        except Exception as e:
            print(f"Database error in update_document for document {document_id}: {e}")
            return False
    
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
        try:
            result = self.supabase.table('pdf_fields').select('*').eq('document_id', document_id).order('page_number').order('position_y').execute()
            
            if not result.data:
                return []
            
            fields = []
            for field in result.data:
                try:
                    # Reconstruct position object
                    field['position'] = {
                        'x': field.get('position_x', 0),
                        'y': field.get('position_y', 0),
                        'width': field.get('width', 0),
                        'height': field.get('height', 0)
                    }
                    # Clean up individual position fields for API compatibility
                    field['name'] = field.get('field_name', '')
                    field['type'] = field.get('field_type', 'text')
                    field['value'] = field.get('field_value', '')
                    field['page'] = field.get('page_number', 0)
                    
                    fields.append(field)
                except Exception as e:
                    print(f"Error processing field {field.get('id', 'unknown')}: {e}")
                    # Skip malformed fields but continue processing others
                    continue
            
            return fields
        except Exception as e:
            print(f"Database error in get_document_fields for document {document_id}: {e}")
            # Return empty list on database error
            return []
    
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