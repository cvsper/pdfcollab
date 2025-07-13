#!/usr/bin/env python3
"""
Test dwelling types specifically to ensure they appear in downloaded PDFs
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import fitz

def test_dwelling_types():
    """Test that dwelling type selection works end-to-end"""
    
    print("🏠 TESTING DWELLING TYPES IN SECTION 1")
    print("=" * 50)
    
    # Test all three dwelling types
    dwelling_tests = [
        ('single_family', 'Single Family Home (Checkbox)', 'dwelling_single_fam1'),
        ('apartment', 'Apartment (Checkbox)', 'dwelling_apt1'), 
        ('condominium', 'Condominium (Checkbox)', 'dwelling_condo1')
    ]
    
    for i, (form_value, display_name, pdf_field) in enumerate(dwelling_tests):
        print(f"\n🔍 TEST {i+1}: {form_value} → {display_name}")
        
        # Create test document with this dwelling type
        test_doc = {
            'id': f'dwelling_test_{i+1}',
            'pdf_fields': [
                # Basic property info
                {
                    'id': 'prop_addr',
                    'name': 'Property Address',
                    'value': f'123 {form_value.title()} Street',
                    'type': 'text',
                    'assigned_to': 'user1',
                    'pdf_field_name': 'property_address1'
                },
                # The dwelling type checkbox
                {
                    'id': f'dwelling_{i+1}',
                    'name': display_name,
                    'value': 'true',
                    'type': 'checkbox', 
                    'assigned_to': 'user1',
                    'pdf_field_name': pdf_field
                }
            ]
        }
        
        # Fill the PDF
        processor = PDFProcessor()
        output_file = f'DWELLING_TEST_{form_value.upper()}.pdf'
        success = processor.fill_pdf_with_pymupdf('homworks.pdf', test_doc, output_file)
        
        if success:
            print(f"   ✅ PDF created: {output_file}")
            
            # Verify the dwelling type was filled
            doc = fitz.open(output_file)
            page = doc[2]  # Page 3 has the form
            widgets = list(page.widgets())
            
            dwelling_filled = False
            property_filled = False
            
            for widget in widgets:
                field_name = widget.field_name
                field_value = widget.field_value
                
                if field_name == pdf_field:
                    if field_value and str(field_value) not in ['', 'False', 'Off']:
                        dwelling_filled = True
                        print(f"   ✅ Dwelling checkbox filled: {field_name} = {field_value}")
                    else:
                        print(f"   ❌ Dwelling checkbox NOT filled: {field_name} = {field_value}")
                
                elif field_name == 'property_address1':
                    if field_value:
                        property_filled = True
                        print(f"   ✅ Property address filled: {field_value}")
            
            doc.close()
            
            if dwelling_filled and property_filled:
                print(f"   🎉 SUCCESS: {form_value} dwelling type works correctly!")
            else:
                print(f"   ⚠️  ISSUE: {form_value} dwelling type not working")
                
        else:
            print(f"   ❌ Failed to create PDF for {form_value}")
    
    # Test comprehensive form with dwelling type
    print(f"\n🎯 COMPREHENSIVE TEST: Full form with dwelling type")
    
    comprehensive_doc = {
        'id': 'comprehensive_dwelling_test',
        'pdf_fields': [
            # Section 1: Property Information
            {'id': 'addr', 'name': 'Property Address', 'value': '456 Comprehensive Avenue', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'apt', 'name': 'Apartment Number', 'value': 'Unit 2B', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'city', 'name': 'City', 'value': 'Hartford', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'state', 'name': 'State', 'value': 'CT', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'zip', 'name': 'ZIP Code', 'value': '06103', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'apt_count', 'name': 'Number of Apartments', 'value': '12', 'type': 'text', 'assigned_to': 'user1'},
            
            # Section 1: Dwelling Type (select apartment)
            {'id': 'dwelling', 'name': 'Apartment (Checkbox)', 'value': 'true', 'type': 'checkbox', 'assigned_to': 'user1'},
            
            # Section 2: Personal Info
            {'id': 'fname', 'name': 'First Name', 'value': 'Maria', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'lname', 'name': 'Last Name', 'value': 'Rodriguez', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'phone', 'name': 'Phone Number', 'value': '860-555-1234', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'email', 'name': 'Email Address', 'value': 'maria@test.com', 'type': 'text', 'assigned_to': 'user1'},
        ]
    }
    
    processor = PDFProcessor()
    output_file = 'COMPREHENSIVE_DWELLING_TEST.pdf'
    success = processor.fill_pdf_with_pymupdf('homworks.pdf', comprehensive_doc, output_file)
    
    if success:
        print(f"   ✅ Comprehensive PDF created: {output_file}")
        
        # Check all Section 1 fields
        doc = fitz.open(output_file)
        page = doc[2]
        widgets = list(page.widgets())
        
        section1_fields = {
            'property_address1': 'Property Address',
            'apt_num1': 'Apartment Number', 
            'city1': 'City',
            'state1': 'State',
            'zip1': 'ZIP Code',
            'num_of_apt1': 'Number of Apartments',
            'dwelling_apt1': 'Apartment Type'
        }
        
        filled_count = 0
        for widget in widgets:
            if widget.field_name in section1_fields:
                if widget.field_value and str(widget.field_value) not in ['', 'False', 'Off']:
                    filled_count += 1
                    field_desc = section1_fields[widget.field_name]
                    print(f"   ✅ {field_desc}: {widget.field_value}")
        
        doc.close()
        
        print(f"\n📊 Section 1 Summary: {filled_count}/{len(section1_fields)} fields filled")
        
        if filled_count == len(section1_fields):
            print("🎉 ALL SECTION 1 FIELDS INCLUDING DWELLING TYPE ARE WORKING!")
        else:
            missing = len(section1_fields) - filled_count
            print(f"⚠️  {missing} Section 1 fields still missing")
    
    else:
        print("❌ Comprehensive test failed")

if __name__ == "__main__":
    test_dwelling_types()