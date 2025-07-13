#!/usr/bin/env python3
"""
Test the updated PDF processor with visual dwelling indicators
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_visual_dwelling_solution():
    """Test the visual dwelling solution in the updated PDF processor"""
    
    print("🎨 TESTING VISUAL DWELLING SOLUTION")
    print("=" * 60)
    print("Using updated PDF processor with visual indicators")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Complete test data with dwelling type
    form_data = {
        'property_address': 'VISUAL SOLUTION TEST - 888 Indicator Street',
        'apartment_number': '9Z',
        'dwelling_type': 'apartment',  # This will trigger visual indicators
        'first_name': 'VISUAL',
        'last_name': 'SOLUTION',
        'telephone': '860-555-VISUAL',
        'email': 'visual@solution.com',
        'heating_fuel': 'electric',
        'applicant_type': 'renter'
    }
    
    print(f"📝 Testing dwelling_type: {form_data['dwelling_type']}")
    
    # Apply mappings (without dwelling_type in EXACT_FIELD_MAPPINGS)
    CORRECTED_EXACT_FIELD_MAPPINGS = {
        'property_address': 'property_address1',
        'apartment_number': 'apt_num1',
        'first_name': 'first_name2',
        'last_name': 'last_name2',
        'telephone': 'phone2',
        'email': 'email2'
    }
    
    # Apply direct mappings
    for form_field, pdf_field_name in CORRECTED_EXACT_FIELD_MAPPINGS.items():
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
    
    # Handle other special cases
    special_mappings = {
        'heating_fuel': {'electric': 'fuel_type_elec2'},
        'applicant_type': {'renter': 'renter2'}
    }
    
    for form_field, mappings in special_mappings.items():
        form_value = form_data.get(form_field)
        if form_value and form_value in mappings:
            pdf_field_name = mappings[form_value]
            for field in pdf_fields:
                if field.get('pdf_field_name') == pdf_field_name:
                    field['value'] = 'true'
                    field['assigned_to'] = 'user1'
                    print(f"✅ Special: {form_field}={form_value} → {field['name']}")
                    break
    
    # Create test document
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': pdf_fields,
        'user1_data': form_data,  # This will be used by add_dwelling_visual_indicators
        'user2_data': {
            'applicant_signature': 'VISUAL SOLUTION',
            'authorization_date': '2025-07-13'
        }
    }
    
    # Add signature
    for field in pdf_fields:
        if field['name'] == 'Applicant Signature':
            field['value'] = 'VISUAL SOLUTION'
            field['assigned_to'] = 'user2'
            field['type'] = 'signature'
            break
    
    # Generate PDF using the updated processor (will include visual indicators)
    output_file = 'VISUAL_DWELLING_SOLUTION_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ Visual solution PDF created: {output_file}")
        
        # Count filled fields
        filled_count = sum(1 for f in pdf_fields if f.get('value'))
        fill_rate = (filled_count / len(pdf_fields)) * 100
        
        print(f"\n📊 RESULTS:")
        print(f"   📋 Total fields: {len(pdf_fields)}")
        print(f"   ✅ Filled fields: {filled_count}")
        print(f"   📈 Fill rate: {fill_rate:.1f}%")
        
        print(f"\n🎯 VISUAL INDICATORS ADDED:")
        print(f"   🔴 Red circle around apartment checkbox")
        print(f"   🟡 Yellow highlight rectangle")
        print(f"   📝 Text indicator (if supported)")
        print(f"   ⚪ Gray circles around unselected options")
        
        print(f"\n📍 WHERE TO LOOK:")
        print(f"   1. Open '{output_file}' in your PDF viewer")
        print(f"   2. Go to page 3")
        print(f"   3. Look around coordinates (41, 268) - apartment area")
        print(f"   4. You should see clear visual indicators showing apartment is selected")
        
        return True
    else:
        print(f"❌ Failed to create visual solution PDF")
        return False

if __name__ == "__main__":
    success = test_visual_dwelling_solution()
    if success:
        print("\n🎉 VISUAL DWELLING SOLUTION TEST COMPLETE!")
        print("📍 The dwelling selection should now be clearly visible!")
    else:
        print("\n❌ Visual dwelling solution test failed!")