#!/usr/bin/env python3
"""
Test that fills EVERY SINGLE FIELD in the PDF to see what's missing
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import fitz

def test_fill_everything():
    """Fill every single field in the PDF with test data"""
    
    print("🔍 COMPREHENSIVE TEST - FILL EVERY FIELD IN PDF")
    print("=" * 60)
    
    # First, extract all fields from the PDF to know what we're working with
    processor = PDFProcessor()
    pdf_path = 'homworks.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ {pdf_path} not found")
        return False
    
    # Extract all fields
    result = processor.extract_fields_with_pymupdf(pdf_path)
    if "error" in result:
        print(f"❌ Error extracting fields: {result['error']}")
        return False
    
    all_fields = result['fields']
    print(f"📋 Found {len(all_fields)} fields in the PDF")
    
    # Create a test document that fills EVERY field
    test_document = {
        'id': 'fill_everything_test',
        'name': 'fill_everything_test.pdf',
        'pdf_fields': []
    }
    
    # Fill every field with test data based on its type
    for i, field in enumerate(all_fields):
        field_name = field['name']
        field_type = field['type']
        pdf_field_name = field.get('pdf_field_name', field_name)
        
        # Generate appropriate test data based on field type
        if field_type == 'text':
            if 'signature' in field_name.lower() or 'sig' in field_name.lower():
                test_value = f"Test Signature {i+1}"
            elif 'date' in field_name.lower():
                test_value = "07/13/2025"
            elif 'phone' in field_name.lower() or 'tel' in field_name.lower():
                test_value = f"860-555-{1000+i:04d}"
            elif 'email' in field_name.lower():
                test_value = f"test{i+1}@example.com"
            elif 'zip' in field_name.lower():
                test_value = f"{6000+i:05d}"
            elif 'state' in field_name.lower():
                test_value = "CT"
            elif 'address' in field_name.lower():
                test_value = f"{100+i} Test Street"
            elif 'city' in field_name.lower():
                test_value = "TestCity"
            elif 'name' in field_name.lower():
                test_value = f"Test Name {i+1}"
            elif 'number' in field_name.lower() or 'num' in field_name.lower():
                test_value = f"{12345+i}"
            elif 'income' in field_name.lower():
                test_value = f"{30000+i*1000}"
            else:
                test_value = f"Test_{field_name}_{i+1}"
        
        elif field_type == 'checkbox':
            test_value = 'true'  # Check all checkboxes
        
        elif field_type == 'radio' or field_type == 'combobox':
            test_value = 'true'  # Select all radio buttons
        
        elif field_type == 'signature':
            test_value = f"Signature Test {i+1}"
        
        else:
            test_value = f"Test_{field_type}_{i+1}"
        
        # Add field with test value
        test_field = {
            'id': f'test_{i}',
            'name': field_name,
            'pdf_field_name': pdf_field_name,
            'value': test_value,
            'type': field_type,
            'assigned_to': 'user2' if 'signature' in field_name.lower() or (field_name == 'Date' and field.get('position', {}).get('y', 0) > 400) else 'user1',
            'position': field.get('position', {}),
            'page': field.get('page', 0)
        }
        
        test_document['pdf_fields'].append(test_field)
        print(f"   {i+1:2d}. {field_name:<35} = '{test_value}'")
    
    print(f"\n🎯 Filling PDF with {len(test_document['pdf_fields'])} test values...")
    
    # Fill the PDF
    output_pdf = 'FILL_EVERYTHING_TEST.pdf'
    success = processor.fill_pdf_with_pymupdf(pdf_path, test_document, output_pdf)
    
    if success:
        print(f"\n✅ PDF filled successfully: {output_pdf}")
        
        # Now verify what was actually filled
        print("\n🔍 Verifying which fields were filled...")
        
        doc = fitz.open(output_pdf)
        filled_fields = []
        unfilled_fields = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            for widget in widgets:
                field_name = widget.field_name
                field_value = widget.field_value
                field_type = widget.field_type
                
                if field_value and str(field_value) not in ['', 'False', 'Off']:
                    filled_fields.append({
                        'name': field_name,
                        'value': field_value,
                        'type': field_type,
                        'page': page_num + 1
                    })
                else:
                    unfilled_fields.append({
                        'name': field_name,
                        'type': field_type,
                        'page': page_num + 1
                    })
        
        doc.close()
        
        # Report results
        print(f"\n📊 RESULTS:")
        print(f"   ✅ Filled fields: {len(filled_fields)}/{len(all_fields)}")
        print(f"   ❌ Unfilled fields: {len(unfilled_fields)}")
        
        if unfilled_fields:
            print(f"\n⚠️  MISSING FIELDS (not filled):")
            for field in unfilled_fields:
                # Find the original field to get more info
                original_field = next((f for f in all_fields if f.get('pdf_field_name', f['name']) == field['name']), None)
                if original_field:
                    print(f"   ❌ {field['name']} (page {field['page']}, type: {field['type']})")
                    print(f"      Display name: {original_field['name']}")
                    print(f"      Position: {original_field.get('position', 'unknown')}")
        
        # Group filled fields by page
        print(f"\n📄 FILLED FIELDS BY PAGE:")
        for page_num in range(1, 6):
            page_fields = [f for f in filled_fields if f['page'] == page_num]
            if page_fields:
                print(f"\n   Page {page_num}: {len(page_fields)} fields")
                for field in page_fields[:5]:  # Show first 5 fields per page
                    print(f"      ✅ {field['name']}: '{field['value']}'")
                if len(page_fields) > 5:
                    print(f"      ... and {len(page_fields) - 5} more fields")
        
        # Success criteria
        fill_rate = len(filled_fields) / len(all_fields) * 100 if all_fields else 0
        print(f"\n📈 FILL RATE: {fill_rate:.1f}%")
        
        if fill_rate >= 95:
            print(f"\n🎉 EXCELLENT! Nearly all fields are being filled!")
            return True
        elif fill_rate >= 80:
            print(f"\n✅ GOOD! Most fields are being filled, but some are missing.")
            return True
        else:
            print(f"\n⚠️  LOW FILL RATE! Many fields are not being filled.")
            return False
    else:
        print("❌ PDF filling failed")
        return False

if __name__ == "__main__":
    success = test_fill_everything()
    if success:
        print("\n🎯 Test completed! Check FILL_EVERYTHING_TEST.pdf to see all filled fields.")
    else:
        print("\n❌ Test revealed significant issues with field filling.")