#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_option_a_higher_right():
    """Test Option A positions moved a little higher and to the right"""
    
    # Test data with only Option A selected
    form_data = {
        # Basic info
        'property_address1': '123 Option A Higher Right Test',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'first_name2': 'OptionA',
        'last_name2': 'HigherRight',
        
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
    output_path = "TEST_OPTION_A_HIGHER_RIGHT.pdf"
    
    print("🔧 Testing Option A positions moved higher and to the right...")
    print("\n📋 New Option A positions:")
    print("   Left column X: 55.0 (was 40.0, moved +15 right)")
    print("   Right column X: 171.0 (was 156.0, moved +15 right)")
    print("   Y positions: 465-488 (was 450-473, moved +15 higher)")
    print("\n📋 Option A should now be positioned higher and to the right!")
    
    # Test with force visible method
    success = processor.fill_pdf_with_force_visible(template_path, document, output_path)
    
    if success:
        print(f"\n✅ Option A higher right test PDF created: {output_path}")
        print(f"📂 File location: {os.path.abspath(output_path)}")
        print("\n🔍 CHECK THE PDF:")
        print("   - Page 3: Single family dwelling checkbox should be visible")
        print("   - Page 4: ONLY Option A checkboxes should be visible")
        print("   - Option A visual indicators should be higher and to the right")
        print("\n⚠️  Check if this position adjustment is perfect for Option A!")
    else:
        print("❌ Failed to create Option A higher right test PDF")

if __name__ == "__main__":
    test_option_a_higher_right()