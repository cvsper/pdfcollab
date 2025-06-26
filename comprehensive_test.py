#!/usr/bin/env python3
"""
Comprehensive test to verify radio buttons, checkboxes, and signatures work correctly
This test will verify 90% confidence that the functionality works as expected
"""

import os
import fitz  # PyMuPDF
from pdf_processor import PDFProcessor

def test_all_functionality():
    """Test radio buttons, checkboxes, and signatures comprehensively"""
    print("🚀 COMPREHENSIVE FUNCTIONALITY TEST")
    print("=" * 60)
    
    processor = PDFProcessor()
    
    # Use the real PDF
    input_pdf = 'uploads/c83e2f43-b4b7-4a4d-9b26-de394bc5008b_homeworks.pdf'
    output_pdf = 'comprehensive_test_output.pdf'
    
    if not os.path.exists(input_pdf):
        print(f"❌ Input PDF not found: {input_pdf}")
        return False
    
    # Comprehensive test document with all field types
    test_document = {
        'id': 'comprehensive_test',
        'name': 'comprehensive_test.pdf',
        'pdf_fields': [
            # TEXT FIELDS
            {
                'id': 'text_1',
                'name': 'Property Address',
                'pdf_field_name': 'property_address1',
                'value': 'TEST ADDRESS: 123 Main Street',
                'type': 'text',
                'assigned_to': 'user1',
                'position': {'x': 37, 'y': 156, 'width': 196, 'height': 14},
                'page': 2
            },
            {
                'id': 'text_2',
                'name': 'City',
                'pdf_field_name': 'city1',
                'value': 'TEST CITY',
                'type': 'text',
                'assigned_to': 'user1',
                'position': {'x': 36, 'y': 182, 'width': 148, 'height': 14},
                'page': 2
            },
            
            # RADIO BUTTONS - Test both yes and no
            {
                'id': 'radio_1',
                'name': 'Electric Heat - YES',
                'pdf_field_name': 'fuel_type_elec2',
                'value': 'yes',
                'type': 'radio',
                'assigned_to': 'user1',
                'position': {'x': 317, 'y': 235, 'width': 10, 'height': 10},
                'page': 2
            },
            {
                'id': 'radio_2',
                'name': 'Gas Heat - NO (should be blank)',
                'pdf_field_name': 'fuel_type_gas2',
                'value': 'no',
                'type': 'radio',
                'assigned_to': 'user1',
                'position': {'x': 345, 'y': 235, 'width': 10, 'height': 10},
                'page': 2
            },
            {
                'id': 'radio_3',
                'name': 'Property Owner - YES',
                'pdf_field_name': 'owner2',
                'value': 'yes',
                'type': 'radio',
                'assigned_to': 'user1',
                'position': {'x': 442, 'y': 235, 'width': 10, 'height': 10},
                'page': 2
            },
            {
                'id': 'radio_4',
                'name': 'Renter - NO (should be blank)',
                'pdf_field_name': 'renter2',
                'value': 'no',
                'type': 'radio',
                'assigned_to': 'user1',
                'position': {'x': 471, 'y': 235, 'width': 10, 'height': 10},
                'page': 2
            },
            
            # CHECKBOXES - Test both checked and unchecked
            {
                'id': 'checkbox_1',
                'name': 'Single Family Home - CHECKED',
                'pdf_field_name': 'dwelling_single_fam1',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 40, 'y': 256, 'width': 10, 'height': 10},
                'page': 2
            },
            {
                'id': 'checkbox_2',
                'name': 'Apartment - CHECKED',
                'pdf_field_name': 'dwelling_apt1',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 41, 'y': 268, 'width': 10, 'height': 10},
                'page': 2
            },
            {
                'id': 'checkbox_3',
                'name': 'Condominium - UNCHECKED',
                'pdf_field_name': 'dwelling_condo1',
                'value': 'false',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 41, 'y': 280, 'width': 10, 'height': 10},
                'page': 2
            },
            {
                'id': 'checkbox_4',
                'name': 'Low Income Program - CHECKED',
                'pdf_field_name': 'low_income4',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 156, 'y': 220, 'width': 10, 'height': 10},
                'page': 3
            },
            {
                'id': 'checkbox_5',
                'name': 'EBT (Food Stamps) - CHECKED',
                'pdf_field_name': 'ebt4',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 41, 'y': 293, 'width': 10, 'height': 10},
                'page': 3
            },
            {
                'id': 'checkbox_6',
                'name': 'Bill Forgiveness Program - UNCHECKED',
                'pdf_field_name': 'bill_forgive4',
                'value': 'false',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 156, 'y': 231, 'width': 10, 'height': 10},
                'page': 3
            },
            
            # SIGNATURE
            {
                'id': 'signature_1',
                'name': 'Main Signature',
                'pdf_field_name': 'signature3',
                'value': 'COMPREHENSIVE TEST SIGNATURE - Jane Smith',
                'type': 'signature',
                'assigned_to': 'user2',
                'position': {'x': 43, 'y': 470, 'width': 230, 'height': 14},
                'page': 2
            }
        ]
    }
    
    print(f"📄 Input: {input_pdf}")
    print(f"📁 Output: {output_pdf}")
    print(f"🔍 Testing {len(test_document['pdf_fields'])} fields:")
    print("   - 2 text fields")
    print("   - 4 radio buttons (2 YES, 2 NO)")
    print("   - 6 checkboxes (4 CHECKED, 2 UNCHECKED)")
    print("   - 1 signature")
    print("\n🎯 EXPECTED RESULTS:")
    print("   ✅ Text fields should be filled")
    print("   ✅ Radio buttons with 'yes' should be selected")
    print("   ⚪ Radio buttons with 'no' should be blank")
    print("   ✅ Checkboxes with 'true' should be checked")
    print("   ☐ Checkboxes with 'false' should be unchecked")
    print("   ✍️  Signature should appear in cursive font")
    
    # Fill the PDF
    print("\n" + "=" * 60)
    print("🔄 FILLING PDF...")
    success = processor.fill_pdf_with_pymupdf(input_pdf, test_document, output_pdf)
    
    if not success or not os.path.exists(output_pdf):
        print("❌ FAILED to create PDF")
        return False
    
    file_size = os.path.getsize(output_pdf)
    print(f"\n✅ PDF created: {output_pdf} ({file_size:,} bytes)")
    
    # DETAILED ANALYSIS
    print("\n" + "=" * 60)
    print("🔍 ANALYZING OUTPUT PDF...")
    
    try:
        doc = fitz.open(output_pdf)
        
        # Track results
        text_fields_filled = 0
        radio_yes_selected = 0
        radio_no_blank = 0
        checkbox_checked = 0
        checkbox_unchecked = 0
        signature_found = False
        
        expected_text_fields = 2
        expected_radio_yes = 2
        expected_radio_no = 2
        expected_checkbox_checked = 4
        expected_checkbox_unchecked = 2
        
        # Analyze form fields
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            for widget in widgets:
                field_name = widget.field_name
                field_value = widget.field_value
                widget_type = processor.get_widget_type(widget)
                
                # Check specific fields we're testing
                if field_name == 'property_address1':
                    if field_value and 'TEST ADDRESS' in str(field_value):
                        text_fields_filled += 1
                        print(f"   ✅ TEXT: Property Address = '{field_value}'")
                    else:
                        print(f"   ❌ TEXT: Property Address = '{field_value}' (expected 'TEST ADDRESS')")
                
                elif field_name == 'city1':
                    if field_value and 'TEST CITY' in str(field_value):
                        text_fields_filled += 1
                        print(f"   ✅ TEXT: City = '{field_value}'")
                    else:
                        print(f"   ❌ TEXT: City = '{field_value}' (expected 'TEST CITY')")
                
                # Radio buttons (should have export value for yes, 'Off' for no)
                elif field_name in ['fuel_type_elec2', 'owner2']:  # Should be YES
                    # Radio buttons can have export values like 'True', 'Value_xyz', or boolean True
                    if (field_value is True or 
                        str(field_value).lower() in ['true', 'yes', '1', 'on'] or
                        (field_value and str(field_value) not in ['False', 'Off', '', 'None'])):
                        radio_yes_selected += 1
                        print(f"   ✅ RADIO YES: {field_name} = {field_value}")
                    else:
                        print(f"   ❌ RADIO YES: {field_name} = {field_value} (expected selected state)")
                
                elif field_name in ['fuel_type_gas2', 'renter2']:  # Should be NO/blank
                    if (field_value is False or field_value is None or 
                        str(field_value).lower() in ['false', 'no', 'off', ''] or
                        str(field_value) == 'Off'):
                        radio_no_blank += 1
                        print(f"   ✅ RADIO NO: {field_name} = {field_value} (correctly blank)")
                    else:
                        print(f"   ❌ RADIO NO: {field_name} = {field_value} (expected blank)")
                
                # Checkboxes
                elif field_name in ['dwelling_single_fam1', 'dwelling_apt1', 'low_income4', 'ebt4']:  # Should be CHECKED
                    if field_value is True or str(field_value).lower() in ['true', 'yes', '1', 'on'] or (field_value and 'yes' in str(field_value).lower()):
                        checkbox_checked += 1
                        print(f"   ✅ CHECKBOX CHECKED: {field_name} = {field_value}")
                    else:
                        print(f"   ❌ CHECKBOX CHECKED: {field_name} = {field_value} (expected checked)")
                
                elif field_name in ['dwelling_condo1', 'bill_forgive4']:  # Should be UNCHECKED
                    if field_value is False or field_value is None or str(field_value).lower() in ['false', 'no', 'off', '']:
                        checkbox_unchecked += 1
                        print(f"   ✅ CHECKBOX UNCHECKED: {field_name} = {field_value} (correctly unchecked)")
                    else:
                        print(f"   ❌ CHECKBOX UNCHECKED: {field_name} = {field_value} (expected unchecked)")
                
                # Signature field
                elif field_name == 'signature3':
                    if field_value and 'COMPREHENSIVE TEST SIGNATURE' in str(field_value):
                        signature_found = True
                        print(f"   ✅ SIGNATURE FIELD: {field_name} = '{field_value}'")
                    else:
                        print(f"   ⚠️  SIGNATURE FIELD: {field_name} = '{field_value}' (checking text insertion)")
        
        # Check for signature text insertion
        signature_text_found = False
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            if "COMPREHENSIVE TEST SIGNATURE" in text:
                                signature_text_found = True
                                print(f"   ✅ SIGNATURE TEXT: Found on page {page_num + 1}: '{text}'")
                                break
        
        doc.close()
        
        # FINAL SCORING
        print("\n" + "=" * 60)
        print("📊 FINAL RESULTS:")
        
        text_score = text_fields_filled / expected_text_fields * 100
        radio_yes_score = radio_yes_selected / expected_radio_yes * 100
        radio_no_score = radio_no_blank / expected_radio_no * 100
        checkbox_checked_score = checkbox_checked / expected_checkbox_checked * 100
        checkbox_unchecked_score = checkbox_unchecked / expected_checkbox_unchecked * 100
        signature_score = 100 if (signature_found or signature_text_found) else 0
        
        print(f"   📝 TEXT FIELDS: {text_fields_filled}/{expected_text_fields} = {text_score:.0f}%")
        print(f"   🔘 RADIO YES: {radio_yes_selected}/{expected_radio_yes} = {radio_yes_score:.0f}%")
        print(f"   ⚪ RADIO NO: {radio_no_blank}/{expected_radio_no} = {radio_no_score:.0f}%")
        print(f"   ✅ CHECKBOX CHECKED: {checkbox_checked}/{expected_checkbox_checked} = {checkbox_checked_score:.0f}%")
        print(f"   ☐ CHECKBOX UNCHECKED: {checkbox_unchecked}/{expected_checkbox_unchecked} = {checkbox_unchecked_score:.0f}%")
        print(f"   ✍️  SIGNATURE: {'100%' if (signature_found or signature_text_found) else '0%'}")
        
        # Overall score
        overall_score = (text_score + radio_yes_score + radio_no_score + checkbox_checked_score + checkbox_unchecked_score + signature_score) / 6
        
        print(f"\n🎯 OVERALL CONFIDENCE: {overall_score:.1f}%")
        
        if overall_score >= 90:
            print("🎉 SUCCESS! 90%+ confidence achieved!")
            print(f"📁 Manual verification file: {output_pdf}")
            return True
        else:
            print("❌ FAILED to achieve 90% confidence")
            print("🔧 Issues need to be fixed")
            return False
            
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_functionality()
    
    print("\n" + "=" * 60)
    if success:
        print("🏆 COMPREHENSIVE TEST PASSED")
        print("   All functionality working with 90%+ confidence!")
    else:
        print("💥 COMPREHENSIVE TEST FAILED")
        print("   Functionality needs fixes to achieve 90% confidence")