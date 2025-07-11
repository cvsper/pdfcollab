#!/usr/bin/env python3
"""
Test the fixed date field mapping to ensure dates appear in PDF
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def test_date_field_mapping():
    """Test that date fields are properly mapped to specific widget names"""
    
    print("🧪 TESTING DATE FIELD MAPPING FIX")
    print("=" * 50)
    
    # Create test document with date fields at specific Y positions
    test_document = {
        'id': 'date_field_test',
        'name': 'date_field_test.pdf',
        'pdf_fields': [
            {
                'id': 'test_auth_date',
                'name': 'Date',  # Generic name that needs position-based mapping
                'value': '2025-07-11',
                'type': 'text',
                'assigned_to': 'user2',
                'position': {'x': 200, 'y': 471.0}  # Near Applicant Signature
            },
            {
                'id': 'test_owner_date',
                'name': 'Date',  # Generic name that needs position-based mapping
                'value': '2025-07-11',
                'type': 'text',
                'assigned_to': 'user2',
                'position': {'x': 200, 'y': 643.0}  # Near Property Owner Signature
            },
            {
                'id': 'test_signature1',
                'name': 'Applicant Signature',
                'value': 'John Smith',
                'type': 'signature',
                'assigned_to': 'user2',
                'position': {'x': 43, 'y': 440}
            },
            {
                'id': 'test_signature2',
                'name': 'Property Owner Signature',
                'value': 'Jane Smith',
                'type': 'signature',
                'assigned_to': 'user2',
                'position': {'x': 43, 'y': 612}
            }
        ]
    }
    
    # Test the PDF processor
    processor = PDFProcessor()
    
    # Test with homworks.pdf
    input_pdf = 'homworks.pdf'
    output_pdf = 'DATE_FIELD_TEST_OUTPUT.pdf'
    
    if not os.path.exists(input_pdf):
        print(f"❌ {input_pdf} not found")
        return False
    
    print(f"📄 Input PDF: {input_pdf}")
    print(f"📄 Output PDF: {output_pdf}")
    
    # Fill the PDF
    success = processor.fill_pdf_with_pymupdf(input_pdf, test_document, output_pdf)
    
    if success:
        print(f"\n✅ PDF filled successfully: {output_pdf}")
        
        # Check if date fields were properly mapped
        print("\n🔍 Verifying date field mapping in output PDF...")
        
        import fitz
        doc = fitz.open(output_pdf)
        page = doc[2]  # Page 3 where signatures are
        widgets = list(page.widgets())
        
        date_widgets_found = []
        for widget in widgets:
            if 'date' in widget.field_name.lower():
                field_value = widget.field_value
                print(f"   📅 {widget.field_name}: '{field_value}' at y={widget.rect.y0}")
                if field_value and str(field_value) != '':
                    date_widgets_found.append(widget.field_name)
        
        doc.close()
        
        expected_date_fields = ['date3', 'date_property_mang3']
        success_count = 0
        
        for expected_field in expected_date_fields:
            if expected_field in date_widgets_found:
                print(f"   ✅ {expected_field} was filled correctly")
                success_count += 1
            else:
                print(f"   ❌ {expected_field} was NOT filled")
        
        if success_count == len(expected_date_fields):
            print(f"\n🎉 SUCCESS! All {success_count} date fields were filled correctly")
            print("✅ Date field mapping fix is working!")
            return True
        else:
            print(f"\n⚠️  Only {success_count}/{len(expected_date_fields)} date fields were filled")
            return False
    else:
        print("❌ PDF filling failed")
        return False

if __name__ == "__main__":
    success = test_date_field_mapping()
    if success:
        print("\n🎯 Test completed successfully!")
    else:
        print("\n❌ Test failed - date field mapping needs more work")