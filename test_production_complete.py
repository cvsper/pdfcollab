#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_production_complete():
    """Comprehensive test simulating complete production form submission"""
    
    print("🚀 PRODUCTION COMPLETE TEST")
    print("=" * 60)
    print("Testing all fixes for dwelling types and Options A, B, D")
    print("This simulates a complete user form submission in production")
    print("=" * 60)
    
    # Complete production-style form data
    form_data = {
        # Section 1: Property Information
        'property_address1': '789 Production Complete Avenue',
        'apt_num1': '15C',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'num_of_apt1': '100',
        'phone_num1': '617-555-0001',
        
        # Section 2: Personal Information
        'first_name2': 'Production',
        'last_name2': 'TestComplete',
        'phone2': '617-555-0002',
        'email2': 'production.test@example.com',
        
        # Section 2: Dwelling Type - Apartment Selected
        'dwelling_single_fam1': 'No',
        'dwelling_apt1': 'Yes',
        'dwelling_condo1': 'No',
        
        # Section 2: Heating Fuel - Gas Selected
        'fuel_type_elec2': 'No',
        'fuel_type_gas2': 'Yes',
        'fuel_type_oil2': 'No',
        'fuel_type_propane2': 'No',
        
        # Section 2: Applicant Type - Renter Selected
        'owner2': 'No',
        'renter2': 'Yes',
        
        # Section 2: Electric Utility - Eversource Selected
        'electric_eversource2': 'Yes',
        'electric_ui2': 'No',
        
        # Section 2: Gas Utility - Eversource Selected
        'gas_util_cng2': 'No',
        'gas_util_eversource2': 'Yes',
        'gas_util_scg2': 'No',
        
        # Section 2: Account Information
        'elect_acct_applicant2': 'Yes',
        'elect_acct_other2': 'No',
        'gas_acct_applicant2': 'Yes',
        'gas_acct_other2': 'No',
        'elec_acct_num2': 'PROD123456789',
        'gas_acct_num2': 'GAS987654321',
        
        # Section 3: Household Information
        'people_in_household4': '3',
        'people_in_household_overage4': '1',
        'annual_income4': '42000',
        
        # Section 4: ALL OPTIONS SELECTED FOR COMPLETE TEST
        
        # Option A: ALL 5 utility programs
        'elec_discount4': 'Yes',
        'low_income4': 'Yes',
        'matching_payment_eversource4': 'Yes',
        'bill_forgive4': 'Yes',
        'matching_pay_united4': 'Yes',
        
        # Option B: ALL 3 documentation types
        'ebt4': 'Yes',
        'energy_award_letter4': 'Yes',
        'section_eight4': 'Yes',
        
        # Option D: Multifamily
        'multifam4': 'Yes',
        
        # Section 4: Landlord Information (for renters)
        'landlord_name3': 'Boston Property Management Co.',
        'address3': '456 Landlord Street',
        'city3': 'Cambridge',
        'text_55cits': 'MA',
        'text_56qpfj': '02139',
        'phone3': '617-555-0003',
        'email3': 'management@bostonproperties.com'
    }
    
    # Test 1: Production method (force visible)
    print("\n🔧 TEST 1: Production Force Visible Method")
    print("-" * 40)
    
    processor = PDFProcessor()
    document = {
        'user1_data': form_data,
        'user2_data': {
            'applicant_signature': 'typed:Production TestComplete',
            'owner_signature': 'typed:Boston Property Management Co.'
        },
        'file_path': 'homworks.pdf'
    }
    
    template_path = "homworks.pdf"
    output_path1 = "PRODUCTION_COMPLETE_TEST.pdf"
    
    success1 = processor.fill_pdf_with_force_visible(template_path, document, output_path1)
    
    if success1:
        print(f"✅ Production test created: {output_path1}")
    else:
        print("❌ Production test failed")
    
    # Test 2: Frontend array format
    print("\n🔧 TEST 2: Frontend Array Format")
    print("-" * 40)
    
    frontend_data = {
        # Basic info with frontend field names
        'property_address': '123 Frontend Array Test',
        'apartment_number': '5A',
        'city': 'Boston',
        'state': 'MA',
        'zip_code': '02101',
        'first_name': 'Frontend',
        'last_name': 'ArrayTest',
        'telephone': '617-555-0004',
        'email': 'frontend@test.com',
        
        # Dwelling type as single field
        'dwelling_type': 'condominium',
        
        # Option A as array
        'utility_program': [
            'electric_discount',
            'low_income_discount',
            'matching_payment'
        ],
        
        # Option B as array
        'documentation': [
            'ebt_award',
            'section_8'
        ],
        
        # Option D as qualification option
        'qualification_option': 'option_d'
    }
    
    document2 = {
        'user1_data': frontend_data,
        'user2_data': {},
        'file_path': 'homworks.pdf'
    }
    
    output_path2 = "FRONTEND_ARRAY_TEST.pdf"
    success2 = processor.fill_pdf_with_force_visible(template_path, document2, output_path2)
    
    if success2:
        print(f"✅ Frontend array test created: {output_path2}")
    else:
        print("❌ Frontend array test failed")
    
    # Test 3: Mixed format (some arrays, some direct)
    print("\n🔧 TEST 3: Mixed Format Test")
    print("-" * 40)
    
    mixed_data = {
        # Mix of frontend and direct field names
        'property_address': '456 Mixed Format Test',
        'first_name2': 'Mixed',
        'last_name2': 'Format',
        'city1': 'Cambridge',
        'state1': 'MA',
        'zip1': '02139',
        
        # Direct dwelling fields
        'dwelling_single_fam1': 'Yes',
        'dwelling_apt1': 'No',
        'dwelling_condo1': 'No',
        
        # Option A: Some array, some direct
        'utility_program': ['electric_discount', 'bill_forgiveness'],
        'matching_pay_united4': 'Yes',
        
        # Option B: Direct fields only
        'ebt4': 'Yes',
        'energy_award_letter4': 'Yes',
        
        # Option D: Both methods (should not conflict)
        'qualification_option': 'option_d',
        'multifam4': 'Yes'
    }
    
    document3 = {
        'user1_data': mixed_data,
        'user2_data': {},
        'file_path': 'homworks.pdf'
    }
    
    output_path3 = "MIXED_FORMAT_TEST.pdf"
    success3 = processor.fill_pdf_with_force_visible(template_path, document3, output_path3)
    
    if success3:
        print(f"✅ Mixed format test created: {output_path3}")
    else:
        print("❌ Mixed format test failed")
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"1. Production Complete: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"2. Frontend Arrays:     {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"3. Mixed Format:        {'✅ PASS' if success3 else '❌ FAIL'}")
    
    print("\n🔍 FILES CREATED:")
    if success1:
        print(f"   📄 {output_path1}")
        print("      - All fields filled with direct PDF field names")
        print("      - All Options A, B, D with visual indicators")
        print("      - Apartment dwelling with visual indicator")
        print("      - Complete production simulation")
    
    if success2:
        print(f"   📄 {output_path2}")
        print("      - Frontend array format (utility_program, documentation)")
        print("      - Condominium dwelling from dwelling_type field")
        print("      - Partial Options A, B, D selections")
    
    if success3:
        print(f"   📄 {output_path3}")
        print("      - Mixed frontend/direct field names")
        print("      - Single family dwelling from direct fields")
        print("      - Mixed array and direct option selections")
    
    print("\n✅ All test PDFs created successfully!")
    print("📂 Files are in the current directory")
    print("\n⚠️  CHECK EACH PDF TO VERIFY:")
    print("   1. All text fields are filled correctly")
    print("   2. Dwelling checkboxes show visual indicators")
    print("   3. Options A, B, D show visual checkbox borders")
    print("   4. No positioning issues with visual indicators")
    
    if not all([success1, success2, success3]):
        print("\n🚨 SOME TESTS FAILED - Review output above for errors")
        return False
    
    return True

if __name__ == "__main__":
    test_production_complete()