#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_option_a_right_column_right():
    """Test Option A right column moved further to the right"""
    
    # Test data with only Option A selected
    form_data = {
        # Basic info
        'property_address1': '123 Option A Right Column Test',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'first_name2': 'OptionA',
        'last_name2': 'RightColumn',
        
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
    output_path = "TEST_OPTION_A_RIGHT_COLUMN_RIGHT.pdf"
    
    print("🔧 Testing Option A right column moved further to the right...")
    print("\n📋 Updated Option A positions:")
    print("   Left column (Electric Discount, Matching Payment Eversource): X = 55.0")
    print("   Right column (Low Income, Bill Forgiveness, Matching Pay United): X = 186.0 (was 171.0, moved +15 right)")
    print("\n📋 Bill Forgiveness, Matching Pay United, Low Income moved to the right!")
    
    # Test with force visible method
    success = processor.fill_pdf_with_force_visible(template_path, document, output_path)
    
    if success:
        print(f"\n✅ Option A right column test PDF created: {output_path}")
        print(f"📂 File location: {os.path.abspath(output_path)}")
        print("\n🔍 CHECK THE PDF:")
        print("   - Page 3: Single family dwelling checkbox should be visible")
        print("   - Page 4: ONLY Option A checkboxes should be visible")
        print("   - Right column indicators (Low Income, Bill Forgiveness, Matching Pay United) moved right")
        print("\n⚠️  Check if the right column positioning is correct!")
    else:
        print("❌ Failed to create Option A right column test PDF")

if __name__ == "__main__":
    test_option_a_right_column_right()