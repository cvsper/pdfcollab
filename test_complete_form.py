#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_complete_form():
    """Test complete form filling with all options selected"""
    
    # Complete test data with everything filled in
    form_data = {
        # Section 1: Property Information
        'property_address1': '123 Complete Test Street',
        'apt_num1': '4B',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'num_of_apt1': '1',
        'phone_num1': '617-555-0123',
        
        # Section 2: Personal Information
        'first_name2': 'John',
        'last_name2': 'Complete',
        'phone2': '617-555-0200',
        'email2': 'john.complete@email.com',
        
        # Section 2: Dwelling Type - All three for testing
        'dwelling_single_fam1': 'Yes',
        'dwelling_apt1': 'No',
        'dwelling_condo1': 'No',
        
        # Section 2: Heating Fuel - Electric
        'fuel_type_elec2': 'Yes',
        'fuel_type_gas2': 'No',
        'fuel_type_oil2': 'No',
        'fuel_type_propane2': 'No',
        
        # Section 2: Applicant Type - Owner
        'owner2': 'Yes',
        'renter2': 'No',
        
        # Section 2: Electric Utility - Eversource
        'electric_eversource2': 'Yes',
        'electric_ui2': 'No',
        
        # Section 2: Gas Utility - Eversource
        'gas_util_cng2': 'No',
        'gas_util_eversource2': 'Yes',
        'gas_util_scg2': 'No',
        
        # Section 2: Account Information
        'elect_acct_applicant2': 'Yes',
        'elect_acct_other2': 'No',
        'gas_acct_applicant2': 'Yes',
        'gas_acct_other2': 'No',
        'elec_acct_num2': '1234567890',
        'gas_acct_num2': '0987654321',
        
        # Section 4: Option A - ALL SELECTED
        'elec_discount4': 'Yes',
        'low_income4': 'Yes',
        'matching_payment_eversource4': 'Yes',
        'bill_forgive4': 'Yes',
        'matching_pay_united4': 'Yes',
        
        # Section 4: Option B - ALL SELECTED
        'ebt4': 'Yes',
        'energy_award_letter4': 'Yes',
        'section_eight4': 'Yes',
        
        # Section 4: Option D - SELECTED
        'multifam4': 'Yes',
        
        # Section 4: Income Information
        'people_in_household4': '4',
        'annual_income4': '65000',
        
        # Section 4: Landlord Information (owner so might not be needed but filling anyway)
        'landlord_name3': 'Property Management LLC',
        'address3': '456 Landlord Avenue',
        'city3': 'Boston',
        'text_55cits': 'MA',
        'text_56qpfj': '02102',
        'phone3': '617-555-0300',
        'email3': 'management@property.com',
        
        # Signatures and Dates
        'signature3': 'John Complete',
        'property_ower_sig3': 'John Complete',
        'date': '12/15/2024'
    }
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Create document structure
    document = {
        'user1_data': form_data,
        'user2_data': {},
        'file_path': 'homworks.pdf'
    }
    
    template_path = "homworks.pdf"
    output_path = "TEST_COMPLETE_FORM.pdf"
    
    print("🔧 Testing complete form filling...")
    print("\n📋 Complete form data:")
    print("   Property: 123 Complete Test Street, Apt 4B, Boston MA 02101")
    print("   Applicant: John Complete")
    print("   Dwelling: Single Family Home")
    print("   Utilities: Electric Eversource, Gas Eversource")
    print("   Option A: ALL 5 programs selected")
    print("   Option B: ALL 3 documents selected")
    print("   Option D: Multifamily selected")
    print("   Income: 4 people, $65,000 annual")
    
    # Test with force visible method
    success = processor.fill_pdf_with_force_visible(template_path, document, output_path)
    
    if success:
        print(f"\n✅ Complete form test PDF created: {output_path}")
        print(f"📂 File location: {os.path.abspath(output_path)}")
        print("\n🔍 CHECK THE PDF:")
        print("   - Page 3: All basic info and dwelling type should be filled")
        print("   - Page 4: ALL Options A, B, D should be visible with indicators")
        print("   - Look for any missing fields or positioning issues")
        print("   - Verify all visual indicators are in correct positions")
        print("\n⚠️  This shows what the complete form looks like!")
    else:
        print("❌ Failed to create complete form test PDF")

if __name__ == "__main__":
    test_complete_form()