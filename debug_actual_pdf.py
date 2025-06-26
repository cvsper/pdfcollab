#!/usr/bin/env python3
"""
Debug the actual homeworks.pdf file to see why fields aren't appearing
"""

import os
import fitz
from pdf_processor import PDFProcessor

def debug_actual_pdf():
    """Debug the actual PDF file step by step"""
    print("🔍 DEBUGGING ACTUAL PDF FILE")
    print("=" * 50)
    
    processor = PDFProcessor()
    
    # Use the actual PDF file
    input_pdf = 'homeworks.pdf'
    output_pdf = 'DEBUG_ACTUAL_OUTPUT.pdf'
    
    if not os.path.exists(input_pdf):
        print(f"❌ PDF file not found: {input_pdf}")
        return False
    
    print(f"📄 Testing with: {input_pdf}")
    
    # Step 1: Extract fields to see what's available
    print("\n1️⃣ EXTRACTING FIELDS FROM ACTUAL PDF")
    print("-" * 40)
    
    fields_result = processor.extract_fields_with_pymupdf(input_pdf)
    if 'error' in fields_result:
        print(f"❌ Field extraction failed: {fields_result['error']}")
        return False
    
    fields = fields_result['fields']
    print(f"✅ Found {len(fields)} fields")
    
    # Show some key fields
    print("\n📋 FIELD SUMMARY:")
    text_fields = [f for f in fields if f['type'] == 'text'][:5]
    radio_fields = [f for f in fields if f['type'] == 'radio'][:5]
    checkbox_fields = [f for f in fields if f['type'] == 'checkbox'][:5]
    signature_fields = [f for f in fields if f['type'] == 'signature'][:5]
    
    print(f"   📝 Text fields: {len([f for f in fields if f['type'] == 'text'])}")
    for field in text_fields:
        print(f"      - {field['name']} ({field.get('pdf_field_name', 'N/A')})")
    
    print(f"   🔘 Radio fields: {len([f for f in fields if f['type'] == 'radio'])}")
    for field in radio_fields:
        print(f"      - {field['name']} ({field.get('pdf_field_name', 'N/A')})")
    
    print(f"   ✅ Checkbox fields: {len([f for f in fields if f['type'] == 'checkbox'])}")
    for field in checkbox_fields:
        print(f"      - {field['name']} ({field.get('pdf_field_name', 'N/A')})")
    
    print(f"   ✍️  Signature fields: {len([f for f in fields if f['type'] == 'signature'])}")
    for field in signature_fields:
        print(f"      - {field['name']} ({field.get('pdf_field_name', 'N/A')})")
    
    # Step 2: Create test document with actual field names
    print("\n2️⃣ CREATING TEST DOCUMENT WITH ACTUAL FIELDS")
    print("-" * 40)
    
    test_document = {
        'id': 'actual_pdf_debug',
        'name': 'debug_test.pdf',
        'pdf_fields': []
    }
    
    # Add some text fields
    for field in text_fields[:2]:
        test_document['pdf_fields'].append({
            'id': f"test_{field['id']}",
            'name': field['name'],
            'pdf_field_name': field.get('pdf_field_name', field['name']),
            'value': f"DEBUG TEST: {field['name']}",
            'type': 'text',
            'assigned_to': 'user1',
            'position': field.get('position', {}),
            'page': field.get('page', 0)
        })
    
    # Add some radio fields - set to yes
    for field in radio_fields[:2]:
        test_document['pdf_fields'].append({
            'id': f"test_{field['id']}",
            'name': field['name'],
            'pdf_field_name': field.get('pdf_field_name', field['name']),
            'value': 'yes',
            'type': 'radio',
            'assigned_to': 'user1',
            'position': field.get('position', {}),
            'page': field.get('page', 0)
        })
    
    # Add some checkbox fields - set to true
    for field in checkbox_fields[:2]:
        test_document['pdf_fields'].append({
            'id': f"test_{field['id']}",
            'name': field['name'],
            'pdf_field_name': field.get('pdf_field_name', field['name']),
            'value': 'true',
            'type': 'checkbox',
            'assigned_to': 'user1',
            'position': field.get('position', {}),
            'page': field.get('page', 0)
        })
    
    # Add signature field
    if signature_fields:
        field = signature_fields[0]
        test_document['pdf_fields'].append({
            'id': f"test_{field['id']}",
            'name': field['name'],
            'pdf_field_name': field.get('pdf_field_name', field['name']),
            'value': 'DEBUG SIGNATURE TEST - John Smith',
            'type': 'signature',
            'assigned_to': 'user2',
            'position': field.get('position', {}),
            'page': field.get('page', 0)
        })
    
    print(f"📊 Created test document with {len(test_document['pdf_fields'])} fields")
    
    # Step 3: Fill the PDF
    print("\n3️⃣ FILLING PDF WITH TEST DATA")
    print("-" * 40)
    
    success = processor.fill_pdf_with_pymupdf(input_pdf, test_document, output_pdf)
    
    if not success:
        print("❌ PDF filling failed")
        return False
    
    if not os.path.exists(output_pdf):
        print("❌ Output PDF not created")
        return False
    
    file_size = os.path.getsize(output_pdf)
    print(f"✅ PDF filled successfully: {output_pdf} ({file_size:,} bytes)")
    
    # Step 4: Analyze the result
    print("\n4️⃣ ANALYZING FILLED PDF")
    print("-" * 40)
    
    try:
        doc = fitz.open(output_pdf)
        
        text_filled = 0
        radio_filled = 0
        checkbox_filled = 0
        signature_found = False
        
        # Check form fields
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            for widget in widgets:
                field_name = widget.field_name
                field_value = widget.field_value
                widget_type = processor.get_widget_type(widget)
                
                # Check if our test values are there
                if field_value:
                    if widget_type == 'text' and 'DEBUG TEST' in str(field_value):
                        text_filled += 1
                        print(f"   ✅ TEXT: {field_name} = '{field_value}'")
                    elif widget_type == 'radio' and str(field_value) not in ['False', 'Off', '']:
                        radio_filled += 1
                        print(f"   🔘 RADIO: {field_name} = '{field_value}'")
                    elif widget_type == 'checkbox' and str(field_value) not in ['False', 'Off', '']:
                        checkbox_filled += 1
                        print(f"   ✅ CHECKBOX: {field_name} = '{field_value}'")
        
        # Check for text insertions (signatures)
        signature_text_found = 0
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            if "DEBUG SIGNATURE TEST" in text:
                                signature_text_found += 1
                                print(f"   ✍️  SIGNATURE: Found '{text}' on page {page_num + 1}")
        
        signature_found = signature_text_found > 0
        
        doc.close()
        
        # Step 5: Final results
        print("\n5️⃣ FINAL RESULTS")
        print("-" * 40)
        
        print(f"📝 Text fields filled: {text_filled}")
        print(f"🔘 Radio buttons selected: {radio_filled}")
        print(f"✅ Checkboxes checked: {checkbox_filled}")
        print(f"✍️  Signature inserted: {'Yes' if signature_found else 'No'}")
        
        total_expected = len(test_document['pdf_fields'])
        total_working = text_filled + radio_filled + checkbox_filled + (1 if signature_found else 0)
        
        success_rate = (total_working / total_expected) * 100 if total_expected > 0 else 0
        
        print(f"\n🎯 SUCCESS RATE: {total_working}/{total_expected} = {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 FIELDS ARE WORKING!")
            print(f"📁 Check '{output_pdf}' - fields should be visible")
        else:
            print("❌ FIELDS ARE NOT WORKING PROPERLY")
            print("🔧 There may be an issue with field mapping or PDF structure")
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_actual_pdf()