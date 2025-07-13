#\!/usr/bin/env python3
"""
Test the exact workflow that happens when a user submits the form
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def test_real_workflow():
    print("🔄 TESTING REAL USER WORKFLOW - DWELLING TYPES")
    print("=" * 60)
    
    # Step 1: Simulate form submission
    form_data = {
        'property_address': '456 Real Workflow Test Street',
        'apartment_number': 'Unit 3B',
        'city': 'Hartford',
        'state': 'CT', 
        'zip_code': '06103',
        'apartments_count': '15',
        'dwelling_type': 'apartment',  # Key field we're testing
        'first_name': 'John',
        'last_name': 'Smith', 
        'telephone': '860-555-1234',
        'email': 'john.smith@test.com'
    }
    
    print(f"📝 User submits dwelling_type: '{form_data['dwelling_type']}'")
    
    # Step 2: Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    
    if "error" in pdf_analysis:
        print(f"❌ Error: {pdf_analysis['error']}")
        return False
    
    pdf_fields = pdf_analysis['fields']
    print(f"🔍 Found {len(pdf_fields)} PDF fields")
    
    # Step 3: Apply dwelling type logic
    dwelling_type = form_data.get('dwelling_type')
    dwelling_mappings = {
        'single_family': 'Single Family Home (Checkbox)',
        'apartment': 'Apartment (Checkbox)', 
        'condominium': 'Condominium (Checkbox)'
    }
    
    target_field_name = dwelling_mappings.get(dwelling_type)
    print(f"🏠 Looking for: '{target_field_name}'")
    
    dwelling_matched = False
    for field in pdf_fields:
        if field['name'] == target_field_name:
            field['value'] = 'true'
            field['assigned_to'] = 'user1'
            dwelling_matched = True
            print(f"   ✅ Found and set: {field['name']}")
            break
    
    if not dwelling_matched:
        print(f"   ❌ Field '{target_field_name}' not found\!")
        return False
    
    # Step 4: Fill PDF
    test_document = {
        'id': 'workflow_test',
        'pdf_fields': [f for f in pdf_fields if f.get('value')]
    }
    
    success = processor.fill_pdf_with_pymupdf('homworks.pdf', test_document, 'WORKFLOW_TEST.pdf')
    
    if success:
        print("✅ PDF created successfully")
        
        # Verify result
        import fitz
        doc = fitz.open('WORKFLOW_TEST.pdf')
        page = doc[2]
        
        for widget in list(page.widgets()):
            if widget.field_name == 'dwelling_apt1':  # apartment checkbox
                value = widget.field_value
                is_checked = value and str(value) not in ['', 'False', 'Off']
                print(f"🔍 dwelling_apt1: {value} ({'CHECKED' if is_checked else 'NOT CHECKED'})")
                doc.close()
                return is_checked
        
        doc.close()
        print("❌ dwelling_apt1 field not found in PDF")
        return False
    else:
        print("❌ PDF creation failed")
        return False

if __name__ == "__main__":
    success = test_real_workflow()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
EOF < /dev/null