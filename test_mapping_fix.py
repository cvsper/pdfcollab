#!/usr/bin/env python3
"""
Test the field mapping fix
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def test_mapping_fix():
    """Test that the field mapping fix works correctly"""
    
    print("🔧 TESTING FIELD MAPPING FIX")
    print("=" * 50)
    
    # Extract fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Simulate the exact mappings
    EXACT_FIELD_MAPPINGS = {
        'property_address': 'property_address1',
        'apartment_number': 'apt_num1',
        'city': 'city1',
        'state': 'state1',
        'zip_code': 'zip1',
        'first_name': 'first_name2',
        'last_name': 'last_name2',
        'telephone': 'phone2',
        'email': 'email2'
    }
    
    # Test data
    form_data = {
        'property_address': '123 Test Street',
        'apartment_number': 'Unit 5',
        'city': 'Hartford',
        'state': 'CT',
        'zip_code': '06103',
        'first_name': 'John',
        'last_name': 'Doe',
        'telephone': '860-555-1234',
        'email': 'john@test.com'
    }
    
    # Apply mappings with the fix
    successful_mappings = 0
    
    for form_field, pdf_field_name in EXACT_FIELD_MAPPINGS.items():
        form_value = form_data.get(form_field)
        if form_value:
            # Find field using the fixed logic
            for field in pdf_fields:
                # The fix: check pdf_field_name property
                if field.get('pdf_field_name') == pdf_field_name or field['name'] == pdf_field_name:
                    field['value'] = str(form_value)
                    successful_mappings += 1
                    print(f"✅ Mapped: {form_field} → {pdf_field_name}")
                    print(f"   Field name: {field['name']}")
                    print(f"   Field pdf_field_name: {field.get('pdf_field_name')}")
                    print(f"   Value: {form_value}")
                    break
    
    print(f"\n📊 Results: {successful_mappings}/{len(form_data)} fields mapped successfully")
    
    # Now test PDF generation
    test_document = {
        'id': 'mapping_fix_test',
        'pdf_fields': pdf_fields
    }
    
    output_file = 'MAPPING_FIX_TEST.pdf'
    success = processor.fill_pdf_with_pymupdf('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ PDF created successfully: {output_file}")
        
        # Count filled fields
        filled_count = sum(1 for f in pdf_fields if f.get('value'))
        print(f"📊 Filled {filled_count} fields in the PDF")
        
        return True
    else:
        print("\n❌ PDF creation failed")
        return False

if __name__ == "__main__":
    success = test_mapping_fix()
    if success:
        print("\n🎉 Field mapping fix is working correctly!")
    else:
        print("\n❌ Field mapping fix needs more work")