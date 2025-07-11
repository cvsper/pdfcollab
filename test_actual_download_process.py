#!/usr/bin/env python3
"""
Test the EXACT download process by simulating the generate_completed_pdf function
This will help us identify where signatures are being lost in the actual download flow
"""

import os
import sys
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_exact_download_process():
    """Test the exact same process that happens during download"""
    
    print("🔍 TESTING EXACT DOWNLOAD PROCESS")
    print("=" * 60)
    
    try:
        from pdf_processor import PDFProcessor
        
        # Create a realistic document structure exactly like what's in the database
        document = {
            'id': 'test_download_123',
            'name': 'Connecticut Home Energy Solutions Form',
            'file_path': os.path.join(os.path.dirname(__file__), 'homworks.pdf'),
            'created_by': 'user1@test.com',
            
            # User 1 data
            'user1_data': {
                'first_name': 'John',
                'last_name': 'Smith', 
                'property_address': '123 Main Street',
                'city': 'Hartford',
                'state': 'CT',
                'zip_code': '06101'
            },
            
            # User 2 data (this is what gets saved when User 2 submits the form)
            'user2_data': {
                'applicant_signature': 'John Smith Digital Signature',
                'authorization_date': '2025-07-11',
                'owner_signature': 'Jane Property Owner Signature', 
                'owner_signature_date': '2025-07-11',
                'manager': 'Property Manager Name',
                'hr_rep': 'HR Representative',
                'benefits': 'Energy Benefits Info',
                'notes': 'Additional notes here'
            },
            
            # PDF fields (this gets populated during field extraction and mapping)
            'pdf_fields': []
        }
        
        # Step 1: Simulate the generate_completed_pdf function
        print("📋 Step 1: Simulating generate_completed_pdf function...")
        
        pdf_processor = PDFProcessor()
        
        # This is the exact path from app.py generate_completed_pdf function
        output_filename = f"completed_{document['id']}_{document['name']}.pdf"
        output_path = os.path.join(os.path.dirname(__file__), 'TEST_ACTUAL_DOWNLOAD.pdf')
        print(f"📁 Output path: {output_path}")
        
        # Try Force Visible method first (this is what the download route does)
        print("🔧 Attempting to fill original PDF with FORCE VISIBLE method...")
        success = pdf_processor.fill_pdf_with_force_visible(document['file_path'], document, output_path)
        
        if success:
            print(f"✅ Successfully filled original PDF with FORCE VISIBLE method: {output_path}")
            file_size = os.path.getsize(output_path)
            print(f"📊 File size: {file_size:,} bytes")
            
            # Let's check what actually got processed
            print("\n🔍 ANALYZING WHAT WAS PROCESSED...")
            
            # Check if document has pdf_fields populated
            if document.get('pdf_fields'):
                signature_fields = [f for f in document['pdf_fields'] if f.get('type') == 'signature' and f.get('value')]
                print(f"📊 Found {len(signature_fields)} signature fields with values in document:")
                for field in signature_fields:
                    print(f"  ✅ {field['name']}: '{field['value']}' (pdf_field: {field.get('pdf_field_name', 'NOT SET')})")
            else:
                print("⚠️  No pdf_fields found in document structure!")
                print("This might be why signatures aren't appearing.")
            
            # Check user2_data
            if document.get('user2_data'):
                user2_data = document['user2_data']
                print(f"\n📊 User2 data contains:")
                print(f"  applicant_signature: '{user2_data.get('applicant_signature', 'NOT SET')}'")
                print(f"  owner_signature: '{user2_data.get('owner_signature', 'NOT SET')}'")
            else:
                print("⚠️  No user2_data found!")
                
            return True
        else:
            print("❌ Force visible method failed, trying fallbacks...")
            
            # Try the fallback methods (this is what happens if force visible fails)
            print("🔧 Attempting legacy method...")
            
            # We don't have access to fill_pdf_fields_advanced, so try overlay method
            print("🔧 Attempting overlay method...")
            
            # Extract fields first
            field_extraction = pdf_processor.extract_fields_with_pymupdf(document['file_path'])
            if 'error' not in field_extraction:
                pdf_fields = field_extraction.get('fields', [])
                
                # Map signature fields
                for field in pdf_fields:
                    if field.get('type') == 'signature':
                        field['assigned_to'] = 'user2'
                        field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                        
                        if 'Applicant' in field.get('name', '') and document['user2_data'].get('applicant_signature'):
                            field['value'] = document['user2_data']['applicant_signature']
                        elif 'Property Owner' in field.get('name', '') and document['user2_data'].get('owner_signature'):
                            field['value'] = document['user2_data']['owner_signature']
                
                overlay_success = pdf_processor.create_overlay_pdf(document['file_path'], pdf_fields, output_path)
                if overlay_success:
                    print(f"✅ Successfully created overlay PDF: {output_path}")
                    return True
            
            print("❌ All methods failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in download process test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Exact Download Process Test")
    print("Testing the exact same process that happens during PDF download")
    print()
    
    success = test_exact_download_process()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"   Download process test: {'✅ COMPLETED' if success else '❌ FAILED'}")
    
    if success:
        print(f"\n🎯 TEST FILE CREATED:")
        print(f"   📄 TEST_ACTUAL_DOWNLOAD.pdf")
        print(f"   💡 This uses the exact same process as real downloads")
        print(f"   🔍 Check if signatures appear in this file")
        print(f"   📋 If signatures don't appear here, the issue is in the PDF processor")

if __name__ == "__main__":
    main()