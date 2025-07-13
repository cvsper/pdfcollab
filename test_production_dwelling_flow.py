#!/usr/bin/env python3
"""
Test dwelling type mapping exactly as app.py does it
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_production_dwelling_flow():
    """Test dwelling type mapping exactly like production app.py"""
    
    print("🔍 TESTING PRODUCTION DWELLING FLOW")
    print("=" * 60)
    print("Mimicking the exact logic from app.py")
    
    # Extract PDF fields exactly like app.py does
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    
    if "error" in pdf_analysis:
        print(f"❌ Error: {pdf_analysis['error']}")
        return False
    
    pdf_fields = pdf_analysis['fields']
    print(f"📋 Extracted {len(pdf_fields)} PDF fields")
    
    # Simulate the exact form data from app.py
    form_data = {
        'property_address': '123 Test Address',
        'dwelling_type': 'apartment',  # This is what comes from the form
        'first_name': 'John',
        'last_name': 'Doe'
    }
    
    print(f"\n📝 Form data: {form_data}")
    
    # Apply the EXACT_FIELD_MAPPINGS from app.py first
    EXACT_FIELD_MAPPINGS = {
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
        'dwelling_type': 'dwelling_single_fam1',  # This is wrong - should be handled specially
    }
    
    # First, apply direct mappings (this is what app.py does)
    print(f"\n🔧 APPLYING EXACT_FIELD_MAPPINGS:")
    for form_field, pdf_field_name in EXACT_FIELD_MAPPINGS.items():
        form_value = form_data.get(form_field)
        if form_value and form_field != 'dwelling_type':  # Skip dwelling_type for now
            print(f"   Looking for field: {form_field} → {pdf_field_name}")
            
            # CRITICAL FIX: Check both pdf_field_name and name for compatibility
            for field in pdf_fields:
                if field.get('pdf_field_name') == pdf_field_name or field['name'] == pdf_field_name:
                    field['value'] = str(form_value)
                    field['assigned_to'] = 'user1'
                    print(f"   ✅ Mapped: {form_field} → {field['name']} = {form_value}")
                    break
    
    # Now handle dwelling_type specially (exactly like app.py)
    print(f"\n🏠 HANDLING DWELLING TYPE SPECIALLY:")
    form_field = 'dwelling_type'
    form_value = form_data.get(form_field)
    
    if form_value:
        print(f"   Form value: {form_value}")
        
        # Handle dwelling type (EXACT copy from app.py)
        dwelling_mappings = {
            'single_family': 'Single Family Home (Checkbox)',
            'apartment': 'Apartment (Checkbox)', 
            'condominium': 'Condominium (Checkbox)'
        }
        target_field = dwelling_mappings.get(form_value)
        print(f"   Target field: {target_field}")
        
        if target_field:
            matched = False
            for field in pdf_fields:
                if field['name'] == target_field:
                    field['value'] = 'true'
                    field['assigned_to'] = 'user1'
                    field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                    matched = True
                    print(f"   ✅ DWELLING MAPPED: {form_value} → {field['name']} = true")
                    print(f"      PDF field name: {field['pdf_field_name']}")
                    break
            
            if not matched:
                print(f"   ❌ NO MATCH FOUND for: {target_field}")
                print(f"   📋 Available checkbox fields:")
                for field in pdf_fields:
                    if field.get('type') == 'checkbox':
                        print(f"      - {field['name']}")
    
    # Create test document exactly like app.py
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': pdf_fields,
        'user1_data': form_data,
        'user2_data': {
            'applicant_signature': 'John Doe',
            'authorization_date': '2025-07-13'
        }
    }
    
    # Add signature for reference
    for field in pdf_fields:
        if field['name'] == 'Applicant Signature':
            field['value'] = 'John Doe'
            field['assigned_to'] = 'user2'
            field['type'] = 'signature'
            break
    
    # Generate PDF using the same method as app.py
    output_file = 'PRODUCTION_DWELLING_FLOW_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ Production flow test PDF created: {output_file}")
        
        # Verify the dwelling checkbox
        import fitz
        doc = fitz.open(output_file)
        page = doc[2]  # Page 3
        widgets = list(page.widgets())
        
        dwelling_found = False
        for widget in widgets:
            if 'dwelling_apt1' in widget.field_name and widget.field_value in [True, 1, 'Yes']:
                dwelling_found = True
                print(f"🎉 SUCCESS: {widget.field_name} = {widget.field_value}")
                break
        
        if not dwelling_found:
            print(f"❌ FAILED: Dwelling checkbox not checked in final PDF")
            
            # Show all checkboxes
            print(f"\n📝 ALL CHECKBOXES:")
            for widget in widgets:
                if widget.field_type == 2:  # Checkbox
                    status = "✅" if widget.field_value in [True, 1, 'Yes'] else "❌"
                    print(f"   {status} {widget.field_name}: {widget.field_value}")
        
        doc.close()
        return dwelling_found
    else:
        print(f"❌ Failed to create production flow test PDF")
        return False

if __name__ == "__main__":
    success = test_production_dwelling_flow()
    if success:
        print("\n✅ Production dwelling flow test PASSED!")
    else:
        print("\n❌ Production dwelling flow test FAILED!")