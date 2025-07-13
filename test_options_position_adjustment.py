#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_options_position_adjustment():
    """Test the adjusted higher positions for Options A, B, D"""
    
    # Test data with ALL options selected
    form_data = {
        # Basic info
        'property_address1': '123 Position Test Street',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'first_name2': 'Position',
        'last_name2': 'TestAdjusted',
        
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
        
        # Option B: ALL 3 documentation types selected
        'ebt4': 'Yes',
        'energy_award_letter4': 'Yes',
        'section_eight4': 'Yes',
        
        # Option D: Multifamily selected
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
    output_path = "TEST_OPTIONS_HIGHER_POSITIONS.pdf"
    
    print("🔧 Testing HIGHER positions for Options A, B, and D...")
    print("\n📋 New Y positions (higher values = higher on page):")
    print("   Option A:")
    print("     - Electric Discount: y=240.0 (was 220.0)")
    print("     - Low Income: y=240.0 (was 220.0)")
    print("     - Matching Payment Eversource: y=252.0 (was 232.0)")
    print("     - Bill Forgiveness: y=251.0 (was 231.0)")
    print("     - Matching Pay United: y=263.0 (was 243.0)")
    print("   Option B:")
    print("     - EBT: y=313.0 (was 293.0)")
    print("     - Energy Award: y=325.0 (was 305.0)")
    print("     - Section Eight: y=337.0 (was 317.0)")
    print("   Option D:")
    print("     - Multifamily: y=357.0 (was 337.0)")
    
    # Test with force visible method
    success = processor.fill_pdf_with_force_visible(template_path, document, output_path)
    
    if success:
        print(f"\n✅ Higher position test PDF created: {output_path}")
        print(f"📂 File location: {os.path.abspath(output_path)}")
        print("\n🔍 CHECK THE PDF:")
        print("   - Page 3: Condominium dwelling checkbox should be visible")
        print("   - Page 4: ALL Options A, B, D checkboxes should be HIGHER")
        print("   - All visual indicators should be repositioned upward")
        print("\n⚠️  If positions are still too low, let me know and I'll move them higher!")
    else:
        print("❌ Failed to create higher position test PDF")

if __name__ == "__main__":
    test_options_position_adjustment()