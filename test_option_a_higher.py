#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_option_a_higher():
    """Test the much higher positions for Option A specifically"""
    
    # Test data with only Option A selected
    form_data = {
        # Basic info
        'property_address1': '123 Option A Higher Test',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'first_name2': 'OptionA',
        'last_name2': 'HigherTest',
        
        # Dwelling - Single Family 
        'dwelling_single_fam1': 'Yes',
        'dwelling_apt1': 'No',
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
    output_path = "TEST_OPTION_A_MUCH_HIGHER.pdf"
    
    print("🔧 Testing MUCH HIGHER positions for Option A...")
    print("\n📋 New Option A Y positions (moved +40 points higher):")
    print("   - Electric Discount: y=280.0 (was 240.0)")
    print("   - Low Income: y=280.0 (was 240.0)")
    print("   - Matching Payment Eversource: y=292.0 (was 252.0)")
    print("   - Bill Forgiveness: y=291.0 (was 251.0)")
    print("   - Matching Pay United: y=303.0 (was 263.0)")
    print("\n📋 Option B and D positions unchanged for comparison")
    
    # Test with force visible method
    success = processor.fill_pdf_with_force_visible(template_path, document, output_path)
    
    if success:
        print(f"\n✅ Option A higher test PDF created: {output_path}")
        print(f"📂 File location: {os.path.abspath(output_path)}")
        print("\n🔍 CHECK THE PDF:")
        print("   - Page 3: Single family dwelling checkbox should be visible")
        print("   - Page 4: ONLY Option A checkboxes should be visible and MUCH HIGHER")
        print("   - Option A visual indicators should be clearly positioned above their original spots")
        print("\n⚠️  If Option A is now at the right height, let me know and I can commit!")
    else:
        print("❌ Failed to create Option A higher test PDF")

if __name__ == "__main__":
    test_option_a_higher()