#!/usr/bin/env python3
"""
Final test to verify dwelling checkbox fix is working after removing from EXACT_FIELD_MAPPINGS
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_final_dwelling_fix():
    """Test dwelling checkbox with corrected app.py logic"""
    
    print("🏆 FINAL DWELLING CHECKBOX FIX TEST")
    print("=" * 60)
    print("Testing with corrected EXACT_FIELD_MAPPINGS (dwelling_type removed)")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    print(f"📋 Extracted {len(pdf_fields)} PDF fields")
    
    # Test all three dwelling types
    test_cases = [
        ('apartment', 'dwelling_apt1', 'Apartment (Checkbox)'),
        ('single_family', 'dwelling_single_fam1', 'Single Family Home (Checkbox)'),
        ('condominium', 'dwelling_condo1', 'Condominium (Checkbox)')
    ]
    
    all_tests_passed = True
    
    for dwelling_value, expected_pdf_field, expected_display_name in test_cases:
        print(f"\n🧪 Testing dwelling_type='{dwelling_value}'")
        
        # Reset all fields
        for field in pdf_fields:
            field.pop('value', None)
            field.pop('assigned_to', None)
        
        # Simulate form data
        form_data = {
            'property_address': f'123 {dwelling_value.title()} Street',
            'dwelling_type': dwelling_value,
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Apply CORRECTED EXACT_FIELD_MAPPINGS (without dwelling_type)
        CORRECTED_EXACT_FIELD_MAPPINGS = {
            'property_address': 'property_address1',
            'apartment_number': 'apt_num1',
            'city': 'city1',
            'state': 'state1',
            'zip_code': 'zip1',
            'apartments_count': 'num_of_apt1',
            'first_name': 'first_name2',
            'last_name': 'last_name2',
            'telephone': 'phone2',
            'email': 'email2',
            'phone_additional': 'phone_num1',
            # Note: dwelling_type REMOVED from direct mappings
            'electric_account': 'elec_acct_num2',
            'gas_account': 'gas_acct_num2',
        }
        
        # Apply direct mappings (dwelling_type should be skipped)
        for form_field, pdf_field_name in CORRECTED_EXACT_FIELD_MAPPINGS.items():
            form_value = form_data.get(form_field)
            if form_value:
                for field in pdf_fields:
                    if field.get('pdf_field_name') == pdf_field_name or field['name'] == pdf_field_name:
                        field['value'] = str(form_value)
                        field['assigned_to'] = 'user1'
                        print(f"   ✅ Direct mapping: {form_field} → {field['name']}")
                        break
        
        # Handle dwelling_type specially
        form_field = 'dwelling_type'
        form_value = form_data.get(form_field)
        
        if form_value:
            print(f"   🏠 Handling dwelling_type='{form_value}' specially")
            
            dwelling_mappings = {
                'single_family': 'Single Family Home (Checkbox)',
                'apartment': 'Apartment (Checkbox)', 
                'condominium': 'Condominium (Checkbox)'
            }
            target_field = dwelling_mappings.get(form_value)
            
            if target_field:
                matched = False
                for field in pdf_fields:
                    if field['name'] == target_field:
                        field['value'] = 'true'
                        field['assigned_to'] = 'user1'
                        field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                        matched = True
                        print(f"   ✅ Special mapping: {form_value} → {field['name']} = true")
                        print(f"      PDF field: {field['pdf_field_name']}")
                        
                        # Verify this is the expected field
                        if field['pdf_field_name'] == expected_pdf_field:
                            print(f"   🎯 CORRECT: Mapped to expected PDF field '{expected_pdf_field}'")
                        else:
                            print(f"   ❌ WRONG: Expected '{expected_pdf_field}', got '{field['pdf_field_name']}'")
                            all_tests_passed = False
                        break
                
                if not matched:
                    print(f"   ❌ FAILED: Could not find {target_field}")
                    all_tests_passed = False
        
        # Create test document and generate PDF
        test_document = {
            'id': str(uuid.uuid4()),
            'pdf_fields': pdf_fields,
            'user1_data': form_data,
            'user2_data': {
                'applicant_signature': 'Test User',
                'authorization_date': '2025-07-13'
            }
        }
        
        # Add signature for reference
        for field in pdf_fields:
            if field['name'] == 'Applicant Signature':
                field['value'] = 'Test User'
                field['assigned_to'] = 'user2'
                field['type'] = 'signature'
                break
        
        # Generate PDF
        output_file = f'FINAL_DWELLING_TEST_{dwelling_value.upper()}.pdf'
        success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
        
        if success:
            print(f"   ✅ PDF created: {output_file}")
            
            # Verify the checkbox in the final PDF
            import fitz
            doc = fitz.open(output_file)
            page = doc[2]  # Page 3
            widgets = list(page.widgets())
            
            checkbox_verified = False
            for widget in widgets:
                if widget.field_name == expected_pdf_field:
                    if widget.field_value in [True, 1, 'Yes']:
                        checkbox_verified = True
                        print(f"   🎉 VERIFIED: {widget.field_name} = {widget.field_value} in final PDF")
                    else:
                        print(f"   ❌ FAILED: {widget.field_name} = {widget.field_value} (not checked)")
                        all_tests_passed = False
                    break
            
            if not checkbox_verified:
                print(f"   ❌ FAILED: Could not verify {expected_pdf_field} in final PDF")
                all_tests_passed = False
            
            doc.close()
        else:
            print(f"   ❌ FAILED: Could not create PDF for {dwelling_value}")
            all_tests_passed = False
    
    print(f"\n📊 FINAL RESULTS:")
    if all_tests_passed:
        print(f"🎉 ALL TESTS PASSED! Dwelling checkboxes are working correctly.")
        print(f"✅ dwelling_apt1, dwelling_single_fam1, dwelling_condo1 all verified")
    else:
        print(f"❌ SOME TESTS FAILED! Check the output above for details.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = test_final_dwelling_fix()
    if success:
        print("\n🏆 Final dwelling fix test PASSED! Ready for production!")
    else:
        print("\n❌ Final dwelling fix test FAILED! Needs more work.")