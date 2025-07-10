#!/usr/bin/env python3
"""
Script to upload the homworks.pdf file as a template document to the database.
Run this once to set up the template in production.
"""

import os
from supabase_client import SupabaseManager

def upload_template():
    """Upload homworks.pdf as a template document"""
    try:
        # Initialize database connection
        db = SupabaseManager()
        print("✅ Connected to Supabase database")
        
        # Check if template already exists
        templates = db.get_active_templates()
        for template in templates:
            if template['filename'] == 'homworks.pdf':
                print(f"⚠️  Template 'homworks.pdf' already exists (ID: {template['id']})")
                return template['id']
        
        # Upload the template
        template_path = os.path.join(os.getcwd(), 'homworks.pdf')
        
        if not os.path.exists(template_path):
            print(f"❌ File not found: {template_path}")
            return None
        
        template_id = db.upload_template_document(
            name="Default Employment Form",
            description="Standard employment form with sections for employee information, qualification details, and zero income affidavit",
            file_path=template_path
        )
        
        if template_id:
            print(f"✅ Template uploaded successfully!")
            print(f"   📋 Template ID: {template_id}")
            print(f"   📄 File: homworks.pdf")
            print(f"   📊 Name: Default Employment Form")
            return template_id
        else:
            print("❌ Failed to upload template")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading template: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Uploading template document to database...")
    template_id = upload_template()
    
    if template_id:
        print(f"\n✅ Template upload complete!")
        print(f"The application will now use this template instead of requiring file uploads.")
        print(f"Template ID: {template_id}")
    else:
        print(f"\n❌ Template upload failed!")
        print(f"Make sure SUPABASE_URL and SUPABASE_ANON_KEY are set in your environment.")