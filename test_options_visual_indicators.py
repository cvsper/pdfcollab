#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_options_visual_indicators():
    """Test visual indicators for Options A, B, and D"""
    
    # Test data with ALL options selected
    form_data = {
        # Basic info
        'property_address1': '123 Visual Test Street',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'first_name2': 'Visual',
        'last_name2': 'TestUser',
        
        # Dwelling - Single Family (for variety)
        'dwelling_single_fam1': 'Yes',
        'dwelling_apt1': 'No',
        'dwelling_condo1': 'No',
        
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
    output_path = "TEST_OPTIONS_VISUAL_INDICATORS.pdf"
    
    print("🔧 Testing visual indicators for Options A, B, and D...")
    print("\n📋 Expected visual indicators:")
    print("   ✓ Option A: 5 checkboxes with checkmarks")
    print("     - Electric Discount (left column, top)")
    print("     - Matching Payment Eversource (left column)")
    print("     - Low Income Program (right column, top)")
    print("     - Bill Forgiveness (right column)")
    print("     - Matching Payment United (right column, bottom)")
    print("   ✓ Option B: 3 checkboxes with checkmarks")
    print("     - EBT (Food Stamps)")
    print("     - Energy Award Letter")
    print("     - Section Eight")
    print("   ✓ Option D: 1 checkbox with checkmark")
    print("     - Multifamily (right side)")
    print("   ✓ Dwelling: Single Family checkbox with checkmark")
    
    # Test with force visible method
    success = processor.fill_pdf_with_force_visible(template_path, document, output_path)
    
    if success:
        print(f"\n✅ Visual indicators test PDF created: {output_path}")
        print(f"📂 File location: {os.path.abspath(output_path)}")
        print("\n🔍 CHECK THE PDF:")
        print("   - Page 3: Should show single family dwelling checkbox")
        print("   - Page 4: Should show ALL Options A, B, D checkboxes with borders and checkmarks")
        print("\n⚠️  If boxes appear but are in wrong positions, we'll need to adjust coordinates!")
    else:
        print("❌ Failed to create visual indicators test PDF")

if __name__ == "__main__":
    test_options_visual_indicators()