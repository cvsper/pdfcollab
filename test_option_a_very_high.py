#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_option_a_very_high():
    """Test the very high positions for Option A"""
    
    # Test data with only Option A selected
    form_data = {
        # Basic info
        'property_address1': '123 Option A Very High Test',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'first_name2': 'OptionA',
        'last_name2': 'VeryHigh',
        
        # Dwelling - Condominium 
        'dwelling_single_fam1': 'No',
        'dwelling_apt1': 'No',
        'dwelling_condo1': 'Yes',
        
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
    output_path = "TEST_OPTION_A_VERY_HIGH.pdf"
    
    print("🔧 Testing VERY HIGH positions for Option A...")
    print("\n📋 New Option A Y positions (moved +60 more points higher):")
    print("   - Electric Discount: y=380.0 (was 320.0)")
    print("   - Low Income: y=380.0 (was 320.0)")
    print("   - Matching Payment Eversource: y=392.0 (was 332.0)")
    print("   - Bill Forgiveness: y=391.0 (was 331.0)")
    print("   - Matching Pay United: y=403.0 (was 343.0)")
    print("\n📋 Option A should now be at the very top of the page")
    
    # Test with force visible method
    success = processor.fill_pdf_with_force_visible(template_path, document, output_path)
    
    if success:
        print(f"\n✅ Option A very high test PDF created: {output_path}")
        print(f"📂 File location: {os.path.abspath(output_path)}")
        print("\n🔍 CHECK THE PDF:")
        print("   - Page 3: Condominium dwelling checkbox should be visible")
        print("   - Page 4: ONLY Option A checkboxes should be visible and VERY HIGH")
        print("   - Option A visual indicators should be near the top of the page")
        print("\n⚠️  Check if this very high position is correct for Option A!")
    else:
        print("❌ Failed to create Option A very high test PDF")

if __name__ == "__main__":
    test_option_a_very_high()