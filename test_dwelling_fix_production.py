#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_dwelling_fix_production():
    """Test the dwelling fix for production"""
    
    # Test data with dwelling fields as they come from app.py
    form_data = {
        # Basic info
        'property_address1': '789 Production Test St',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'first_name2': 'Jane',
        'last_name2': 'Smith',
        'phone2': '617-555-9999',
        'email2': 'jane@example.com',
        
        # Dwelling checkboxes - apartment selected
        'dwelling_single_fam1': 'No',
        'dwelling_apt1': 'Yes',  # This should be checked
        'dwelling_condo1': 'No',
        
        # Other fields
        'fuel_type_elec2': 'Yes',
        'owner2': 'No',
        'renter2': 'Yes'
    }
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Create document structure as app.py would
    document = {
        'user1_data': form_data,
        'user2_data': {},
        'file_path': 'homworks.pdf'
    }
    
    template_path = "homworks.pdf"
    output_path = "TEST_DWELLING_FIX_PRODUCTION.pdf"
    
    # Test the force visible method that production uses
    print("🔧 Testing fill_pdf_with_force_visible (production method)...")
    success = processor.fill_pdf_with_force_visible(template_path, document, output_path)
    
    if success:
        print(f"\n✅ Test PDF created: {output_path}")
        print("\n📊 Expected results:")
        print("   ✓ Apartment checkbox should be checked")
        print("   ✓ Visual indicator should appear for Apartment")
        print("   ✓ All form fields should be filled")
    else:
        print("❌ Failed to create test PDF")

if __name__ == "__main__":
    test_dwelling_fix_production()