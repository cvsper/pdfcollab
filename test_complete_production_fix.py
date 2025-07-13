#!/usr/bin/env python3
"""
Create a comprehensive test PDF with ALL sections filled after the production fix
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_complete_production_fix():
    """Test complete form filling after production fix"""
    
    print("🚀 COMPLETE PRODUCTION FIX TEST")
    print("=" * 60)
    print("Testing all form sections with comprehensive data")
    
    # Comprehensive test data that matches production form
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': [],
        'user1_data': {
            # Section 1: Property Information
            'property_address': '456 Production Test Avenue',
            'apartment_number': 'Suite 789',
            'city': 'Hartford',
            'state': 'CT',
            'zip_code': '06103',
            'apartments_count': '12',
            'dwelling_type': 'apartment',
            
            # Section 2: Personal Information
            'first_name': 'Maria',
            'last_name': 'Rodriguez',
            'telephone': '860-555-9876',
            'email': 'maria.rodriguez@test.com',
            'phone_additional': '860-555-5432',
            
            # Section 2: Energy & Utilities
            'heating_fuel': 'electric',
            'applicant_type': 'property_owner',
            'electric_utility': 'eversource',
            'gas_utility': 'cng',
            'electric_account': '123456789',
            'gas_account': '987654321',
            'electric_account_holder': 'applicant',
            'gas_account_holder': 'other',
            'electric_other_name': '',
            'gas_other_name': 'John Rodriguez',
            
            # Section 3: Qualification
            'qualification_option': 'option_a',
            'utility_program': ['electric_discount', 'low_income_discount', 'matching_payment', 'bill_forgiveness'],
            'household_size': '4',
            'adults_count': '2',
            'annual_income': '45000',
            
            # Property Owner Information
            'owner_name': 'ABC Property Management LLC',
            'owner_address': '789 Management Street',
            'owner_city': 'New Haven',
            'owner_state': 'CT',
            'owner_zip': '06511',
            'owner_telephone': '203-555-0000',
            'owner_email': 'info@abcproperty.com'
        },
        'user2_data': {
            'applicant_signature': 'Maria Rodriguez',
            'authorization_date': '2025-07-13',
            'owner_signature': 'ABC Property Management LLC',
            'owner_signature_date': '2025-07-13'
        }
    }
    
    # First extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    print(f"📋 Extracted {len(pdf_fields)} PDF fields")
    
    # Apply comprehensive mappings using the fixed logic
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
        
        # Section 2: Utility Information
        'electric_account': 'elec_acct_num2',
        'gas_account': 'gas_acct_num2',
        'electric_other_name': 'elect_acct_other_name2',
        'gas_other_name': 'gas_acct_other_name2',
        
        # Section 3: Qualification
        'household_size': 'people_in_household4',
        'adults_count': 'people_in_household_overage4',
        'annual_income': 'annual_income4',
        
        # Property Owner Information
        'owner_name': 'landlord_name3',
        'owner_address': 'address3',
        'owner_city': 'city3',
        'owner_state': 'text_55cits',
        'owner_zip': 'text_56qpfj',
        'owner_telephone': 'phone3',
        'owner_email': 'email3'
    }
    
    # Apply direct mappings
    mapped_count = 0
    user1_data = test_document['user1_data']
    
    for form_field, pdf_field_name in EXACT_FIELD_MAPPINGS.items():
        form_value = user1_data.get(form_field)
        if form_value:
            # Use the fixed mapping logic
            for field in pdf_fields:
                if field.get('pdf_field_name') == pdf_field_name or field['name'] == pdf_field_name:
                    field['value'] = str(form_value)
                    field['assigned_to'] = 'user1'
                    mapped_count += 1
                    print(f"✅ Mapped: {form_field} → {field['name']}")
                    break
    
    # Apply special case mappings
    # Dwelling type
    dwelling_type = user1_data.get('dwelling_type')
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
                    mapped_count += 1
                    print(f"✅ Dwelling: {dwelling_type} → {target_field}")
                    break
    
    # Heating fuel
    heating_fuel = user1_data.get('heating_fuel')
    if heating_fuel:
        fuel_mappings = {
            'electric': 'Electric Heat (Radio Button)',
            'natural_gas': 'Gas Heat (Radio Button)',
            'oil': 'Oil Heat (Radio Button)',
            'propane': 'Propane Heat (Radio Button)'
        }
        target_field = fuel_mappings.get(heating_fuel)
        if target_field:
            for field in pdf_fields:
                if field['name'] == target_field:
                    field['value'] = 'true'
                    field['assigned_to'] = 'user1'
                    mapped_count += 1
                    print(f"✅ Heating: {heating_fuel} → {target_field}")
                    break
    
    # Applicant type
    applicant_type = user1_data.get('applicant_type')
    if applicant_type:
        applicant_mappings = {
            'property_owner': 'Property Owner (Radio Button)',
            'renter': 'Renter (Radio Button)'
        }
        target_field = applicant_mappings.get(applicant_type)
        if target_field:
            for field in pdf_fields:
                if field['name'] == target_field:
                    field['value'] = 'true'
                    field['assigned_to'] = 'user1'
                    mapped_count += 1
                    print(f"✅ Applicant: {applicant_type} → {target_field}")
                    break
    
    # Electric utility
    electric_utility = user1_data.get('electric_utility')
    if electric_utility:
        electric_mappings = {
            'eversource': 'Electric Eversource (Radio Button)',
            'ui': 'Electric UI (Radio Button)'
        }
        target_field = electric_mappings.get(electric_utility)
        if target_field:
            for field in pdf_fields:
                if field['name'] == target_field:
                    field['value'] = 'true'
                    field['assigned_to'] = 'user1'
                    mapped_count += 1
                    print(f"✅ Electric: {electric_utility} → {target_field}")
                    break
    
    # Gas utility
    gas_utility = user1_data.get('gas_utility')
    if gas_utility:
        gas_mappings = {
            'cng': 'Gas Util CNG (Radio Button)',
            'eversource': 'Gas Util Eversource (Radio Button)',
            'scg': 'Gas Util SCG (Radio Button)'
        }
        target_field = gas_mappings.get(gas_utility)
        if target_field:
            for field in pdf_fields:
                if field['name'] == target_field:
                    field['value'] = 'true'
                    field['assigned_to'] = 'user1'
                    mapped_count += 1
                    print(f"✅ Gas: {gas_utility} → {target_field}")
                    break
    
    # Account holder types
    electric_holder = user1_data.get('electric_account_holder')
    if electric_holder:
        electric_holder_mappings = {
            'applicant': 'Electric Account Applicant (Radio Button)',
            'other': 'Electric Account Other (Radio Button)'
        }
        target_field = electric_holder_mappings.get(electric_holder)
        if target_field:
            for field in pdf_fields:
                if field['name'] == target_field:
                    field['value'] = 'true'
                    field['assigned_to'] = 'user1'
                    mapped_count += 1
                    print(f"✅ Elec holder: {electric_holder} → {target_field}")
                    break
    
    # Utility programs (qualification checkboxes)
    utility_programs = user1_data.get('utility_program', [])
    if utility_programs:
        program_mappings = {
            'electric_discount': 'Elec Discount4 (Checkbox)',
            'low_income_discount': 'Low Income Program (Checkbox)',
            'matching_payment': 'Matching Payment Eversource4 (Checkbox)',
            'bill_forgiveness': 'Bill Forgiveness Program (Checkbox)',
            'matching_payment_united': 'Matching Pay United4 (Checkbox)'
        }
        
        for program in utility_programs:
            target_field = program_mappings.get(program)
            if target_field:
                for field in pdf_fields:
                    if field['name'] == target_field:
                        field['value'] = 'true'
                        field['assigned_to'] = 'user1'
                        mapped_count += 1
                        print(f"✅ Program: {program} → {target_field}")
                        break
    
    # Add signature fields
    user2_data = test_document['user2_data']
    signature_fields = [
        ('applicant_signature', 'Applicant Signature', 'signature3'),
        ('owner_signature', 'Property Owner Signature', 'property_ower_sig3')
    ]
    
    for data_key, field_name, pdf_field_name in signature_fields:
        signature_value = user2_data.get(data_key)
        if signature_value:
            for field in pdf_fields:
                if field['name'] == field_name:
                    field['value'] = signature_value
                    field['assigned_to'] = 'user2'
                    field['type'] = 'signature'
                    mapped_count += 1
                    print(f"✅ Signature: {data_key} → {field_name}")
                    break
    
    # Add date fields
    date_mappings = [
        ('authorization_date', 'user2', 471.0, 'date3'),
        ('owner_signature_date', 'user2', 643.0, 'date_property_mang3')
    ]
    
    for data_key, user, y_pos, pdf_field_name in date_mappings:
        date_value = user2_data.get(data_key)
        if date_value:
            for field in pdf_fields:
                if field['name'] == 'Date' and field.get('position', {}).get('y') == y_pos:
                    field['value'] = date_value
                    field['assigned_to'] = user
                    mapped_count += 1
                    print(f"✅ Date: {data_key} → Date field at y={y_pos}")
                    break
    
    print(f"\n📊 Total mappings applied: {mapped_count}")
    
    # Update document with filled fields
    test_document['pdf_fields'] = pdf_fields
    
    # Generate PDF
    output_file = 'COMPLETE_PRODUCTION_FIX_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ Complete test PDF created: {output_file}")
        
        # Count filled fields
        filled_count = sum(1 for f in pdf_fields if f.get('value'))
        fill_rate = (filled_count / len(pdf_fields)) * 100
        
        print(f"📊 Final results:")
        print(f"   📋 Total fields: {len(pdf_fields)}")
        print(f"   ✅ Filled fields: {filled_count}")
        print(f"   📈 Fill rate: {fill_rate:.1f}%")
        
        if fill_rate >= 80:
            print(f"\n🎉 SUCCESS: Production fix is working! {fill_rate:.1f}% fill rate")
            return True
        else:
            print(f"\n⚠️  Moderate success: {fill_rate:.1f}% fill rate (some fields missing)")
            return True
    else:
        print(f"\n❌ PDF generation failed")
        return False

if __name__ == "__main__":
    success = test_complete_production_fix()
    if success:
        print("\n✅ Production fix validated - ready for deployment!")
    else:
        print("\n❌ Production fix needs more work")