#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_property_owner_fields():
    """Test property owner city, state, zip fields that were missing on website"""
    
    # Test data with property owner fields using frontend field names
    form_data = {
        # Basic info
        'property_address1': '123 Property Owner Test Street',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'first_name2': 'John',
        'last_name2': 'PropertyOwner',
        
        # Dwelling - Single Family 
        'dwelling_single_fam1': 'Yes',
        'dwelling_apt1': 'No',
        'dwelling_condo1': 'No',
        
        # Property Owner section - Testing the missing fields
        'landlord_name3': 'Jane Smith',
        'address3': '456 Owner Avenue',
        'city3': 'Cambridge',           # ✅ PROPERTY OWNER CITY
        'text_55cits': 'MA',           # ✅ PROPERTY OWNER STATE  
        'text_56qpfj': '02139',        # ✅ PROPERTY OWNER ZIP
        'phone3': '617-555-9999',
        'email3': 'jane.smith@owner.com',
        
        # Signatures and dates
        'signature3': 'John PropertyOwner',
        'property_ower_sig3': 'Jane Smith',
        'date': '12/15/2024'
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
    output_path = "TEST_PROPERTY_OWNER_FIELDS.pdf"
    
    print("🔧 Testing Property Owner City, State, ZIP fields...")
    print("\n📋 Property Owner fields being tested:")
    print("   Name: Jane Smith")
    print("   Address: 456 Owner Avenue") 
    print("   City: Cambridge         ✅ TESTING THIS FIELD")
    print("   State: MA               ✅ TESTING THIS FIELD")
    print("   ZIP: 02139              ✅ TESTING THIS FIELD")
    print("   Phone: 617-555-9999")
    print("   Email: jane.smith@owner.com")
    
    # Test with force visible method
    success = processor.fill_pdf_with_force_visible(template_path, document, output_path)
    
    if success:
        print(f"\n✅ Property Owner fields test PDF created: {output_path}")
        print(f"📂 File location: {os.path.abspath(output_path)}")
        print("\n🔍 CHECK THE PDF:")
        print("   - Page 3: Property Owner section should be completely filled")
        print("   - VERIFY: City = 'Cambridge'")
        print("   - VERIFY: State = 'MA'")
        print("   - VERIFY: ZIP = '02139'")
        print("   - All other property owner fields should also be filled")
        print("\n⚠️  This tests the exact fields that were missing on the website!")
    else:
        print("❌ Failed to create Property Owner fields test PDF")

if __name__ == "__main__":
    test_property_owner_fields()