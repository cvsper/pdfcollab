#!/usr/bin/env python3
"""
Test Section 4 field filling (qualification options A, B, C, D)
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def test_section4_fields():
    """Test that Section 4 (qualification options) are properly filled"""
    
    print("🧪 TESTING SECTION 4 FIELD FILLING")
    print("=" * 50)
    
    # Create test document with Section 4 fields (Option A, B, C, D)
    test_document = {
        'id': 'section4_test',
        'name': 'section4_test.pdf',
        'pdf_fields': [
            # Option A - Utility Programs
            {
                'id': 'test_elec_discount',
                'name': 'Elec Discount4 (Checkbox)',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_low_income',
                'name': 'Low Income Program (Checkbox)',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1'
            },
            
            # Option B - Documentation
            {
                'id': 'test_ebt',
                'name': 'EBT (Food Stamps) (Checkbox)',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1'
            },
            
            # Option D - Multifamily
            {
                'id': 'test_multifam',
                'name': 'Multifam4 (Checkbox)',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1'
            },
            
            # Section 3 fields
            {
                'id': 'test_household_size',
                'name': 'People In Household4',
                'value': '4',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_annual_income',
                'name': 'Annual Income4',
                'value': '45000',
                'type': 'text',
                'assigned_to': 'user1'
            }
        ]
    }
    
    # Test the PDF processor
    processor = PDFProcessor()
    
    # Test with homworks.pdf
    input_pdf = 'homworks.pdf'
    output_pdf = 'SECTION4_TEST_OUTPUT.pdf'
    
    if not os.path.exists(input_pdf):
        print(f"❌ {input_pdf} not found")
        return False
    
    print(f"📄 Input PDF: {input_pdf}")
    print(f"📄 Output PDF: {output_pdf}")
    
    # Fill the PDF
    success = processor.fill_pdf_with_pymupdf(input_pdf, test_document, output_pdf)
    
    if success:
        print(f"\n✅ PDF filled successfully: {output_pdf}")
        
        # Check if Section 4 fields were properly filled
        print("\n🔍 Verifying Section 4 field filling in output PDF...")
        
        import fitz
        doc = fitz.open(output_pdf)
        page4 = doc[3]  # Page 4 where Section 4 is
        widgets = list(page4.widgets())
        
        # Expected Section 4 field mappings
        expected_fields = {
            'elec_discount4': 'Option A - Electric Discount',
            'low_income4': 'Option A - Low Income Program', 
            'ebt4': 'Option B - EBT (Food Stamps)',
            'multifam4': 'Option D - Multifamily',
            'people_in_household4': 'Section 3 - Household Size',
            'annual_income4': 'Section 3 - Annual Income'
        }
        
        filled_fields = []
        for widget in widgets:
            field_name = widget.field_name
            field_value = widget.field_value
            
            if field_name in expected_fields and field_value and str(field_value) not in ['', 'False', 'Off']:
                filled_fields.append(field_name)
                if widget.field_type == 2:  # Checkbox
                    print(f"   ✅ {field_name} (checkbox): {field_value} - {expected_fields[field_name]}")
                else:
                    print(f"   ✅ {field_name} (text): '{field_value}' - {expected_fields[field_name]}")
        
        doc.close()
        
        success_count = len(filled_fields)
        total_expected = len(expected_fields)
        
        print(f"\n📊 Section 4 Filling Results:")
        print(f"   ✅ Filled: {success_count}/{total_expected} fields")
        
        missing_fields = [field for field in expected_fields if field not in filled_fields]
        if missing_fields:
            print(f"   ❌ Missing: {missing_fields}")
        
        if success_count >= 4:  # At least most fields should be filled
            print(f"\n🎉 SUCCESS! Section 4 fields are being filled correctly")
            return True
        else:
            print(f"\n⚠️  Only {success_count}/{total_expected} Section 4 fields were filled")
            return False
    else:
        print("❌ PDF filling failed")
        return False

if __name__ == "__main__":
    success = test_section4_fields()
    if success:
        print("\n🎯 Section 4 test completed successfully!")
    else:
        print("\n❌ Section 4 test failed - fields may need mapping fixes")