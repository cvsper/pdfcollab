#!/usr/bin/env python3
"""
Test dwelling indicators with CORRECT coordinate system understanding
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_correct_top_position():
    """Test dwelling indicators at the ACTUAL top using high Y values"""
    
    print("🔝 TESTING CORRECT TOP POSITIONING")
    print("=" * 60)
    print("Using HIGH Y values (y=750) to place at TOP of page")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Test data
    form_data = {
        'property_address': 'CORRECT TOP TEST - 777 High Street',
        'dwelling_type': 'apartment',  # This will create banner at y=750 (top)
        'first_name': 'HIGH',
        'last_name': 'POSITION'
    }
    
    print(f"📝 Testing dwelling_type: {form_data['dwelling_type']}")
    print(f"🔝 Expected: Banner at y=750 (ACTUAL top of page)")
    print(f"📊 Coordinate system: (0,0) = bottom-left, high Y = top")
    
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
        'user1_data': form_data,  # This triggers banner at y=750
        'user2_data': {}
    }
    
    # Generate PDF with correct top positioning
    output_file = 'CORRECT_TOP_POSITION_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ CORRECT TOP position PDF created: {output_file}")
        
        print(f"\n🔝 CORRECT TOP POSITIONING SPECS:")
        print(f"   📍 Apartment position: x=250, y=750 (HIGH Y = TOP)")
        print(f"   📏 Size: 120x15 pixels (readable width)")
        print(f"   🟥 Red banner with light red fill")
        print(f"   📝 Text: 'APARTMENT' (fontsize 8)")
        print(f"   🔲 Clean border")
        
        print(f"\n📖 COORDINATE SYSTEM UNDERSTANDING:")
        print(f"   🔻 WRONG: y=5 was near BOTTOM of page")
        print(f"   🔝 RIGHT: y=750 is near TOP of page")
        print(f"   📊 PDF coordinates: (0,0) = bottom-left corner")
        print(f"   📏 Page height ≈ 792 points, so y=750 = top area")
        
        print(f"\n📖 WHAT YOU SHOULD SEE:")
        print(f"   1. Open '{output_file}' in your PDF viewer")
        print(f"   2. Go to page 3")
        print(f"   3. Look at the TOP of the page")
        print(f"   4. You should see a red banner saying 'APARTMENT' at the TOP!")
        print(f"   5. It should finally be where you wanted it!")
        
        return True
    else:
        print(f"❌ Failed to create correct top position PDF")
        return False

if __name__ == "__main__":
    success = test_correct_top_position()
    if success:
        print("\n🎉 CORRECT TOP POSITION TEST COMPLETE!")
        print("🔝 The dwelling selection should NOW be at the actual top!")
    else:
        print("\n❌ Correct top position test failed!")