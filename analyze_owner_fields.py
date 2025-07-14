#!/usr/bin/env python3
"""
Analyze property owner field mappings and identify missing city/state/zip fields
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def analyze_owner_field_mappings():
    """Analyze property owner field mappings for missing city/state/zip"""
    
    print("🔍 ANALYZING PROPERTY OWNER FIELD MAPPINGS")
    print("=" * 80)
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Extract fields from the PDF
    if not os.path.exists('homworks.pdf'):
        print("❌ homworks.pdf not found")
        return False
    
    print("📄 Extracting fields from homworks.pdf...")
    field_extraction = processor.extract_fields_with_pymupdf('homworks.pdf')
    
    if 'error' in field_extraction:
        print(f"❌ Error extracting fields: {field_extraction['error']}")
        return False
    
    pdf_fields = field_extraction.get('fields', [])
    print(f"✅ Extracted {len(pdf_fields)} PDF fields")
    
    # 1. Find all landlord/property owner related fields
    print(f"\n1️⃣ ALL LANDLORD/PROPERTY OWNER RELATED FIELDS:")
    print("-" * 50)
    
    owner_related_fields = []
    for field in pdf_fields:
        field_name = field.get('pdf_field_name', field['name']).lower()
        display_name = field['name'].lower()
        
        # Check if field is related to landlord/property owner
        if any(keyword in field_name or keyword in display_name for keyword in ['landlord', 'owner', 'property', 'city3', 'text_55', 'text_56', 'phone3', 'email3', 'address3']):
            owner_related_fields.append(field)
            position = field.get('position', {})
            print(f"   📄 {field['name']}")
            print(f"      PDF field name: {field.get('pdf_field_name', 'N/A')}")
            print(f"      Type: {field.get('type', 'unknown')}")
            print(f"      Position: ({position.get('x', '?'):.0f}, {position.get('y', '?'):.0f})")
            print()
    
    print(f"Found {len(owner_related_fields)} owner-related fields")
    
    # 2. Check current field_type_map for property owner mappings
    print(f"\n2️⃣ CURRENT FIELD_TYPE_MAP FOR PROPERTY OWNER:")
    print("-" * 50)
    
    owner_mappings = {}
    for display_name, pdf_field_name in processor.field_type_map.items():
        if any(keyword in display_name.lower() for keyword in ['landlord', 'owner']):
            owner_mappings[display_name] = pdf_field_name
            print(f"   ✅ {display_name} → {pdf_field_name}")
    
    # 3. Check for missing city, state, zip mappings
    print(f"\n3️⃣ PROPERTY OWNER CITY/STATE/ZIP FIELD ANALYSIS:")
    print("-" * 50)
    
    # Expected mappings for property owner location
    expected_owner_location_fields = {
        'city': ['city3', 'landlord_city', 'owner_city'],
        'state': ['text_55cits', 'landlord_state', 'owner_state'], 
        'zip': ['text_56qpfj', 'landlord_zip', 'owner_zip']
    }
    
    # Find actual PDF fields that might be property owner city/state/zip
    potential_owner_location_fields = []
    for field in pdf_fields:
        field_name = field.get('pdf_field_name', field['name'])
        position = field.get('position', {})
        
        # Look for fields in the property owner section (around y=600-650 based on test data)
        if position.get('y', 0) > 580:
            if any(keyword in field_name.lower() for keyword in ['city', 'state', 'zip', 'text_55', 'text_56']):
                potential_owner_location_fields.append(field)
                print(f"   🔍 Potential owner location field: {field['name']}")
                print(f"      PDF field name: {field_name}")
                print(f"      Position: ({position.get('x', '?'):.0f}, {position.get('y', '?'):.0f})")
                print()
    
    # 4. Check what's in test data vs what's mapped
    print(f"\n4️⃣ TEST DATA VS MAPPED FIELDS:")
    print("-" * 50)
    
    # Common test data fields for property owner
    test_owner_data = {
        'owner_name': 'Smith Properties LLC',
        'owner_address': '456 Management Ave', 
        'owner_city': 'New Haven',
        'owner_state': 'CT',
        'owner_zip': '06511',
        'owner_telephone': '203-555-0000',
        'owner_email': 'info@smithproperties.com'
    }
    
    for test_field, test_value in test_owner_data.items():
        mapped_pdf_field = processor.field_type_map.get(test_field.replace('owner_', 'Landlord ').replace('_', ' ').title())
        if not mapped_pdf_field:
            # Try alternative mappings
            alt_mappings = {
                'owner_city': 'Landlord City',
                'owner_state': 'Landlord State', 
                'owner_zip': 'Landlord ZIP'
            }
            mapped_pdf_field = processor.field_type_map.get(alt_mappings.get(test_field, ''))
        
        print(f"   📝 {test_field}: {test_value}")
        if mapped_pdf_field:
            print(f"      ✅ Mapped to: {mapped_pdf_field}")
        else:
            print(f"      ❌ NO MAPPING FOUND!")
        
        # Check if the PDF field actually exists
        if mapped_pdf_field:
            field_exists = any(
                field.get('pdf_field_name') == mapped_pdf_field or field['name'] == mapped_pdf_field 
                for field in pdf_fields
            )
            if field_exists:
                print(f"      ✅ PDF field exists")
            else:
                print(f"      ❌ PDF field NOT FOUND in extracted fields")
        print()
    
    # 5. Identify the actual missing mappings
    print(f"\n5️⃣ MISSING OR INCORRECT MAPPINGS:")
    print("-" * 50)
    
    issues_found = []
    
    # Check the key owner location fields
    owner_location_checks = {
        'Landlord City': 'city3',
        'Landlord State': 'text_55cits',
        'Landlord ZIP': 'text_56qpfj'
    }
    
    for display_name, expected_pdf_field in owner_location_checks.items():
        current_mapping = processor.field_type_map.get(display_name)
        
        if not current_mapping:
            issues_found.append(f"❌ Missing mapping: {display_name} (should map to {expected_pdf_field})")
        elif current_mapping != expected_pdf_field:
            issues_found.append(f"⚠️  Incorrect mapping: {display_name} → {current_mapping} (should be {expected_pdf_field})")
        else:
            print(f"   ✅ Correct mapping: {display_name} → {current_mapping}")
        
        # Check if the PDF field actually exists
        field_exists = any(
            field.get('pdf_field_name') == expected_pdf_field 
            for field in pdf_fields
        )
        if not field_exists:
            issues_found.append(f"❌ PDF field missing: {expected_pdf_field}")
        else:
            print(f"   ✅ PDF field exists: {expected_pdf_field}")
    
    # 6. Print summary of issues
    print(f"\n6️⃣ SUMMARY OF ISSUES:")
    print("-" * 50)
    
    if issues_found:
        for issue in issues_found:
            print(f"   {issue}")
        
        print(f"\n🔧 RECOMMENDED FIXES:")
        print("-" * 30)
        print("1. Add missing field mappings to field_type_map in pdf_processor.py:")
        print("   'Landlord City': 'city3',")
        print("   'Landlord State': 'text_55cits',") 
        print("   'Landlord ZIP': 'text_56qpfj',")
        print()
        print("2. Add frontend to PDF mappings in app.py:")
        print("   'owner_city': 'city3',")
        print("   'owner_state': 'text_55cits',")
        print("   'owner_zip': 'text_56qpfj',")
        print()
    else:
        print("   ✅ No issues found! All property owner location fields are properly mapped.")
    
    return len(issues_found) == 0

if __name__ == "__main__":
    success = analyze_owner_field_mappings()
    if success:
        print("\n🎉 Property owner field mapping analysis COMPLETE - no issues found!")
    else:
        print("\n⚠️  Property owner field mapping analysis found issues that need fixing.")