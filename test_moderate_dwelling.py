#!/usr/bin/env python3
"""
Test dwelling indicators at moderate height and narrow width
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_moderate_dwelling():
    """Test dwelling indicators at y=650 and w=80 (lower and narrower)"""
    
    print("📏 TESTING MODERATE HEIGHT AND NARROW WIDTH")
    print("=" * 60)
    print("Using y=650 (lower) and w=80 (narrower)")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Test data
    form_data = {
        'property_address': 'MODERATE TEST - 555 Medium Street',
        'dwelling_type': 'apartment',
        'first_name': 'MODERATE',
        'last_name': 'SIZE'
    }
    
    print(f"📝 Testing dwelling_type: {form_data['dwelling_type']}")
    print(f"📏 Position: y=650 (lower than 750), w=80 (narrower than 120)")
    
    # Apply basic mappings
    basic_mappings = {
        'property_address': 'property_address1',
        'first_name': 'first_name2',
        'last_name': 'last_name2'
    }
    
    for form_field, pdf_field_name in basic_mappings.items():
        form_value = form_data.get(form_field)
        if form_value:
            for field in pdf_fields:
                if field.get('pdf_field_name') == pdf_field_name or field['name'] == pdf_field_name:
                    field['value'] = str(form_value)
                    field['assigned_to'] = 'user1'
                    break
    
    # Handle dwelling_type specially
    dwelling_type = form_data.get('dwelling_type')
    if dwelling_type:
        dwelling_mappings = {
            'single_family': 'Single Family Home (Checkbox)',
            'apartment': 'Apartment (Checkbox)', 
            'condominium': 'Condominium (Checkbox)'
        }
        target_field = dwelling_mappings.get(dwelling_type)
        
        if target_field:
            for field in pdf_fields:
                if field['name'] == target_field:
                    field['value'] = 'true'
                    field['assigned_to'] = 'user1'
                    break
    
    # Create test document
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': pdf_fields,
        'user1_data': form_data,
        'user2_data': {}
    }
    
    # Generate PDF
    output_file = 'MODERATE_DWELLING_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ Moderate dwelling PDF created: {output_file}")
        print(f"📏 Position: x=250, y=650, w=80, h=12")
        return True
    else:
        print(f"❌ Failed to create moderate dwelling PDF")
        return False

if __name__ == "__main__":
    test_moderate_dwelling()