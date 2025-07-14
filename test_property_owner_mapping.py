#!/usr/bin/env python3
"""
Test property owner field mappings to verify city, state, zip fields work correctly
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_property_owner_mapping():
    """Test complete property owner field mapping including city, state, zip"""
    
    print("🏢 TESTING PROPERTY OWNER FIELD MAPPING")
    print("=" * 80)
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Extract fields from PDF
    if not os.path.exists('homworks.pdf'):
        print("❌ homworks.pdf not found")
        return False
    
    print("📄 Extracting fields from homworks.pdf...")
    field_extraction = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = field_extraction.get('fields', [])
    print(f"✅ Extracted {len(pdf_fields)} PDF fields")
    
    # Complete property owner test data
    property_owner_data = {
        'owner_name': 'ABC Property Management LLC',
        'owner_address': '123 Business Park Drive',
        'owner_city': 'Hartford',
        'owner_state': 'CT', 
        'owner_zip': '06103',
        'owner_telephone': '860-555-PROP',
        'owner_email': 'contact@abcproperties.com'
    }
    
    print(f"\n📝 PROPERTY OWNER TEST DATA:")
    for field, value in property_owner_data.items():
        print(f"   {field}: {value}")
    
    # Apply field mappings using the same logic as app.py
    EXACT_FIELD_MAPPINGS = {
        'owner_name': 'landlord_name3',
        'owner_address': 'address3', 
        'owner_city': 'city3',
        'owner_state': 'text_55cits',
        'owner_zip': 'text_56qpfj',
        'owner_telephone': 'phone3',
        'owner_email': 'email3'
    }
    
    print(f"\n🔗 APPLYING FIELD MAPPINGS:")
    mapped_fields = 0
    
    # Clear all existing assignments
    for field in pdf_fields:
        field['assigned_to'] = None
        field['value'] = ''
    
    # Map each property owner field
    for form_field, form_value in property_owner_data.items():
        pdf_field_name = EXACT_FIELD_MAPPINGS.get(form_field)
        
        if pdf_field_name:
            # Find the PDF field
            field_found = False
            for field in pdf_fields:
                if field.get('pdf_field_name') == pdf_field_name or field['name'] == pdf_field_name:
                    field['value'] = str(form_value)
                    field['assigned_to'] = 'user1'
                    field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                    
                    print(f"   ✅ {form_field} → {pdf_field_name} = '{form_value}'")
                    mapped_fields += 1
                    field_found = True
                    break
            
            if not field_found:
                print(f"   ❌ Field not found: {form_field} → {pdf_field_name}")
        else:
            print(f"   ❌ No mapping for: {form_field}")
    
    print(f"\n📊 Mapped {mapped_fields}/{len(property_owner_data)} property owner fields")
    
    # Create test document
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': pdf_fields,
        'user1_data': property_owner_data,
        'user2_data': {}
    }
    
    # Generate PDF
    output_file = 'PROPERTY_OWNER_MAPPING_TEST.pdf'
    print(f"\n🔧 Generating test PDF: {output_file}")
    
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if not success:
        print("❌ PDF generation failed")
        return False
    
    print(f"✅ PDF generated successfully")
    
    # Verify the output by checking widget values
    print(f"\n🔍 VERIFYING PROPERTY OWNER FIELDS IN OUTPUT PDF:")
    
    import fitz
    doc = fitz.open(output_file)
    
    # Property owner fields are on page 3 (index 2)
    page = doc[2]
    widgets = list(page.widgets())
    
    verification_results = {}
    expected_mappings = {
        'landlord_name3': property_owner_data['owner_name'],
        'address3': property_owner_data['owner_address'],
        'city3': property_owner_data['owner_city'],
        'text_55cits': property_owner_data['owner_state'],
        'text_56qpfj': property_owner_data['owner_zip'],
        'phone3': property_owner_data['owner_telephone'],
        'email3': property_owner_data['owner_email']
    }
    
    for widget in widgets:
        field_name = widget.field_name
        field_value = widget.field_value
        
        if field_name in expected_mappings:
            expected_value = expected_mappings[field_name]
            
            if field_value and str(field_value) == expected_value:
                verification_results[field_name] = 'PASS'
                print(f"   ✅ {field_name}: '{field_value}' (correct)")
            elif field_value:
                verification_results[field_name] = 'WRONG_VALUE'
                print(f"   ⚠️  {field_name}: '{field_value}' (expected '{expected_value}')")
            else:
                verification_results[field_name] = 'EMPTY'
                print(f"   ❌ {field_name}: EMPTY (expected '{expected_value}')")
    
    doc.close()
    
    # Check for missing fields
    for field_name in expected_mappings:
        if field_name not in verification_results:
            verification_results[field_name] = 'MISSING'
            print(f"   ❌ {field_name}: FIELD NOT FOUND")
    
    # Summary
    print(f"\n📊 VERIFICATION SUMMARY:")
    
    passed = sum(1 for result in verification_results.values() if result == 'PASS')
    total = len(expected_mappings)
    
    print(f"   ✅ Passed: {passed}/{total}")
    print(f"   ❌ Issues: {total - passed}/{total}")
    
    if passed == total:
        print(f"\n🎉 SUCCESS! All property owner fields are correctly mapped and filled!")
        
        # Check the specific missing fields mentioned by user
        print(f"\n🔍 SPECIFIC CHECK - CITY, STATE, ZIP FIELDS:")
        print(f"   City field (city3): {verification_results.get('city3', 'NOT CHECKED')}")
        print(f"   State field (text_55cits): {verification_results.get('text_55cits', 'NOT CHECKED')}")
        print(f"   ZIP field (text_56qpfj): {verification_results.get('text_56qpfj', 'NOT CHECKED')}")
        
        if all(verification_results.get(field) == 'PASS' for field in ['city3', 'text_55cits', 'text_56qpfj']):
            print(f"   ✅ All city, state, zip fields are working correctly!")
            return True
        else:
            print(f"   ❌ Some city, state, zip fields have issues")
            return False
    else:
        print(f"\n❌ FAILED! Some property owner fields are not working correctly")
        
        # Show details of issues
        issues = {k: v for k, v in verification_results.items() if v != 'PASS'}
        if issues:
            print(f"\n🔍 DETAILED ISSUES:")
            for field_name, issue in issues.items():
                frontend_field = next((k for k, v in EXACT_FIELD_MAPPINGS.items() if v == field_name), 'unknown')
                expected_value = expected_mappings.get(field_name, 'unknown')
                
                print(f"   ❌ {field_name} (frontend: {frontend_field})")
                print(f"      Issue: {issue}")
                print(f"      Expected: '{expected_value}'")
                print()
        
        return False

if __name__ == "__main__":
    success = test_property_owner_mapping()
    if success:
        print("\n🎯 Property owner mapping test PASSED!")
        print("✅ City, state, and zip fields are working correctly!")
    else:
        print("\n❌ Property owner mapping test FAILED!")
        print("⚠️  There are issues with the property owner field mappings.")