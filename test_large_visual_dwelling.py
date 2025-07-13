#!/usr/bin/env python3
"""
Test the large visual dwelling indicators
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_large_visual_dwelling():
    """Test the large visual dwelling indicators"""
    
    print("🎯 TESTING LARGE VISUAL DWELLING INDICATORS")
    print("=" * 60)
    print("Creating PDF with LARGE and HIGH visual indicators")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Test data
    form_data = {
        'property_address': 'LARGE VISUAL TEST - 777 High Visibility Avenue',
        'dwelling_type': 'apartment',  # This will trigger LARGE visual indicators
        'first_name': 'LARGE',
        'last_name': 'VISUAL'
    }
    
    print(f"📝 Testing dwelling_type: {form_data['dwelling_type']}")
    print(f"🎯 Expected: LARGE visual indicators above and around apartment checkbox")
    
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
                    print(f"✅ Mapped: {form_field} → {field['name']}")
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
                    print(f"✅ Dwelling: {dwelling_type} → {field['name']} = true")
                    break
    
    # Create test document
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': pdf_fields,
        'user1_data': form_data,  # This triggers the visual indicators
        'user2_data': {}
    }
    
    # Generate PDF with LARGE visual indicators
    output_file = 'LARGE_VISUAL_DWELLING_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ LARGE visual dwelling PDF created: {output_file}")
        
        print(f"\n🎯 WHAT YOU SHOULD NOW SEE:")
        print(f"   📍 Location: Page 3, around coordinates (41, 268)")
        print(f"   🔴 LARGE red circle (4x bigger) around apartment checkbox") 
        print(f"   🟡 LARGE yellow highlight rectangle extending much wider")
        print(f"   📝 Text '>>> APARTMENT SELECTED <<<' ABOVE the checkbox")
        print(f"   ➡️  Red arrow pointing TO the checkbox")
        print(f"   📏 All indicators are much LARGER and HIGHER than before")
        
        print(f"\n📖 INSTRUCTIONS:")
        print(f"   1. Open '{output_file}' in your PDF viewer")
        print(f"   2. Go to page 3")
        print(f"   3. Look for the dwelling type section")
        print(f"   4. The apartment selection should be IMPOSSIBLE to miss now!")
        
        return True
    else:
        print(f"❌ Failed to create large visual dwelling PDF")
        return False

if __name__ == "__main__":
    success = test_large_visual_dwelling()
    if success:
        print("\n🎉 LARGE VISUAL DWELLING TEST COMPLETE!")
        print("📍 The dwelling selection should now be MUCH more visible and higher!")
    else:
        print("\n❌ Large visual dwelling test failed!")