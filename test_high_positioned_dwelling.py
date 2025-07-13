#!/usr/bin/env python3
"""
Test dwelling indicators positioned much higher on the page
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_high_positioned_dwelling():
    """Test dwelling indicators positioned much higher"""
    
    print("⬆️  TESTING HIGH POSITIONED DWELLING INDICATORS")
    print("=" * 60)
    print("Creating PDF with indicators positioned MUCH HIGHER on page 3")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Test data
    form_data = {
        'property_address': 'HIGH POSITION TEST - 555 Top Of Page Street',
        'dwelling_type': 'apartment',  # This will create HIGH positioned indicators
        'first_name': 'HIGH',
        'last_name': 'POSITION'
    }
    
    print(f"📝 Testing dwelling_type: {form_data['dwelling_type']}")
    print(f"⬆️  Expected: HUGE indicators at y=220 (much higher than y=268)")
    
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
        'user1_data': form_data,  # This triggers HIGH positioned indicators
        'user2_data': {}
    }
    
    # Generate PDF with HIGH positioned indicators
    output_file = 'HIGH_POSITIONED_DWELLING_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ HIGH positioned dwelling PDF created: {output_file}")
        
        print(f"\n⬆️  NEW HIGH POSITION INDICATORS:")
        print(f"   📍 Location: Page 3, y=220 (was y=268 - now 48 points higher!)")
        print(f"   📏 Size: 200x20 pixels (was 7x7 - now 28x larger!)")
        print(f"   🟥 HUGE bright red banner across the width")
        print(f"   📝 Large text 'SELECTED: APARTMENT' (fontsize 16)")
        print(f"   🔲 Red border with corner markers")
        print(f"   📊 Multiple fallback indicators if text fails")
        
        print(f"\n📖 POSITION COMPARISON:")
        print(f"   🔻 OLD position: y=268 (lower on page)")
        print(f"   ⬆️  NEW position: y=220 (much higher on page)")
        print(f"   📏 Moved up by: 48 points = ~0.67 inches")
        
        print(f"\n📖 INSTRUCTIONS:")
        print(f"   1. Open '{output_file}' in your PDF viewer")
        print(f"   2. Go to page 3")
        print(f"   3. Look at the UPPER part of the page around y=220")
        print(f"   4. You should see a large red banner that's impossible to miss!")
        
        return True
    else:
        print(f"❌ Failed to create high positioned dwelling PDF")
        return False

if __name__ == "__main__":
    success = test_high_positioned_dwelling()
    if success:
        print("\n🎉 HIGH POSITIONED DWELLING TEST COMPLETE!")
        print("⬆️  The dwelling selection should now be positioned MUCH HIGHER!")
    else:
        print("\n❌ High positioned dwelling test failed!")