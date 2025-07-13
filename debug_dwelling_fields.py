#!/usr/bin/env python3
"""
Debug dwelling field mappings to see what's actually happening
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def debug_dwelling_fields():
    """Debug exactly what's happening with dwelling fields"""
    
    print("🔍 DEBUGGING DWELLING FIELD MAPPINGS")
    print("=" * 60)
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    print(f"📋 Total fields extracted: {len(pdf_fields)}")
    
    # Find all dwelling-related fields
    print("\n🏠 DWELLING-RELATED FIELDS:")
    dwelling_fields = []
    for field in pdf_fields:
        field_name = field['name']
        pdf_field_name = field.get('pdf_field_name', 'N/A')
        field_type = field.get('type', 'unknown')
        
        if 'dwelling' in pdf_field_name.lower() or 'single' in field_name.lower() or 'apartment' in field_name.lower() or 'condominium' in field_name.lower():
            dwelling_fields.append(field)
            print(f"   📝 Display Name: '{field_name}'")
            print(f"      PDF Field: '{pdf_field_name}'")
            print(f"      Type: {field_type}")
            print(f"      Position: {field.get('position', 'N/A')}")
            print()
    
    print(f"Found {len(dwelling_fields)} dwelling-related fields")
    
    # Test setting dwelling values directly
    print("\n🧪 TESTING DWELLING FIELD SETTING:")
    
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': pdf_fields,
        'user1_data': {
            'property_address': '123 Test Street',
            'dwelling_type': 'apartment'
        },
        'user2_data': {
            'applicant_signature': 'John Doe',
            'authorization_date': '2025-07-13'
        }
    }
    
    # Try different approaches to set dwelling
    print("Approach 1: Set by PDF field name 'dwelling_apt1'")
    found_by_pdf_name = False
    for field in pdf_fields:
        if field.get('pdf_field_name') == 'dwelling_apt1':
            field['value'] = 'true'
            field['assigned_to'] = 'user1'
            found_by_pdf_name = True
            print(f"   ✅ Set field: {field['name']} = true")
            break
    
    if not found_by_pdf_name:
        print("   ❌ No field found with pdf_field_name 'dwelling_apt1'")
    
    print("\nApproach 2: Set by display name 'Apartment (Checkbox)'")
    found_by_display = False
    for field in pdf_fields:
        if field['name'] == 'Apartment (Checkbox)':
            field['value'] = 'true'
            field['assigned_to'] = 'user1'
            found_by_display = True
            print(f"   ✅ Set field: {field['name']} = true (pdf_field: {field.get('pdf_field_name')})")
            break
    
    if not found_by_display:
        print("   ❌ No field found with display name 'Apartment (Checkbox)'")
    
    # Add basic property address for reference
    for field in pdf_fields:
        if field['name'] == 'Property Address':
            field['value'] = '123 Test Street'
            field['assigned_to'] = 'user1'
            break
    
    # Add signature for reference
    for field in pdf_fields:
        if field['name'] == 'Applicant Signature':
            field['value'] = 'John Doe'
            field['assigned_to'] = 'user2'
            field['type'] = 'signature'
            break
    
    # Generate test PDF
    output_file = 'DEBUG_DWELLING_FIELDS.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ Debug PDF created: {output_file}")
        
        # Show which fields actually have values
        print("\n📊 FIELDS WITH VALUES:")
        filled_count = 0
        for field in pdf_fields:
            if field.get('value'):
                filled_count += 1
                field_name = field['name']
                pdf_field_name = field.get('pdf_field_name', 'N/A')
                value = field['value']
                print(f"   ✅ {field_name} (pdf: {pdf_field_name}) = {value}")
        
        print(f"\n📈 Total filled: {filled_count} fields")
        
        # Check specifically for dwelling
        dwelling_set = False
        for field in pdf_fields:
            if 'apartment' in field['name'].lower() and field.get('value'):
                dwelling_set = True
                print(f"\n🏠 DWELLING CONFIRMED: {field['name']} = {field['value']}")
                break
        
        if not dwelling_set:
            print("\n⚠️  WARNING: No dwelling field appears to be set!")
            
    else:
        print(f"\n❌ Failed to create debug PDF")
    
    return True

if __name__ == "__main__":
    debug_dwelling_fields()