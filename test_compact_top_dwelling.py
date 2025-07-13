#!/usr/bin/env python3
"""
Test compact dwelling header banner at the very top of the page
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_compact_top_dwelling():
    """Test compact dwelling header banner at the very top"""
    
    print("📋 TESTING COMPACT TOP HEADER DWELLING BANNER")
    print("=" * 60)
    print("Creating PDF with COMPACT header banner at VERY TOP of page 3")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Test data
    form_data = {
        'property_address': 'COMPACT HEADER TEST - 222 Header Street',
        'dwelling_type': 'apartment',  # This will create compact top header
        'first_name': 'COMPACT',
        'last_name': 'HEADER'
    }
    
    print(f"📝 Testing dwelling_type: {form_data['dwelling_type']}")
    print(f"📋 Expected: Compact header banner at y=20 (very top, like a page header)")
    
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
        'user1_data': form_data,  # This triggers compact top header
        'user2_data': {}
    }
    
    # Generate PDF with compact top header
    output_file = 'COMPACT_TOP_DWELLING_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ COMPACT TOP header PDF created: {output_file}")
        
        print(f"\n📋 COMPACT TOP HEADER SPECIFICATIONS:")
        print(f"   📍 Position: x=200, y=20 (very top center of page)")
        print(f"   📏 Size: 150x15 pixels (compact header banner)")
        print(f"   🟥 Red banner with light red fill")
        print(f"   📝 Text: 'APARTMENT SELECTED' (fontsize 12)")
        print(f"   🔲 Clean border with small corner markers")
        print(f"   📊 8 fallback red rectangles if text fails")
        
        print(f"\n📖 FINAL POSITION COMPARISON:")
        print(f"   🔻 ORIGINAL: y=268, w=7 (tiny checkbox)")
        print(f"   ⬆️  PREVIOUS: y=90, w=400 (too wide, still low)")
        print(f"   📋 NOW: y=20, w=150 (compact header at very top!)")
        print(f"   📏 Final move: 248 points = ~3.4 inches higher!")
        print(f"   📐 Width reduced: From 400 to 150 pixels (much narrower)")
        
        print(f"\n📖 WHAT YOU SHOULD SEE:")
        print(f"   1. Open '{output_file}' in your PDF viewer")
        print(f"   2. Go to page 3")
        print(f"   3. Look at the VERY TOP CENTER of the page immediately")
        print(f"   4. You should see a compact red header banner saying 'APARTMENT SELECTED'")
        print(f"   5. It should look like a page header - narrow and at the very top!")
        
        return True
    else:
        print(f"❌ Failed to create compact top header PDF")
        return False

if __name__ == "__main__":
    success = test_compact_top_dwelling()
    if success:
        print("\n🎉 COMPACT TOP HEADER TEST COMPLETE!")
        print("📋 The dwelling selection is now a compact header at the very top!")
    else:
        print("\n❌ Compact top header test failed!")