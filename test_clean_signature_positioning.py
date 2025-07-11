#!/usr/bin/env python3
"""
Test clean signature positioning without debug boxes
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def create_clean_signature_test():
    """Create a clean test PDF with signatures positioned correctly without debug boxes"""
    
    print("🧪 CREATING CLEAN SIGNATURE POSITIONING TEST")
    print("=" * 60)
    
    try:
        from pdf_processor import PDFProcessor
        
        homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        processor = PDFProcessor()
        
        # Test data
        test_user1_data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'property_address': '123 Main Street'
        }
        
        test_user2_data = {
            'name': 'John Smith',
            'email': 'john.smith@email.com',
            'applicant_signature': 'John Smith',
            'authorization_date': '2025-07-11',
            'owner_signature': 'Jane Smith',
            'owner_signature_date': '2025-07-11'
        }
        
        # Extract and map fields
        field_analysis = processor.extract_fields_with_pymupdf(homeworks_path)
        if "error" in field_analysis:
            print(f"❌ Error: {field_analysis['error']}")
            return False
        
        pdf_fields = field_analysis.get('fields', [])
        
        # Apply field mapping
        for field in pdf_fields:
            field['assigned_to'] = 'user1'
            field['value'] = ''
            field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
            
            if field['name'] == 'Applicant Signature':
                field['value'] = test_user2_data['applicant_signature']
                field['type'] = 'signature'
                field['assigned_to'] = 'user2'
            elif field['name'] == 'Property Owner Signature':
                field['value'] = test_user2_data['owner_signature']
                field['type'] = 'signature'
                field['assigned_to'] = 'user2'
            elif field['name'] == 'First Name':
                field['value'] = test_user1_data['first_name']
            elif field['name'] == 'Last Name':
                field['value'] = test_user1_data['last_name']
            elif field['name'] == 'Property Address':
                field['value'] = test_user1_data['property_address']
        
        # Create document structure
        document = {
            'user1_data': test_user1_data,
            'user2_data': test_user2_data,
            'pdf_fields': pdf_fields,
            'file_path': homeworks_path
        }
        
        # Generate the clean test PDF
        output_path = os.path.join(os.path.dirname(__file__), 'CLEAN_SIGNATURE_POSITIONING_TEST.pdf')
        
        print(f"🔧 Generating clean signature positioning test...")
        success = processor.fill_pdf_with_force_visible(homeworks_path, document, output_path)
        
        if success:
            print(f"\n🎉 CLEAN SIGNATURE TEST CREATED!")
            print(f"✅ File: {output_path}")
            print(f"📄 Size: {os.path.getsize(output_path):,} bytes")
            
            print(f"\n📝 TEST CONTENTS:")
            print(f"   • Applicant Signature: '{test_user2_data['applicant_signature']}'")
            print(f"   • Property Owner Signature: '{test_user2_data['owner_signature']}'")
            print(f"   • First Name: '{test_user1_data['first_name']}'")
            print(f"   • Last Name: '{test_user1_data['last_name']}'")
            print(f"   • Property Address: '{test_user1_data['property_address']}'")
            
            print(f"\n🔍 WHAT TO VERIFY:")
            print(f"   ✅ Signatures appear in correct form fields")
            print(f"   ✅ Signatures are right-side up (not upside down)")
            print(f"   ✅ Signatures are readable (not backwards)")
            print(f"   ✅ Signatures are positioned properly within fields")
            
            return True
        else:
            print(f"❌ Failed to create clean signature test")
            return False
            
    except Exception as e:
        print(f"❌ Error creating clean signature test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Clean Signature Positioning Test")
    print("Creating a clean test PDF without debug boxes")
    print()
    
    success = create_clean_signature_test()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"   Clean signature test: {'✅ CREATED' if success else '❌ FAILED'}")
    
    if success:
        print(f"\n🎯 FILE CREATED:")
        print(f"   📄 CLEAN_SIGNATURE_POSITIONING_TEST.pdf")
        print(f"   💡 This shows signatures positioned correctly without any debug boxes")

if __name__ == "__main__":
    main()