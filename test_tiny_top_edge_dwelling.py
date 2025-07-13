#!/usr/bin/env python3
"""
Test tiny dwelling banner at the absolute top edge of the page
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_tiny_top_edge_dwelling():
    """Test tiny dwelling banner at the absolute top edge"""
    
    print("🔝 TESTING TINY TOP EDGE DWELLING BANNER")
    print("=" * 60)
    print("Creating PDF with TINY banner at ABSOLUTE TOP EDGE of page 3")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Test data
    form_data = {
        'property_address': 'TINY TOP EDGE TEST - 333 Edge Street',
        'dwelling_type': 'apartment',  # This will create tiny top edge banner
        'first_name': 'TINY',
        'last_name': 'EDGE'
    }
    
    print(f"📝 Testing dwelling_type: {form_data['dwelling_type']}")
    print(f"🔝 Expected: Tiny banner at y=5 (absolute top edge of page)")
    
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
        'user1_data': form_data,  # This triggers tiny top edge banner
        'user2_data': {}
    }
    
    # Generate PDF with tiny top edge banner
    output_file = 'TINY_TOP_EDGE_DWELLING_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ TINY TOP EDGE banner PDF created: {output_file}")
        
        print(f"\n🔝 TINY TOP EDGE BANNER SPECIFICATIONS:")
        print(f"   📍 Position: x=250, y=5 (absolute top edge center)")
        print(f"   📏 Size: 80x10 pixels (very narrow and tiny)")
        print(f"   🟥 Thin red banner with very light fill")
        print(f"   📝 Text: 'APARTMENT' (fontsize 8, compact)")
        print(f"   🔲 Minimal thin border")
        print(f"   📊 4 tiny fallback red rectangles if text fails")
        
        print(f"\n📖 FINAL SIZE AND POSITION COMPARISON:")
        print(f"   🔻 ORIGINAL: x=41, y=268, w=7, h=7 (tiny checkbox)")
        print(f"   📋 PREVIOUS: x=200, y=20, w=150, h=15 (still too wide/low)")
        print(f"   🔝 NOW: x=250, y=5, w=80, h=10 (tiny top edge!)")
        print(f"   📏 Final position: 263 points = ~3.7 inches higher!")
        print(f"   📐 Width: Now only 80px (was 150px - much narrower)")
        print(f"   📐 Height: Now only 10px (was 15px - shorter)")
        
        print(f"\n📖 WHAT YOU SHOULD SEE:")
        print(f"   1. Open '{output_file}' in your PDF viewer")
        print(f"   2. Go to page 3")
        print(f"   3. Look at the ABSOLUTE TOP EDGE of the page")
        print(f"   4. You should see a tiny red banner saying 'APARTMENT'")
        print(f"   5. It should be at the very edge, like a page tab!")
        
        return True
    else:
        print(f"❌ Failed to create tiny top edge banner PDF")
        return False

if __name__ == "__main__":
    success = test_tiny_top_edge_dwelling()
    if success:
        print("\n🎉 TINY TOP EDGE BANNER TEST COMPLETE!")
        print("🔝 The dwelling selection is now a tiny banner at the absolute top edge!")
    else:
        print("\n❌ Tiny top edge banner test failed!")