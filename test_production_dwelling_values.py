#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_production_dwelling_values():
    """Test exactly how dwelling values should be set in production"""
    
    # Test data mimicking production form submission
    form_data = {
        # Basic info
        'property_address1': '123 Main St',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'first_name2': 'John',
        'last_name2': 'Doe',
        
        # CRITICAL: Test different dwelling value formats
        # Production might be sending these differently
        'dwelling_single_fam1': 'No',
        'dwelling_apt1': 'Yes',  # Selected dwelling type
        'dwelling_condo1': 'No',
    }
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Create document structure
    document = {
        'user1_data': form_data,
        'user2_data': {}
    }
    
    # Test 1: Direct field filling
    print("🔍 Test 1: Direct field value setting")
    template_path = "homworks.pdf"
    output_path = "TEST_DWELLING_VALUES_PRODUCTION.pdf"
    
    success = processor.fill_pdf_with_pymupdf(template_path, document, output_path)
    print(f"✅ Basic fill completed: {success}")
    
    # Test 2: Check how app.py handles dwelling_type
    print("\n🔍 Test 2: Testing app.py dwelling_type handling")
    
    # This is how app.py processes dwelling_type
    app_style_data = {
        'dwelling_type': 'apartment',  # app.py uses this format
        'property_address1': '456 Oak Ave',
        'city1': 'Cambridge',
        'state1': 'MA',
        'zip1': '02139'
    }
    
    # Create a mapping test
    dwelling_mappings = {
        'single_family': 'dwelling_single_fam1',
        'apartment': 'dwelling_apt1', 
        'condominium': 'dwelling_condo1'
    }
    
    # Convert dwelling_type to individual checkbox values
    dwelling_type = app_style_data.get('dwelling_type')
    if dwelling_type:
        print(f"   Processing dwelling_type: {dwelling_type}")
        
        # Set all dwelling checkboxes to No first
        for key, pdf_field in dwelling_mappings.items():
            app_style_data[pdf_field] = 'No'
            print(f"   Set {pdf_field} = No")
        
        # Set selected dwelling to Yes
        selected_pdf_field = dwelling_mappings.get(dwelling_type)
        if selected_pdf_field:
            app_style_data[selected_pdf_field] = 'Yes'
            print(f"   Set {selected_pdf_field} = Yes")
    
    # Create document and process
    document2 = {
        'user1_data': app_style_data,
        'user2_data': {}
    }
    
    output_path2 = "TEST_DWELLING_APP_STYLE.pdf"
    success2 = processor.fill_pdf_with_pymupdf(template_path, document2, output_path2)
    print(f"\n✅ App-style fill completed: {success2}")
    
    # Test 3: Try different checkbox values
    print("\n🔍 Test 3: Testing different checkbox value formats")
    test_values = ['Yes', 'true', 'True', 'checked', '1', True]
    
    for i, test_val in enumerate(test_values):
        test_data = {
            'dwelling_single_fam1': 'No',
            'dwelling_apt1': test_val,  # Try different values
            'dwelling_condo1': 'No',
            'property_address1': f'Test {i+1}',
        }
        
        document3 = {
            'user1_data': test_data,
            'user2_data': {}
        }
        
        output_path3 = f"TEST_DWELLING_VALUE_{i+1}.pdf"
        success3 = processor.fill_pdf_with_pymupdf(template_path, document3, output_path3)
        print(f"   Value '{test_val}' (type: {type(test_val).__name__}): {success3}")
    
    print("\n📊 Summary:")
    print("1. Check TEST_DWELLING_VALUES_PRODUCTION.pdf - basic field values")
    print("2. Check TEST_DWELLING_APP_STYLE.pdf - app.py style processing")
    print("3. Check TEST_DWELLING_VALUE_*.pdf files - different value formats")
    print("\n⚠️  If dwelling checkboxes aren't visible in any of these, the issue is:")
    print("   - PDF form field visibility settings")
    print("   - Need to use visual indicators (already implemented)")
    print("   - Field value format mismatch")

if __name__ == "__main__":
    test_production_dwelling_values()