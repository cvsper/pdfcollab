#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_frontend_options_mapping():
    """Test how frontend form data maps to PDF options"""
    
    # Test 1: Frontend-style form data (as app.py expects)
    print("🔍 Test 1: Frontend-style form data")
    frontend_form_data = {
        # Basic info
        'property_address': '123 Frontend Test St',
        'city': 'Boston',
        'state': 'MA',
        'zip_code': '02101',
        'first_name': 'Frontend',
        'last_name': 'Test',
        
        # Dwelling type
        'dwelling_type': 'apartment',
        
        # Option A: Utility programs (array format)
        'utility_program': ['electric_discount', 'low_income_discount', 'matching_payment', 'bill_forgiveness', 'matching_payment_united'],
        
        # Option B: Documentation (array format)
        'documentation': ['ebt_award', 'energy_assistance', 'section_8'],
        
        # Option D: Qualification option
        'qualification_option': 'option_d'
    }
    
    # Test 2: Direct PDF field names (as PDF processor expects)
    print("\n🔍 Test 2: Direct PDF field names")
    direct_pdf_data = {
        # Basic info with PDF field names
        'property_address1': '456 Direct Test Ave',
        'city1': 'Cambridge',
        'state1': 'MA',
        'zip1': '02139',
        'first_name2': 'Direct',
        'last_name2': 'Test',
        
        # Dwelling checkboxes
        'dwelling_single_fam1': 'No',
        'dwelling_apt1': 'Yes',
        'dwelling_condo1': 'No',
        
        # Option A: Direct checkbox values
        'elec_discount4': 'Yes',
        'low_income4': 'Yes',
        'matching_payment_eversource4': 'Yes',
        'bill_forgive4': 'Yes',
        'matching_pay_united4': 'Yes',
        
        # Option B: Direct checkbox values
        'ebt4': 'Yes',
        'energy_award_letter4': 'Yes',
        'section_eight4': 'Yes',
        
        # Option D: Direct checkbox value
        'multifam4': 'Yes'
    }
    
    # Initialize PDF processor
    processor = PDFProcessor()
    template_path = "homworks.pdf"
    
    # Test frontend-style data
    document1 = {
        'user1_data': frontend_form_data,
        'user2_data': {},
        'file_path': template_path
    }
    
    output_path1 = "TEST_FRONTEND_STYLE_OPTIONS.pdf"
    print("\n🔧 Testing frontend-style data...")
    success1 = processor.fill_pdf_with_force_visible(template_path, document1, output_path1)
    
    if success1:
        print(f"✅ Frontend-style test created: {output_path1}")
        print("⚠️  Check if Options A, B, D are filled correctly")
    else:
        print("❌ Frontend-style test failed")
    
    # Test direct PDF field names
    document2 = {
        'user1_data': direct_pdf_data,
        'user2_data': {},
        'file_path': template_path
    }
    
    output_path2 = "TEST_DIRECT_PDF_OPTIONS.pdf"
    print("\n🔧 Testing direct PDF field names...")
    success2 = processor.fill_pdf_with_force_visible(template_path, document2, output_path2)
    
    if success2:
        print(f"✅ Direct PDF test created: {output_path2}")
        print("✅ Options A, B, D should all be filled correctly")
    else:
        print("❌ Direct PDF test failed")
    
    print("\n📊 Summary:")
    print("1. TEST_FRONTEND_STYLE_OPTIONS.pdf - Uses array format (utility_program, documentation)")
    print("2. TEST_DIRECT_PDF_OPTIONS.pdf - Uses direct field names (elec_discount4, ebt4, etc.)")
    print("\n⚠️  If frontend-style doesn't work but direct does, the issue is in app.py field mapping!")

if __name__ == "__main__":
    test_frontend_options_mapping()