#!/usr/bin/env python3
"""
Optional Supabase API client for advanced features
This complements the SQLAlchemy database integration
"""

import os
from supabase import create_client, Client
from config import Config
from typing import Optional, Dict, Any, List
import json

class SupabaseAPI:
    """
    Supabase API client for advanced features like:
    - File storage for PDF uploads
    - Real-time subscriptions
    - Authentication integration
    - Direct API access
    """
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.initialize()
    
    def initialize(self):
        """Initialize Supabase client"""
        try:
            if Config.SUPABASE_URL and Config.SUPABASE_ANON_KEY:
                self.supabase = create_client(
                    Config.SUPABASE_URL,
                    Config.SUPABASE_ANON_KEY
                )
                print("✅ Supabase API client initialized")
            else:
                print("⚠️  Supabase API credentials not found in config")
        except Exception as e:
            print(f"❌ Failed to initialize Supabase API client: {e}")
    
    def is_available(self) -> bool:
        """Check if Supabase API client is available"""
        return self.supabase is not None
    
    def upload_pdf(self, file_path: str, bucket_name: str = "pdfs") -> Optional[str]:
        """
        Upload PDF file to Supabase Storage
        Returns the public URL if successful
        """
        if not self.is_available():
            return None
        
        try:
            with open(file_path, 'rb') as f:
                file_name = os.path.basename(file_path)
                
                # Upload file
                response = self.supabase.storage.from_(bucket_name).upload(
                    path=file_name,
                    file=f,
                    file_options={"content-type": "application/pdf"}
                )
                
                if response:
                    # Get public URL
                    public_url = self.supabase.storage.from_(bucket_name).get_public_url(file_name)
                    print(f"✅ PDF uploaded to Supabase Storage: {public_url}")
                    return public_url
                
        except Exception as e:
            print(f"❌ Failed to upload PDF: {e}")
        
        return None
    
    def download_pdf(self, file_name: str, bucket_name: str = "pdfs") -> Optional[bytes]:
        """Download PDF file from Supabase Storage"""
        if not self.is_available():
            return None
        
        try:
            response = self.supabase.storage.from_(bucket_name).download(file_name)
            return response
        except Exception as e:
            print(f"❌ Failed to download PDF: {e}")
            return None
    
    def delete_pdf(self, file_name: str, bucket_name: str = "pdfs") -> bool:
        """Delete PDF file from Supabase Storage"""
        if not self.is_available():
            return False
        
        try:
            response = self.supabase.storage.from_(bucket_name).remove([file_name])
            return response is not None
        except Exception as e:
            print(f"❌ Failed to delete PDF: {e}")
            return False
    
    def get_user_documents(self, user_id: int) -> List[Dict[str, Any]]:
        """Get documents for a specific user using direct API access"""
        if not self.is_available():
            return []
        
        try:
            response = self.supabase.table('documents').select('*').eq('created_by_id', user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Failed to get user documents: {e}")
            return []
    
    def subscribe_to_document_changes(self, document_id: str, callback):
        """Subscribe to real-time changes for a document"""
        if not self.is_available():
            return None
        
        try:
            # Set up real-time subscription
            subscription = self.supabase.table('document_fields').on(
                'UPDATE',
                callback
            ).filter('document_id', 'eq', document_id).subscribe()
            
            print(f"📡 Subscribed to changes for document: {document_id}")
            return subscription
        except Exception as e:
            print(f"❌ Failed to subscribe to document changes: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test the Supabase API connection"""
        if not self.is_available():
            return False
        
        try:
            # Try to fetch a simple query
            response = self.supabase.table('users').select('count').execute()
            print("✅ Supabase API connection test successful")
            return True
        except Exception as e:
            print(f"❌ Supabase API connection test failed: {e}")
            return False

# Global instance
supabase_api = SupabaseAPI()

def get_supabase_api() -> SupabaseAPI:
    """Get the global Supabase API instance"""
    return supabase_api