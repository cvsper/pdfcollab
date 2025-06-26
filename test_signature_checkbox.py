#!/usr/bin/env python3
"""
Focused test for signature and checkbox functionality
"""

import os
import fitz  # PyMuPDF
from pdf_processor import PDFProcessor

def test_signature_and_checkbox():
    """Test specifically signature and checkbox functionality"""
    print("🔍 Testing signature and checkbox functionality...")
    
    processor = PDFProcessor()
    
    # Use the real PDF
    input_pdf = 'uploads/c83e2f43-b4b7-4a4d-9b26-de394bc5008b_homeworks.pdf'
    output_pdf = 'test_signature_checkbox_output.pdf'
    
    if not os.path.exists(input_pdf):
        print(f"❌ Input PDF not found: {input_pdf}")
        return False
    
    # Test document with just signature and checkboxes
    test_document = {
        'id': 'sig_checkbox_test',
        'name': 'signature_checkbox_test.pdf',
        'pdf_fields': [
            # Signature field
            {
                'id': 'sig_1',
                'name': 'Signature',
                'pdf_field_name': 'signature3',
                'value': 'TEST SIGNATURE - John Smith Jr.',
                'type': 'signature',
                'assigned_to': 'user2',
                'position': {'x': 43, 'y': 470, 'width': 230, 'height': 14},
                'page': 2
            },
            
            # Checkbox fields - set some to true
            {
                'id': 'cb_1',
                'name': 'Single Family Home',
                'pdf_field_name': 'dwelling_single_fam1',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 40, 'y': 256, 'width': 10, 'height': 10},
                'page': 2
            },
            {
                'id': 'cb_2',
                'name': 'Apartment',
                'pdf_field_name': 'dwelling_apt1',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 41, 'y': 268, 'width': 10, 'height': 10},
                'page': 2
            },
            {
                'id': 'cb_3',
                'name': 'Condominium',
                'pdf_field_name': 'dwelling_condo1',
                'value': 'false',  # This should remain unchecked
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 41, 'y': 280, 'width': 10, 'height': 10},
                'page': 2
            },
            {
                'id': 'cb_4',
                'name': 'Low Income Program',
                'pdf_field_name': 'low_income4',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 156, 'y': 220, 'width': 10, 'height': 10},
                'page': 3
            },
            {
                'id': 'cb_5',
                'name': 'EBT (Food Stamps)',
                'pdf_field_name': 'ebt4',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 41, 'y': 293, 'width': 10, 'height': 10},
                'page': 3
            },
            {
                'id': 'cb_6',
                'name': 'Bill Forgiveness Program',
                'pdf_field_name': 'bill_forgive4',
                'value': 'false',  # This should remain unchecked
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 156, 'y': 231, 'width': 10, 'height': 10},
                'page': 3
            }
        ]
    }
    
    print(f"📄 Input: {input_pdf}")
    print(f"📁 Output: {output_pdf}")
    print(f"🔍 Testing {len(test_document['pdf_fields'])} fields:")
    print("   - 1 signature field")
    print("   - 5 checkbox fields (4 should be checked, 2 unchecked)")
    
    # Fill the PDF
    success = processor.fill_pdf_with_pymupdf(input_pdf, test_document, output_pdf)
    
    if success and os.path.exists(output_pdf):
        file_size = os.path.getsize(output_pdf)
        print(f"\n✅ PDF created: {output_pdf} ({file_size:,} bytes)")
        
        # Now analyze the output to see what was actually filled
        print("\n🔍 Analyzing output PDF...")
        try:
            doc = fitz.open(output_pdf)
            
            signature_found = False
            checkboxes_checked = 0
            checkboxes_unchecked = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = list(page.widgets())
                
                for widget in widgets:
                    field_name = widget.field_name
                    field_value = widget.field_value
                    
                    if field_name == 'signature3':
                        if field_value:
                            signature_found = True
                            print(f"   🖋️  SIGNATURE: Found value in field '{field_name}': '{field_value}'")
                        else:
                            print(f"   ❌ SIGNATURE: Field '{field_name}' is empty")
                    
                    elif widget.field_type == 2:  # Checkbox
                        if field_value in [True, 'On', 'Yes']:
                            checkboxes_checked += 1
                            print(f"   ✅ CHECKBOX: '{field_name}' is CHECKED ({field_value})")
                        else:
                            checkboxes_unchecked += 1
                            print(f"   ☐  CHECKBOX: '{field_name}' is unchecked ({field_value})")
            
            doc.close()
            
            # Check if text was inserted directly on pages (for signature)
            print("\n🔍 Checking for text insertions on pages...")
            doc = fitz.open(output_pdf)
            text_insertions_found = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_dict = page.get_text("dict")
                
                for block in text_dict.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                text = span.get("text", "")
                                if "TEST SIGNATURE" in text or "John Smith Jr" in text:
                                    text_insertions_found += 1
                                    print(f"   ✍️  TEXT INSERTION: Found signature text on page {page_num + 1}: '{text}'")
            
            doc.close()
            
            # Summary
            print(f"\n📊 RESULTS SUMMARY:")
            print(f"   🖋️  Signature in form field: {'✅ FOUND' if signature_found else '❌ NOT FOUND'}")
            print(f"   ✍️  Signature text insertions: {text_insertions_found} found")
            print(f"   ✅ Checkboxes checked: {checkboxes_checked}")
            print(f"   ☐  Checkboxes unchecked: {checkboxes_unchecked}")
            
            if signature_found or text_insertions_found > 0:
                print("   🎉 SIGNATURE: Working correctly!")
            else:
                print("   ❌ SIGNATURE: NOT working")
                
            if checkboxes_checked > 0:
                print("   🎉 CHECKBOXES: Working correctly!")
            else:
                print("   ❌ CHECKBOXES: NOT working")
            
            return signature_found or text_insertions_found > 0, checkboxes_checked > 0
            
        except Exception as e:
            print(f"❌ Error analyzing output PDF: {e}")
            return False, False
            
    else:
        print("❌ Failed to create PDF")
        return False, False

