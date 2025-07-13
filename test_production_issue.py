#!/usr/bin/env python3
"""
Test to diagnose why field mappings are failing in production
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import json

def test_production_issue():
    """Diagnose the field mapping issue from production"""
    
    print("🔍 DIAGNOSING PRODUCTION FIELD MAPPING ISSUE")
    print("=" * 60)
    
    # Step 1: Extract fields exactly like production
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    
    if "error" in pdf_analysis:
        print(f"❌ Error: {pdf_analysis['error']}")
        return False
    
    pdf_fields = pdf_analysis['fields']
    print(f"✅ Extracted {len(pdf_fields)} fields from PDF")
    
    # Step 2: Show what field names are available
    print("\n📋 Field structure analysis:")
    sample_field = pdf_fields[0]
    print(f"   Sample field keys: {list(sample_field.keys())}")
    print(f"   Sample field data: {json.dumps(sample_field, indent=2)}")
    
    # Step 3: Simulate the exact mapping logic from app.py
    print("\n🔍 Testing EXACT_FIELD_MAPPINGS from app.py:")
    
    EXACT_FIELD_MAPPINGS = {
        'property_address': 'property_address1',
        'apartment_number': 'apt_num1',
        'city': 'city1',
        'state': 'state1',
        'zip_code': 'zip1'
    }
    
    # Test form data
    form_data = {
        'property_address': '9604 Capendon Ave, Apt 301',
        'apartment_number': '5',
        'city': 'Palm Beach Gardens',
        'state': 'FL',
        'zip_code': '33418'
    }
    
    print("\n🔍 Attempting to map fields:")
    
    for form_field, pdf_field_name in EXACT_FIELD_MAPPINGS.items():
        form_value = form_data.get(form_field, '')
        if form_value:
            print(f"\n   Mapping: {form_field} → {pdf_field_name}")
            print(f"   Form value: '{form_value}'")
            
            # Method 1: Find by pdf_field_name
            found_by_pdf_name = False
            for field in pdf_fields:
                if field.get('pdf_field_name') == pdf_field_name:
                    found_by_pdf_name = True
                    print(f"   ✅ Found by pdf_field_name: {field['name']}")
                    break
            
            if not found_by_pdf_name:
                print(f"   ❌ NOT FOUND by pdf_field_name")
                
                # Method 2: Find by name
                for field in pdf_fields:
                    if field.get('name', '').lower() == form_field.replace('_', ' '):
                        print(f"   💡 Found by display name: {field['name']} (pdf_field: {field.get('pdf_field_name', 'N/A')})")
                        break
    
    # Step 4: Show the mapping table we need
    print("\n📊 MAPPING TABLE NEEDED:")
    print("Form Field → Display Name → PDF Field Name")
    print("-" * 50)
    
    # Create the proper mapping
    needed_mappings = {
        'property_address': 'Property Address',
        'apartment_number': 'Apartment Number',
        'city': 'City',
        'state': 'State',
        'zip_code': 'ZIP Code',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'telephone': 'Phone Number',
        'email': 'Email Address'
    }
    
    for form_field, display_name in needed_mappings.items():
        # Find the field with this display name
        for field in pdf_fields:
            if field['name'] == display_name:
                pdf_field_name = field.get('pdf_field_name', 'N/A')
                print(f"{form_field} → {display_name} → {pdf_field_name}")
                break
    
    # Step 5: Test the fix
    print("\n🔧 TESTING THE FIX:")
    print("The issue is that app.py is looking for fields by pdf_field_name")
    print("but should be looking by display name first.")
    
    return True

if __name__ == "__main__":
    test_production_issue()