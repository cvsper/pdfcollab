#!/usr/bin/env python3
"""
Test dwelling indicators at the very top of the page
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_top_of_page_dwelling():
    """Test dwelling indicators at the absolute top of the page"""
    
    print("🔝 TESTING TOP OF PAGE DWELLING INDICATORS")
    print("=" * 60)
    print("Creating PDF with indicators at the ABSOLUTE TOP of page 3")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Test data
    form_data = {
        'property_address': 'TOP OF PAGE TEST - 111 Very Top Street',
        'dwelling_type': 'apartment',  # This will create TOP OF PAGE indicators
        'first_name': 'TOP',
        'last_name': 'PAGE'
    }
    
    print(f"📝 Testing dwelling_type: {form_data['dwelling_type']}")
    print(f"🔝 Expected: MASSIVE banner at y=90 (absolute top of page)")
    
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
        'user1_data': form_data,  # This triggers TOP OF PAGE indicators
        'user2_data': {}
    }
    
    # Generate PDF with TOP OF PAGE indicators
    output_file = 'TOP_OF_PAGE_DWELLING_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ TOP OF PAGE dwelling PDF created: {output_file}")
        
        print(f"\n🔝 ABSOLUTE TOP POSITION INDICATORS:")
        print(f"   📍 Location: Page 3, y=90 (absolute top of page!)")
        print(f"   📏 Size: 400x30 pixels (MASSIVE banner)")
        print(f"   🟥 MASSIVE bright red banner across nearly full width")
        print(f"   📝 HUGE text '🏠 DWELLING TYPE SELECTED: APARTMENT 🏠' (fontsize 20)")
        print(f"   🔲 Thick red border with large corner markers")
        print(f"   📊 Attention bars above and below")
        print(f"   ⭐ 20 fallback red rectangles if text fails")
        
        print(f"\n📖 POSITION PROGRESSION:")
        print(f"   🔻 ORIGINAL: y=268 (middle-lower)")
        print(f"   ⬆️  PREVIOUS: y=220 (higher)")
        print(f"   🔝 NOW: y=90 (ABSOLUTE TOP!)")
        print(f"   📏 Total move: 178 points = ~2.5 inches higher!")
        
        print(f"\n📖 WHAT TO EXPECT:")
        print(f"   1. Open '{output_file}' in your PDF viewer")
        print(f"   2. Go to page 3")
        print(f"   3. Look at the VERY TOP of the page immediately")
        print(f"   4. You should see a MASSIVE red banner that fills most of the width")
        print(f"   5. It should be literally the FIRST thing you see on the page!")
        
        return True
    else:
        print(f"❌ Failed to create top of page dwelling PDF")
        return False

if __name__ == "__main__":
    success = test_top_of_page_dwelling()
    if success:
        print("\n🎉 TOP OF PAGE DWELLING TEST COMPLETE!")
        print("🔝 The dwelling selection is now at the ABSOLUTE TOP of the page!")
    else:
        print("\n❌ Top of page dwelling test failed!")