def test_signature_insertion_directly():
    """Test signature insertion on a simple PDF"""
    print("\n🧪 Testing signature insertion on a simple PDF...")
    
    # Create a simple PDF for testing
    doc = fitz.open()
    page = doc.new_page()
    
    # Add a signature field area
    page.insert_text((50, 100), "Test Document", fontsize=16)
    page.insert_text((50, 150), "Signature: ___________________", fontsize=12)
    
    # Save simple PDF
    simple_pdf = "simple_test.pdf"
    doc.save(simple_pdf)
    doc.close()
    
    # Now test signature insertion
    processor = PDFProcessor()
    output_pdf = "simple_signature_test.pdf"
    
    try:
        doc = fitz.open(simple_pdf)
        page = doc[0]
        
        # Insert signature directly
        processor.insert_signature_text(
            page, 
            "Direct Signature Test", 
            {'x': 150, 'y': 150, 'width': 200, 'height': 20}, 
            "test_signature"
        )
        
        doc.save(output_pdf)
        doc.close()
        
        if os.path.exists(output_pdf):
            file_size = os.path.getsize(output_pdf)
            print(f"✅ Simple signature test PDF created: {output_pdf} ({file_size} bytes)")
            
            # Check if signature text is there
            doc = fitz.open(output_pdf)
            page = doc[0]
            text = page.get_text()
            doc.close()
            
            if "Direct Signature Test" in text:
                print("✅ Signature text found in simple PDF!")
                return True
            else:
                print("❌ Signature text NOT found in simple PDF")
                print(f"   Page text: {text}")
                return False
        else:
            print("❌ Simple signature test PDF not created")
            return False
            
    except Exception as e:
        print(f"❌ Error in simple signature test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        for f in [simple_pdf, output_pdf]:
            if os.path.exists(f):
                try:
                    os.unlink(f)
                except:
                    pass

if __name__ == "__main__":
    print("🚀 Signature and Checkbox Functionality Test")
    print("=" * 50)
    
    # Test 1: Signature insertion directly
    simple_test = test_signature_insertion_directly()
    
    # Test 2: Full signature and checkbox test
    sig_works, checkbox_works = test_signature_and_checkbox()
    
    print("\n" + "=" * 50)
    print("🏁 FINAL RESULTS:")
    print(f"   Simple signature test: {'✅ PASS' if simple_test else '❌ FAIL'}")
    print(f"   Signature functionality: {'✅ PASS' if sig_works else '❌ FAIL'}")
    print(f"   Checkbox functionality: {'✅ PASS' if checkbox_works else '❌ FAIL'}")
    
    if simple_test and sig_works and checkbox_works:
        print("\n🎉 ALL TESTS PASSED - Signatures and checkboxes are working!")
    else:
        print("\n❌ SOME TESTS FAILED - Issues detected")
        
    print(f"\n📁 Check 'test_signature_checkbox_output.pdf' to manually verify results")