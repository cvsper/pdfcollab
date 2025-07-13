#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_option_a_even_higher():
    """Test the even higher positions for Option A"""
    
    # Test data with only Option A selected
    form_data = {
        # Basic info
        'property_address1': '123 Option A Even Higher Test',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'first_name2': 'OptionA',
        'last_name2': 'EvenHigher',
        
        # Dwelling - Apartment 
        'dwelling_single_fam1': 'No',
        'dwelling_apt1': 'Yes',
        'dwelling_condo1': 'No',
        
        # Option A: ALL 5 utility programs selected
        'elec_discount4': 'Yes',
        'low_income4': 'Yes',
        'matching_payment_eversource4': 'Yes',
        'bill_forgive4': 'Yes',
        'matching_pay_united4': 'Yes',
        
        # Option B: None selected
        'ebt4': 'No',
        'energy_award_letter4': 'No',
        'section_eight4': 'No',
        
        # Option D: None selected
        'multifam4': 'No'
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
    output_path = "TEST_OPTION_A_EVEN_HIGHER.pdf"
    
    print("🔧 Testing EVEN HIGHER positions for Option A...")
    print("\n📋 New Option A Y positions (moved +40 more points higher):")
    print("   - Electric Discount: y=320.0 (was 280.0)")
    print("   - Low Income: y=320.0 (was 280.0)")
    print("   - Matching Payment Eversource: y=332.0 (was 292.0)")
    print("   - Bill Forgiveness: y=331.0 (was 291.0)")
    print("   - Matching Pay United: y=343.0 (was 303.0)")
    print("\n📋 Now Option A should be clearly above everything else")
    
    # Test with force visible method
    success = processor.fill_pdf_with_force_visible(template_path, document, output_path)
    
    if success:
        print(f"\n✅ Option A even higher test PDF created: {output_path}")
        print(f"📂 File location: {os.path.abspath(output_path)}")
        print("\n🔍 CHECK THE PDF:")
        print("   - Page 3: Apartment dwelling checkbox should be visible")
        print("   - Page 4: ONLY Option A checkboxes should be visible and EVEN HIGHER")
        print("   - Option A visual indicators should be at the top of the qualification section")
        print("\n⚠️  Check if this height is correct for Option A!")
    else:
        print("❌ Failed to create Option A even higher test PDF")

if __name__ == "__main__":
    test_option_a_even_higher()