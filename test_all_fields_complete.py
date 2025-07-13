#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_all_fields_complete():
    """Test filling ALL fields including Options A, B, and D"""
    
    # Comprehensive form data with ALL fields filled
    form_data = {
        # Section 1: Property Information
        'property_address1': '123 Complete Test Street',
        'apt_num1': '10B',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'num_of_apt1': '50',  # Number of apartments in building
        'phone_num1': '617-555-1234',  # Additional phone field
        
        # Section 2: Personal Information
        'first_name2': 'John',
        'last_name2': 'TestComplete',
        'phone2': '617-555-5678',
        'email2': 'john.test@example.com',
        
        # Section 2: Dwelling Type - Testing Apartment
        'dwelling_single_fam1': 'No',
        'dwelling_apt1': 'Yes',  # Selected
        'dwelling_condo1': 'No',
        
        # Section 2: Heating Fuel - Testing Electric
        'fuel_type_elec2': 'Yes',  # Selected
        'fuel_type_gas2': 'No',
        'fuel_type_oil2': 'No',
        'fuel_type_propane2': 'No',
        
        # Section 2: Applicant Type - Testing Renter
        'owner2': 'No',
        'renter2': 'Yes',  # Selected
        
        # Section 2: Electric Utility - Testing Eversource
        'electric_eversource2': 'Yes',  # Selected
        'electric_ui2': 'No',
        
        # Section 2: Gas Utility - Testing CNG
        'gas_util_cng2': 'Yes',  # Selected
        'gas_util_eversource2': 'No',
        'gas_util_scg2': 'No',
        
        # Section 2: Account Holder Information
        'elect_acct_applicant2': 'Yes',  # Electric account in applicant's name
        'elect_acct_other2': 'No',
        'elect_acct_other_acct2': 'No',
        'gas_acct_applicant2': 'No',
        'gas_acct_other2': 'Yes',  # Gas account in other's name
        
        # Section 2: Account Names and Numbers
        'elect_acct_other_name2': '',  # Not needed since applicant holds electric
        'gas_acct_other_name2': 'Jane Doe',  # Gas account holder name
        'elec_acct_num2': 'ELEC123456789',
        'gas_acct_num2': 'GAS987654321',
        
        # Section 3: Household and Income Information
        'people_in_household4': '4',  # Total people
        'people_in_household_overage4': '2',  # Adults over 60
        'annual_income4': '35000',  # Annual income
        
        # Section 4: Option A - ALL UTILITY PROGRAMS CHECKED
        'elec_discount4': 'Yes',
        'low_income4': 'Yes',
        'matching_payment_eversource4': 'Yes',
        'bill_forgive4': 'Yes',
        'matching_pay_united4': 'Yes',
        
        # Section 4: Option B - ALL ASSISTANCE PROGRAMS CHECKED
        'ebt4': 'Yes',
        'energy_award_letter4': 'Yes',
        'section_eight4': 'Yes',
        
        # Section 4: Option D - MULTIFAMILY CHECKED
        'multifam4': 'Yes',
        
        # Section 4: Landlord/Owner Information (for renters)
        'landlord_name3': 'Property Management LLC',
        'address3': '456 Landlord Avenue',
        'city3': 'Cambridge',
        'text_55cits': 'MA',  # Landlord state
        'text_56qpfj': '02139',  # Landlord ZIP
        'phone3': '617-555-9999',  # Landlord phone
        'email3': 'landlord@property.com',  # Landlord email
        
        # Signatures (would normally come from User 2)
        'signature3': 'John TestComplete',  # Applicant signature
        'property_ower_sig3': 'Property Manager',  # Property owner signature
        'date3': '01/13/2025',  # Applicant signature date
        'date_property_mang3': '01/13/2025'  # Property owner signature date
    }
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Create document structure
    document = {
        'user1_data': form_data,
        'user2_data': {
            'applicant_signature': 'typed:John TestComplete',
            'owner_signature': 'typed:Property Manager'
        },
        'file_path': 'homworks.pdf'
    }
    
    template_path = "homworks.pdf"
    output_path = "TEST_ALL_FIELDS_COMPLETE.pdf"
    
    print("🔧 Testing ALL fields including Options A, B, and D...")
    print("\n📋 Fields being tested:")
    print("   ✓ All Section 1 property fields")
    print("   ✓ All Section 2 personal info and utilities")
    print("   ✓ All Section 3 household/income fields")
    print("   ✓ Option A: ALL 5 utility programs")
    print("   ✓ Option B: ALL 3 assistance programs")
    print("   ✓ Option D: Multifamily program")
    print("   ✓ All landlord fields")
    print("   ✓ Both signatures\n")
    
    # Test with force visible method (production method)
    success = processor.fill_pdf_with_force_visible(template_path, document, output_path)
    
    if success:
        print(f"\n✅ Comprehensive test PDF created: {output_path}")
        print(f"📂 File location: {os.path.abspath(output_path)}")
        print("\n🔍 VERIFY IN THE PDF:")
        print("   1. Dwelling: Apartment checkbox should be checked with visual indicator")
        print("   2. Option A: ALL 5 boxes should be checked:")
        print("      - Electric Discount Rate")
        print("      - Low Income Discount") 
        print("      - Matching Payment Program (Eversource)")
        print("      - Bill Forgiveness")
        print("      - Matching Payment Program (United Illuminating)")
        print("   3. Option B: ALL 3 boxes should be checked:")
        print("      - EBT Card (Food Stamps)")
        print("      - Copy of Energy Assistance Award Letter")
        print("      - Verification of Section 8")
        print("   4. Option D: Multifamily box should be checked")
        print("   5. All text fields should be filled")
        print("\n⚠️  If Options A, B, or D are NOT checked, there's a mapping issue!")
    else:
        print("❌ Failed to create comprehensive test PDF")

if __name__ == "__main__":
    test_all_fields_complete()