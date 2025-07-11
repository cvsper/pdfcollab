#!/usr/bin/env python3
"""
Debug script to trace signature data flow from user input to PDF generation
This simulates the exact download process to identify where signatures are lost
"""

import os
import sys
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def debug_signature_flow():
    """Debug the complete signature flow that happens during download"""
    
    print("🔍 DEBUGGING SIGNATURE FLOW IN DOWNLOAD PROCESS")
    print("=" * 60)
    
    try:
        from pdf_processor import PDFProcessor
        
        # Step 1: Create a document structure that mimics what's stored in the database
        print("📋 Step 1: Creating document structure (simulating database data)")
        
        # This simulates what gets stored in the database after User 1 and User 2 fill their forms
        document = {
            'id': 'test_doc_123',
            'name': 'Test Document',
            'file_path': os.path.join(os.path.dirname(__file__), 'homworks.pdf'),
            
            # User 1 data (from initial form submission)
            'user1_data': {
                'first_name': 'John',
                'last_name': 'Smith', 
                'property_address': '123 Test Street'
            },
            
            # User 2 data (from authorization form submission)
            'user2_data': {
                'applicant_signature': 'John Smith Signature',
                'authorization_date': '2025-07-11',
                'owner_signature': 'Jane Property Owner',
                'owner_signature_date': '2025-07-11'
            },
            
            # PDF fields (extracted and mapped)
            'pdf_fields': []
        }
        
        # Step 2: Extract PDF fields (simulating field extraction process)
        print("📋 Step 2: Extracting PDF fields...")
        processor = PDFProcessor()
        field_extraction = processor.extract_fields_with_pymupdf(document['file_path'])
        
        if 'error' in field_extraction:
            print(f"❌ Error extracting fields: {field_extraction['error']}")
            return False
            
        pdf_fields = field_extraction.get('fields', [])
        print(f"✅ Extracted {len(pdf_fields)} PDF fields")
        
        # Step 3: Apply field mapping (simulating User 1 form submission mapping)
        print("📋 Step 3: Applying field mapping...")
        mapped_fields = 0
        
        for field in pdf_fields:
            field['assigned_to'] = None
            field['value'] = ''
            
            # Map basic fields
            if field['name'] == 'Property Address':
                field['value'] = document['user1_data']['property_address']
                field['assigned_to'] = 'user1'
                mapped_fields += 1
            elif field['name'] == 'First Name':
                field['value'] = document['user1_data']['first_name'] 
                field['assigned_to'] = 'user1'
                mapped_fields += 1
            elif field['name'] == 'Last Name':
                field['value'] = document['user1_data']['last_name']
                field['assigned_to'] = 'user1'
                mapped_fields += 1
        
        print(f"✅ Mapped {mapped_fields} basic fields")
        
        # Step 4: Apply User 2 signature mapping (simulating User 2 form submission)
        print("📋 Step 4: Applying User 2 signature mapping...")
        signature_fields_mapped = 0
        
        for field in pdf_fields:
            if field.get('type') == 'signature':
                field_name = field.get('name', '')
                # CRITICAL: Ensure pdf_field_name is set for PDF processor to find the field
                field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                field['assigned_to'] = 'user2'
                
                # Map Applicant Signature field
                if 'Applicant' in field_name and document['user2_data'].get('applicant_signature'):
                    field['value'] = document['user2_data']['applicant_signature']
                    signature_fields_mapped += 1
                    print(f"🖋️  Mapped Applicant signature: '{field['name']}' -> '{field['value']}'")
                    print(f"    pdf_field_name: '{field['pdf_field_name']}'")
                    print(f"    type: '{field['type']}'")
                    print(f"    assigned_to: '{field['assigned_to']}'")
                
                # Map Property Owner Signature field  
                elif 'Property Owner' in field_name and document['user2_data'].get('owner_signature'):
                    field['value'] = document['user2_data']['owner_signature']
                    signature_fields_mapped += 1
                    print(f"🖋️  Mapped Property Owner signature: '{field['name']}' -> '{field['value']}'")
                    print(f"    pdf_field_name: '{field['pdf_field_name']}'")
                    print(f"    type: '{field['type']}'")
                    print(f"    assigned_to: '{field['assigned_to']}'")
                
                else:
                    print(f"⚠️  Signature field '{field_name}' found but no matching signature data")
        
        print(f"✅ Mapped {signature_fields_mapped} signature fields")
        
        # Step 5: Store mapped fields in document
        document['pdf_fields'] = pdf_fields
        
        # Step 6: Generate PDF using the same method as download (force visible)
        print("📋 Step 5: Generating PDF using download method...")
        output_path = os.path.join(os.path.dirname(__file__), 'DEBUG_DOWNLOAD_SIGNATURES.pdf')
        
        success = processor.fill_pdf_with_force_visible(document['file_path'], document, output_path)
        
        if success:
            print(f"✅ DEBUG PDF CREATED: {output_path}")
            file_size = os.path.getsize(output_path)
            print(f"📊 File size: {file_size:,} bytes")
            
            # Step 7: Analyze what was actually processed
            print("\n📋 Step 6: Analysis of PDF generation...")
            print("Signature fields that should have been processed:")
            
            signature_count = 0
            for field in pdf_fields:
                if field.get('type') == 'signature' and field.get('value'):
                    signature_count += 1
                    print(f"  ✅ Field: '{field['name']}'")
                    print(f"     Value: '{field['value']}'")
                    print(f"     PDF Field Name: '{field.get('pdf_field_name', 'NOT SET')}'")
                    print(f"     Type: '{field['type']}'")
                    print(f"     Assigned To: '{field.get('assigned_to', 'NOT SET')}'")
                    print()
            
            print(f"📊 Total signature fields with values: {signature_count}")
            
            if signature_count == 0:
                print("❌ NO SIGNATURE FIELDS FOUND WITH VALUES!")
                print("This indicates the mapping process failed.")
            else:
                print("✅ Signature fields are properly mapped.")
                print("If signatures don't appear in the PDF, the issue is in the PDF processor.")
            
            return True
        else:
            print("❌ Failed to generate debug PDF")
            return False
            
    except Exception as e:
        print(f"❌ Error in debug process: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Download Signature Debug")
    print("Debugging why signatures don't appear in downloaded PDFs")
    print()
    
    success = debug_signature_flow()
    
    print(f"\n📊 DEBUG RESULTS:")
    print(f"   Debug process: {'✅ COMPLETED' if success else '❌ FAILED'}")
    
    if success:
        print(f"\n🎯 DEBUG FILE CREATED:")
        print(f"   📄 DEBUG_DOWNLOAD_SIGNATURES.pdf")
        print(f"   💡 This simulates the exact download process")
        print(f"   🔍 Check if signatures appear in this file")
        print(f"   📋 Review the mapping analysis above")

if __name__ == "__main__":
    main()