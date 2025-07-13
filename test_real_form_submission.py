#!/usr/bin/env python3
"""
Test with real form submission data to see if dwelling type gets lost
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_real_form_submission():
    """Test with realistic form submission data"""
    
    print("📋 TESTING REAL FORM SUBMISSION FLOW")
    print("=" * 60)
    print("Simulating complete form submission with dwelling type")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    print(f"📋 Extracted {len(pdf_fields)} PDF fields")
    
    # Simulate a REAL form submission with all data
    form_data = {
        # Section 1: Property Information
        'property_address': '123 Real Street',
        'apartment_number': '5A',
        'city': 'Hartford',
        'state': 'CT',
        'zip_code': '06103',
        'apartments_count': '8',
        'dwelling_type': 'apartment',  # KEY FIELD
        
        # Section 2: Personal Information
        'first_name': 'Jane',
        'last_name': 'Smith',
        'telephone': '860-555-1234',
        'email': 'jane@example.com',
        'phone_additional': '860-555-5678',
        
        # Section 2: Energy Information
        'heating_fuel': 'electric',
        'applicant_type': 'renter',
        'electric_utility': 'eversource',
        'gas_utility': 'cng',
        'electric_account': '111222333',
        'gas_account': '444555666',
        'electric_account_holder': 'applicant',
        'gas_account_holder': 'other',
        'gas_other_name': 'Property Manager',
        
        # Section 3: Qualification
        'household_size': '3',
        'adults_count': '2',
        'annual_income': '35000',
        'utility_program': ['electric_discount', 'low_income_discount'],
        
        # Property Owner Information
        'owner_name': 'Smith Properties LLC',
        'owner_address': '456 Management Ave',
        'owner_city': 'New Haven',
        'owner_state': 'CT',
        'owner_zip': '06511',
        'owner_telephone': '203-555-0000',
        'owner_email': 'info@smithproperties.com'
    }
    
    print(f"📝 Form dwelling_type: {form_data['dwelling_type']}")
    
    # Apply the EXACT logic from app.py line by line
    EXACT_FIELD_MAPPINGS = {
        # Section 1: Property Information  
        'property_address': 'property_address1',
        'apartment_number': 'apt_num1',
        'city': 'city1',
        'state': 'state1',
        'zip_code': 'zip1',
        'apartments_count': 'num_of_apt1',
        
        # Section 2: Personal Information
        'first_name': 'first_name2',
        'last_name': 'last_name2',
        'telephone': 'phone2',
        'email': 'email2',
        'phone_additional': 'phone_num1',
        
        # This is WRONG in app.py - dwelling_type shouldn't be in direct mappings
        'dwelling_type': 'dwelling_single_fam1',  
        
        # Other mappings...
        'heating_fuel': 'fuel_type_elec2',
        'applicant_type': 'owner2',
        'electric_utility': 'electric_eversource2',
        'gas_utility': 'gas_util_cng2',
        'electric_account': 'elec_acct_num2',
        'gas_account': 'gas_acct_num2',
        'electric_other_name': 'elect_acct_other_name2',
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
    
    print(f"\\n🔧 STEP 1: EXACT_FIELD_MAPPINGS (this might BREAK dwelling_type)")
    special_case_matches = 0
    
    # Apply direct mappings first (this is problematic for dwelling_type)
    for form_field, pdf_field_name in EXACT_FIELD_MAPPINGS.items():
        form_value = form_data.get(form_field)
        if not form_value:
            continue
        
        if form_field == 'dwelling_type':
            print(f"   ⚠️  PROBLEM: dwelling_type in EXACT_FIELD_MAPPINGS")
            print(f"      Trying to map 'apartment' → 'dwelling_single_fam1' (WRONG!)")
            
            # This will FAIL because we're looking for dwelling_single_fam1 but form has 'apartment'
            for field in pdf_fields:
                if field.get('pdf_field_name') == pdf_field_name or field['name'] == pdf_field_name:
                    field['value'] = str(form_value)  # This sets 'apartment' on dwelling_single_fam1!
                    field['assigned_to'] = 'user1'
                    print(f"      ❌ WRONG MAPPING: Set {field['name']} = 'apartment' (should be checkbox!)")
                    break
            continue
        
        # Handle other fields normally
        for field in pdf_fields:
            if field.get('pdf_field_name') == pdf_field_name or field['name'] == pdf_field_name:
                field['value'] = str(form_value)
                field['assigned_to'] = 'user1'
                print(f"   ✅ {form_field} → {field['name']} = {form_value}")
                break
    
    print(f"\\n🔧 STEP 2: SPECIAL CASE HANDLING (this should fix dwelling_type)")
    
    # Now handle special cases (this should override the wrong mapping above)
    form_field = 'dwelling_type'
    form_value = form_data.get(form_field)
    
    if form_value:
        print(f"   Form value: {form_value}")
        
        # Handle dwelling type specially
        dwelling_mappings = {
            'single_family': 'Single Family Home (Checkbox)',
            'apartment': 'Apartment (Checkbox)', 
            'condominium': 'Condominium (Checkbox)'
        }
        target_field = dwelling_mappings.get(form_value)
        print(f"   Target field: {target_field}")
        
        if target_field:
            matched = False
            for field in pdf_fields:
                if field['name'] == target_field:
                    field['value'] = 'true'  # Override previous wrong value
                    field['assigned_to'] = 'user1'
                    field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                    matched = True
                    special_case_matches += 1
                    print(f"   ✅ FIXED: {form_value} → {field['name']} = true")
                    print(f"      PDF field: {field['pdf_field_name']}")
                    break
            
            if not matched:
                print(f"   ❌ FAILED: Could not find {target_field}")
    
    # Create test document
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': pdf_fields,
        'user1_data': form_data,
        'user2_data': {
            'applicant_signature': 'Jane Smith',
            'authorization_date': '2025-07-13'
        }
    }
    
    # Add signature
    for field in pdf_fields:
        if field['name'] == 'Applicant Signature':
            field['value'] = 'Jane Smith'
            field['assigned_to'] = 'user2'
            field['type'] = 'signature'
            break
    
    # Generate PDF
    output_file = 'REAL_FORM_SUBMISSION_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\\n✅ Real form submission PDF created: {output_file}")
        
        # Check if dwelling checkbox is properly set
        import fitz
        doc = fitz.open(output_file)
        page = doc[2]  # Page 3
        widgets = list(page.widgets())
        
        # Check dwelling checkbox
        dwelling_found = False
        dwelling_wrong = False
        
        for widget in widgets:
            # Check if apartment checkbox is checked
            if 'dwelling_apt1' in widget.field_name:
                if widget.field_value in [True, 1, 'Yes']:
                    dwelling_found = True
                    print(f"🎉 SUCCESS: {widget.field_name} = {widget.field_value}")
                else:
                    print(f"❌ FAILED: {widget.field_name} = {widget.field_value}")
            
            # Check if wrong field got set
            elif 'dwelling_single_fam1' in widget.field_name:
                if widget.field_value == 'apartment':
                    dwelling_wrong = True
                    print(f"⚠️  WRONG: {widget.field_name} = {widget.field_value} (should be checkbox!)")
        
        doc.close()
        
        if dwelling_found:
            print(f"\\n✅ Dwelling type mapping works correctly!")
        else:
            print(f"\\n❌ Dwelling type mapping FAILED!")
            if dwelling_wrong:
                print(f"   The problem is EXACT_FIELD_MAPPINGS overrides special handling")
        
        return dwelling_found
    else:
        print(f"❌ Failed to create real form submission PDF")
        return False

if __name__ == "__main__":
    success = test_real_form_submission()
    if success:
        print("\\n✅ Real form submission test PASSED!")
    else:
        print("\\n❌ Real form submission test FAILED!")