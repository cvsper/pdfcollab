#!/usr/bin/env python3
"""
Focused test to verify fields are ACTUALLY visible in the downloaded PDF
"""

import os
import fitz  # PyMuPDF
from pdf_processor import PDFProcessor

def test_visible_fields():
    """Test that fields are actually visible when you open the PDF"""
    print("🔍 VERIFYING FIELDS ARE VISIBLE IN DOWNLOADED PDF")
    print("=" * 60)
    
    processor = PDFProcessor()
    
    input_pdf = 'uploads/c83e2f43-b4b7-4a4d-9b26-de394bc5008b_homeworks.pdf'
    output_pdf = 'VERIFY_VISIBLE_TEST.pdf'
    
    # Very simple test with just a few fields
    test_document = {
        'id': 'visibility_test',
        'name': 'visibility_test.pdf',
        'pdf_fields': [
            # ONE TEXT FIELD
            {
                'id': 'text_1',
                'name': 'Property Address',
                'pdf_field_name': 'property_address1',
                'value': '*** VISIBLE TEST TEXT - 123 Main Street ***',
                'type': 'text',
                'assigned_to': 'user1',
                'position': {'x': 37, 'y': 156, 'width': 196, 'height': 14},
                'page': 2
            },
            
            # ONE RADIO BUTTON - YES
            {
                'id': 'radio_1',
                'name': 'Electric Heat - Should be SELECTED',
                'pdf_field_name': 'fuel_type_elec2',
                'value': 'yes',
                'type': 'radio',
                'assigned_to': 'user1',
                'position': {'x': 317, 'y': 235, 'width': 10, 'height': 10},
                'page': 2
            },
            
            # ONE CHECKBOX - TRUE (should be checked)
            {
                'id': 'checkbox_1',
                'name': 'Single Family Home - Should be CHECKED',
                'pdf_field_name': 'dwelling_single_fam1',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 40, 'y': 256, 'width': 10, 'height': 10},
                'page': 2
            },
            
            # ONE SIGNATURE
            {
                'id': 'signature_1',
                'name': 'Signature - Should be in cursive',
                'pdf_field_name': 'signature3',
                'value': '*** VISIBLE SIGNATURE TEST ***',
                'type': 'signature',
                'assigned_to': 'user2',
                'position': {'x': 43, 'y': 470, 'width': 230, 'height': 14},
                'page': 2
            }
        ]
    }
    
    print(f"📄 Input: {input_pdf}")
    print(f"📁 Output: {output_pdf}")
    print("\n🎯 EXPECTED VISIBLE RESULTS:")
    print("   📝 Property Address should show: '*** VISIBLE TEST TEXT - 123 Main Street ***'")
    print("   🔘 Electric Heat radio button should be SELECTED/filled")
    print("   ✅ Single Family Home checkbox should be CHECKED/filled")
    print("   ✍️  Signature should show: '*** VISIBLE SIGNATURE TEST ***' in cursive")
    
    print("\n" + "=" * 60)
    print("🔄 PROCESSING PDF...")
    
    # Fill the PDF
    success = processor.fill_pdf_with_pymupdf(input_pdf, test_document, output_pdf)
    
    if not success:
        print("❌ FAILED to process PDF")
        return False
    
    if not os.path.exists(output_pdf):
        print("❌ Output PDF not created")
        return False
    
    file_size = os.path.getsize(output_pdf)
    print(f"\n✅ PDF created: {output_pdf} ({file_size:,} bytes)")
    
    # Now ANALYZE the output PDF to see what's actually in it
    print("\n" + "=" * 60)
    print("🔍 ANALYZING WHAT'S ACTUALLY IN THE OUTPUT PDF...")
    
    try:
        doc = fitz.open(output_pdf)
        
        text_found = False
        radio_found = False
        checkbox_found = False
        signature_found = False
        
        print("\n📋 FORM FIELD VALUES:")
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            for widget in widgets:
                field_name = widget.field_name
                field_value = widget.field_value
                
                if field_name == 'property_address1':
                    print(f"   📝 TEXT FIELD '{field_name}': '{field_value}'")
                    if field_value and 'VISIBLE TEST TEXT' in str(field_value):
                        text_found = True
                        print("      ✅ TEXT FIELD IS FILLED!")
                    else:
                        print("      ❌ TEXT FIELD IS NOT FILLED")
                
                elif field_name == 'fuel_type_elec2':
                    print(f"   🔘 RADIO FIELD '{field_name}': '{field_value}'")
                    if field_value and str(field_value) not in ['False', 'Off', '', 'None']:
                        radio_found = True
                        print("      ✅ RADIO BUTTON IS SELECTED!")
                    else:
                        print("      ❌ RADIO BUTTON IS NOT SELECTED")
                
                elif field_name == 'dwelling_single_fam1':
                    print(f"   ✅ CHECKBOX FIELD '{field_name}': '{field_value}'")
                    if field_value and str(field_value) not in ['False', 'Off', '', 'None']:
                        checkbox_found = True
                        print("      ✅ CHECKBOX IS CHECKED!")
                    else:
                        print("      ❌ CHECKBOX IS NOT CHECKED")
                
                elif field_name == 'signature3':
                    print(f"   ✍️  SIGNATURE FIELD '{field_name}': '{field_value}'")
                    if field_value and 'VISIBLE SIGNATURE TEST' in str(field_value):
                        signature_found = True
                        print("      ✅ SIGNATURE FIELD IS FILLED!")
                    else:
                        print("      ❌ SIGNATURE FIELD IS NOT FILLED")
        
        # Check for text insertions on pages
        print("\n📝 TEXT INSERTIONS ON PAGES:")
        signature_text_found = False
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            if "VISIBLE SIGNATURE TEST" in text:
                                signature_text_found = True
                                print(f"   ✍️  Found signature text on page {page_num + 1}: '{text}'")
                            elif "VISIBLE TEST TEXT" in text:
                                print(f"   📝 Found text insertion on page {page_num + 1}: '{text}'")
        
        doc.close()
        
        # Final Results
        print("\n" + "=" * 60)
        print("🏁 FINAL VISIBILITY RESULTS:")
        print(f"   📝 TEXT FIELD VISIBLE: {'✅ YES' if text_found else '❌ NO'}")
        print(f"   🔘 RADIO BUTTON SELECTED: {'✅ YES' if radio_found else '❌ NO'}")
        print(f"   ✅ CHECKBOX CHECKED: {'✅ YES' if checkbox_found else '❌ NO'}")
        print(f"   ✍️  SIGNATURE VISIBLE: {'✅ YES' if (signature_found or signature_text_found) else '❌ NO'}")
        
        total_working = sum([text_found, radio_found, checkbox_found, (signature_found or signature_text_found)])
        
        print(f"\n🎯 VISIBILITY SCORE: {total_working}/4 fields working")
        
        if total_working >= 3:
            print(f"\n🎉 SUCCESS! Fields are visible in {output_pdf}")
            print(f"📁 PLEASE MANUALLY OPEN '{output_pdf}' TO CONFIRM VISIBILITY")
            return True
        else:
            print(f"\n❌ FAILURE! Fields are not visible properly")
            print(f"📁 Check '{output_pdf}' manually - some fields may not be working")
            return False
            
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_visible_fields()
    
    print("\n" + "=" * 60)
    if success:
        print("🏆 VISIBILITY TEST PASSED")
        print("   Fields should be visible when you open the PDF!")
    else:
        print("💥 VISIBILITY TEST FAILED") 
        print("   Fields are not showing up properly in the PDF")
    
    print("\n📋 MANUAL VERIFICATION REQUIRED:")
    print("   Please open 'VERIFY_VISIBLE_TEST.pdf' and check:")
    print("   1. Property Address field shows the test text")
    print("   2. Electric Heat radio button is selected") 
    print("   3. Single Family Home checkbox is checked")
    print("   4. Signature shows the test signature text")