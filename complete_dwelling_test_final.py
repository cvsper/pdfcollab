#!/usr/bin/env python3
"""
Complete final test with all dwelling fixes applied and visual enhancements
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import fitz  # PyMuPDF
from pdf_processor import PDFProcessor
import uuid

def complete_dwelling_test_final():
    """Final comprehensive test with visual dwelling checkbox confirmation"""
    
    print("🏆 COMPLETE FINAL DWELLING TEST")
    print("=" * 60)
    print("Creating comprehensive PDF with dwelling checkbox fixes")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Complete form data
    form_data = {
        # Section 1: Property Information
        'property_address': '789 FINAL TEST - Dwelling Checkbox Street',
        'apartment_number': '12B',
        'city': 'Hartford',
        'state': 'CT',
        'zip_code': '06103',
        'apartments_count': '15',
        'dwelling_type': 'apartment',  # THIS IS THE KEY FIELD
        
        # Section 2: Personal Information
        'first_name': 'FINAL',
        'last_name': 'TESTER',
        'telephone': '860-555-FINAL',
        'email': 'final@test.com',
        'phone_additional': '860-555-TEST',
        
        # Section 2: Energy Information
        'heating_fuel': 'electric',
        'applicant_type': 'renter',
        'electric_utility': 'eversource',
        'gas_utility': 'cng',
        'electric_account': '999888777',
        'gas_account': '666555444',
        'electric_account_holder': 'applicant',
        'gas_account_holder': 'other',
        'gas_other_name': 'FINAL PROPERTY MANAGER',
        
        # Section 3: Qualification
        'household_size': '4',
        'adults_count': '2',
        'annual_income': '42000',
        'utility_program': ['electric_discount', 'low_income_discount'],
        
        # Property Owner Information
        'owner_name': 'FINAL TEST PROPERTIES LLC',
        'owner_address': '999 Management Final Ave',
        'owner_city': 'New Haven',
        'owner_state': 'CT',
        'owner_zip': '06511',
        'owner_telephone': '203-555-FINAL',
        'owner_email': 'final@properties.com'
    }
    
    print(f"📝 Dwelling type to test: {form_data['dwelling_type']}")
    
    # Apply CORRECTED mappings (WITHOUT dwelling_type in direct mappings)
    CORRECTED_EXACT_FIELD_MAPPINGS = {
        'property_address': 'property_address1',
        'apartment_number': 'apt_num1',
        'city': 'city1',
        'state': 'state1',
        'zip_code': 'zip1',
        'apartments_count': 'num_of_apt1',
        'first_name': 'first_name2',
        'last_name': 'last_name2',
        'telephone': 'phone2',
        'email': 'email2',
        'phone_additional': 'phone_num1',
        'electric_account': 'elec_acct_num2',
        'gas_account': 'gas_acct_num2',
        'gas_other_name': 'gas_acct_other_name2',
        'household_size': 'people_in_household4',
        'adults_count': 'people_in_household_overage4',
        'annual_income': 'annual_income4',
        'owner_name': 'landlord_name3',
        'owner_address': 'address3',
        'owner_city': 'city3',
        'owner_state': 'text_55cits',
        'owner_zip': 'text_56qpfj',
        'owner_telephone': 'phone3',
        'owner_email': 'email3'
    }
    
    # Apply direct mappings (dwelling_type intentionally excluded)
    mapped_count = 0
    for form_field, pdf_field_name in CORRECTED_EXACT_FIELD_MAPPINGS.items():
        form_value = form_data.get(form_field)
        if form_value:
            for field in pdf_fields:
                if field.get('pdf_field_name') == pdf_field_name or field['name'] == pdf_field_name:
                    field['value'] = str(form_value)
                    field['assigned_to'] = 'user1'
                    mapped_count += 1
                    print(f"✅ Direct: {form_field} → {field['name']}")
                    break
    
    # Handle dwelling_type specially (CRITICAL FIX)
    dwelling_type = form_data.get('dwelling_type')
    if dwelling_type:
        print(f"\\n🏠 SPECIAL DWELLING HANDLING:")
        print(f"   Form value: {dwelling_type}")
        
        dwelling_mappings = {
            'single_family': 'Single Family Home (Checkbox)',
            'apartment': 'Apartment (Checkbox)', 
            'condominium': 'Condominium (Checkbox)'
        }
        target_field = dwelling_mappings.get(dwelling_type)
        print(f"   Target field: {target_field}")
        
        if target_field:
            for field in pdf_fields:
                if field['name'] == target_field:
                    field['value'] = 'true'
                    field['assigned_to'] = 'user1'
                    field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                    mapped_count += 1
                    print(f"   ✅ DWELLING: {dwelling_type} → {field['name']} = true")
                    print(f"      PDF field: {field['pdf_field_name']}")
                    break
    
    # Handle other special cases
    special_mappings = {
        'heating_fuel': {'electric': 'fuel_type_elec2'},
        'applicant_type': {'renter': 'renter2'},
        'electric_utility': {'eversource': 'elec_eversource2'},
        'gas_utility': {'cng': 'gas_cng2'},
        'electric_account_holder': {'applicant': 'elect_acct_applicant2'},
        'utility_program': {
            'electric_discount': 'elec_discount4',
            'low_income_discount': 'low_income4'
        }
    }
    
    # Apply special mappings
    for form_field, mappings in special_mappings.items():
        form_value = form_data.get(form_field)
        
        if form_field == 'utility_program' and isinstance(form_value, list):
            for program in form_value:
                pdf_field_name = mappings.get(program)
                if pdf_field_name:
                    for field in pdf_fields:
                        if field.get('pdf_field_name') == pdf_field_name:
                            field['value'] = 'true'
                            field['assigned_to'] = 'user1'
                            mapped_count += 1
                            print(f"✅ Program: {program} → {field['name']}")
                            break
        elif form_value and form_value in mappings:
            pdf_field_name = mappings[form_value]
            for field in pdf_fields:
                if field.get('pdf_field_name') == pdf_field_name:
                    field['value'] = 'true'
                    field['assigned_to'] = 'user1'
                    mapped_count += 1
                    print(f"✅ Special: {form_field}={form_value} → {field['name']}")
                    break
    
    print(f"\\n📊 Total mappings applied: {mapped_count}")
    
    # Create test document
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': pdf_fields,
        'user1_data': form_data,
        'user2_data': {
            'applicant_signature': 'FINAL TESTER',
            'authorization_date': '2025-07-13',
            'owner_signature': 'FINAL TEST PROPERTIES LLC',
            'owner_signature_date': '2025-07-13'
        }
    }
    
    # Add signatures
    for field in pdf_fields:
        if field['name'] == 'Applicant Signature':
            field['value'] = 'FINAL TESTER'
            field['assigned_to'] = 'user2'
            field['type'] = 'signature'
        elif field['name'] == 'Property Owner Signature':
            field['value'] = 'FINAL TEST PROPERTIES LLC'
            field['assigned_to'] = 'user2'
            field['type'] = 'signature'
    
    # Add dates
    for field in pdf_fields:
        if field['name'] == 'Date' and field.get('position', {}).get('y') == 471.0:
            field['value'] = '2025-07-13'
            field['assigned_to'] = 'user2'
        elif field['name'] == 'Date' and field.get('position', {}).get('y') == 643.0:
            field['value'] = '2025-07-13'
            field['assigned_to'] = 'user2'
    
    # Generate initial PDF
    temp_output = 'TEMP_FINAL_COMPLETE.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, temp_output)
    
    if success:
        print(f"\\n✅ Initial PDF created: {temp_output}")
        
        # Add visual enhancements to dwelling checkbox
        doc = fitz.open(temp_output)
        page = doc[2]  # Page 3
        
        widgets = list(page.widgets())
        dwelling_enhanced = False
        
        for widget in widgets:
            if 'dwelling_apt1' in widget.field_name and widget.field_value in [True, 1, 'Yes', 'On']:
                print(f"\\n🎨 ENHANCING DWELLING CHECKBOX VISIBILITY:")
                
                widget_rect = widget.rect
                x1, y1, x2, y2 = widget_rect
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                # Draw multiple visual indicators
                try:
                    # 1. Bold checkmark text
                    page.insert_text(
                        (center_x - 2, center_y + 1),
                        "✓",
                        fontsize=10,
                        color=(0, 0, 0),
                        fontname="helv"
                    )
                    
                    # 2. Highlight background
                    highlight_rect = fitz.Rect(x1 - 1, y1 - 1, x2 + 1, y2 + 1)
                    page.draw_rect(highlight_rect, color=(0, 0.8, 0), width=2)
                    
                    # 3. Add text label
                    page.insert_text(
                        (x2 + 5, y2),
                        "← APARTMENT SELECTED",
                        fontsize=8,
                        color=(0, 0.8, 0),
                        fontname="helv-bold"
                    )
                    
                    dwelling_enhanced = True
                    print(f"   ✅ Added visual enhancements at ({center_x:.1f}, {center_y:.1f})")
                    
                except Exception as e:
                    print(f"   ❌ Error enhancing checkbox: {e}")
                
                break
        
        # Save the final enhanced PDF
        final_output = 'COMPLETE_FINAL_DWELLING_TEST.pdf'
        doc.save(final_output)
        doc.close()
        
        # Clean up temp file
        if os.path.exists(temp_output):
            os.remove(temp_output)
        
        print(f"\\n🏆 FINAL PDF CREATED: {final_output}")
        
        # Final verification
        doc2 = fitz.open(final_output)
        page2 = doc2[2]
        widgets2 = list(page2.widgets())
        
        # Count filled fields
        filled_count = sum(1 for f in pdf_fields if f.get('value'))
        fill_rate = (filled_count / len(pdf_fields)) * 100
        
        # Check dwelling checkbox specifically
        dwelling_verified = False
        for widget in widgets2:
            if 'dwelling_apt1' in widget.field_name:
                if widget.field_value in [True, 1, 'Yes', 'On']:
                    dwelling_verified = True
                    print(f"✅ DWELLING VERIFIED: {widget.field_name} = {widget.field_value}")
                break
        
        doc2.close()
        
        print(f"\\n📊 FINAL STATISTICS:")
        print(f"   📋 Total fields: {len(pdf_fields)}")
        print(f"   ✅ Filled fields: {filled_count}")
        print(f"   📈 Fill rate: {fill_rate:.1f}%")
        print(f"   🏠 Dwelling checkbox: {'✅ WORKING' if dwelling_verified else '❌ FAILED'}")
        print(f"   🎨 Visual enhancement: {'✅ APPLIED' if dwelling_enhanced else '❌ FAILED'}")
        
        print(f"\\n🎯 INSTRUCTIONS:")
        print(f"   1. Open '{final_output}' in your PDF viewer")
        print(f"   2. Go to page 3")
        print(f"   3. Look for the apartment checkbox - it should be clearly marked")
        print(f"   4. You should see a green border and '← APARTMENT SELECTED' label")
        
        return dwelling_verified and dwelling_enhanced
    else:
        print(f"❌ Failed to create initial PDF")
        return False

if __name__ == "__main__":
    success = complete_dwelling_test_final()
    if success:
        print("\\n🎉 COMPLETE FINAL TEST PASSED!")
        print("🏠 Dwelling checkboxes are working and visually enhanced!")
    else:
        print("\\n❌ Complete final test failed!")