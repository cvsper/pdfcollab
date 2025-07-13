#!/usr/bin/env python3
"""
Test dwelling type checkbox filling specifically
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_dwelling_fix():
    """Test that dwelling type checkboxes are properly filled"""
    
    print("🏠 TESTING DWELLING TYPE CHECKBOX FIX")
    print("=" * 60)
    
    # Test data with all dwelling types
    test_cases = [
        ('single_family', 'Single Family Home (Checkbox)', 'dwelling_single_fam1'),
        ('apartment', 'Apartment (Checkbox)', 'dwelling_apt1'),
        ('condominium', 'Condominium (Checkbox)', 'dwelling_condo1')
    ]
    
    for dwelling_value, display_name, pdf_field_name in test_cases:
        print(f"\n🧪 Testing {dwelling_value} → {pdf_field_name}")
        
        # Create test document
        test_document = {
            'id': str(uuid.uuid4()),
            'pdf_fields': [],
            'user1_data': {
                'property_address': '123 Test Street',
                'dwelling_type': dwelling_value,  # This is the key field
                'first_name': 'John',
                'last_name': 'Doe'
            },
            'user2_data': {
                'applicant_signature': 'John Doe',
                'authorization_date': '2025-07-13'
            }
        }
        
        # Extract PDF fields
        processor = PDFProcessor()
        pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
        pdf_fields = pdf_analysis['fields']
        
        print(f"📋 Extracted {len(pdf_fields)} PDF fields")
        
        # Find the dwelling checkbox field
        dwelling_field = None
        for field in pdf_fields:
            if field['name'] == display_name:
                dwelling_field = field
                break
        
        if not dwelling_field:
            print(f"❌ Could not find field: {display_name}")
            continue
            
        print(f"✅ Found dwelling field: {display_name}")
        print(f"   PDF field name: {dwelling_field.get('pdf_field_name', 'N/A')}")
        print(f"   Field type: {dwelling_field.get('type', 'N/A')}")
        
        # Set the value directly on the field
        dwelling_field['value'] = 'true'
        dwelling_field['assigned_to'] = 'user1'
        
        # Add basic property address mapping
        for field in pdf_fields:
            if field['name'] == 'Property Address':
                field['value'] = test_document['user1_data']['property_address']
                field['assigned_to'] = 'user1'
                break
                
        # Add signature mapping
        for field in pdf_fields:
            if field['name'] == 'Applicant Signature':
                field['value'] = test_document['user2_data']['applicant_signature']
                field['assigned_to'] = 'user2'
                field['type'] = 'signature'
                break
        
        # Update document with fields
        test_document['pdf_fields'] = pdf_fields
        
        # Generate test PDF
        output_file = f'DWELLING_TEST_{dwelling_value.upper()}.pdf'
        success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
        
        if success:
            print(f"✅ Test PDF created: {output_file}")
            
            # Count filled fields
            filled_count = sum(1 for f in pdf_fields if f.get('value'))
            print(f"📊 Filled {filled_count} fields")
            
        else:
            print(f"❌ Failed to create PDF for {dwelling_value}")
    
    print(f"\n🎯 All dwelling type tests completed!")
    return True

if __name__ == "__main__":
    test_dwelling_fix()