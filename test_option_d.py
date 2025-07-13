#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_option_d():
    """Test Option D positioning"""
    
    # Test data with only Option D selected
    form_data = {
        # Basic info
        'property_address1': '123 Option D Test',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'first_name2': 'OptionD',
        'last_name2': 'Test',
        
        # Dwelling - Single Family 
        'dwelling_single_fam1': 'Yes',
        'dwelling_apt1': 'No',
        'dwelling_condo1': 'No',
        
        # Option A: None selected
        'elec_discount4': 'No',
        'low_income4': 'No',
        'matching_payment_eversource4': 'No',
        'bill_forgive4': 'No',
        'matching_pay_united4': 'No',
        
        # Option B: None selected
        'ebt4': 'No',
        'energy_award_letter4': 'No',
        'section_eight4': 'No',
        
        # Option D: Selected
        'multifam4': 'Yes'
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
    output_path = "TEST_OPTION_D.pdf"
    
    print("🔧 Testing Option D positioning...")
    print("\n📋 Current Option D position:")
    print("   Multifam: (317.0, 357.0)")
    
    # Test with force visible method
    success = processor.fill_pdf_with_force_visible(template_path, document, output_path)
    
    if success:
        print(f"\n✅ Option D test PDF created: {output_path}")
        print(f"📂 File location: {os.path.abspath(output_path)}")
        print("\n🔍 CHECK THE PDF:")
        print("   - Page 3: Single family dwelling checkbox should be visible")
        print("   - Page 4: ONLY Option D checkbox should be visible")
        print("   - Option D visual indicator should be positioned correctly")
        print("\n⚠️  Check if Option D position needs adjustment!")
    else:
        print("❌ Failed to create Option D test PDF")

if __name__ == "__main__":
    test_option_d()