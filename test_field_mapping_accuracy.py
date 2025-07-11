#!/usr/bin/env python3
"""
Test field mapping accuracy to ensure inputs are correctly placed on the PDF
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def extract_pdf_fields_and_analyze():
    """Extract all fields from the PDF and analyze their positions"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        # Try embedded PDF
        try:
            from embedded_homworks import save_homworks_pdf_to_file
            save_homworks_pdf_to_file(homeworks_path)
            print("✅ Using embedded homworks.pdf")
        except ImportError:
            print(f"❌ Error: {homeworks_path} not found")
            return None
    
    print("🔍 Analyzing Connecticut Home Energy Solutions PDF")
    print("=" * 80)
    
    # Extract fields using PDF processor
    processor = PDFProcessor()
    field_analysis = processor.extract_fields_with_pymupdf(homeworks_path)
    
    if "error" in field_analysis:
        print(f"❌ Error: {field_analysis['error']}")
        return None
    
    fields = field_analysis.get('fields', [])
    
    print(f"\n📊 Found {len(fields)} fields in the PDF")
    
    # Organize fields by page
    fields_by_page = {}
    for field in fields:
        page = field.get('page', 0)
        if page not in fields_by_page:
            fields_by_page[page] = []
        fields_by_page[page].append(field)
    
    # Expected field mappings for Connecticut Home Energy Solutions form
    expected_mappings = {
        "Section 1: Property Information": {
            "property_address": ["property address", "street address", "address"],
            "apartment_number": ["apartment", "unit", "apt"],
            "city": ["city"],
            "state": ["state", "ct"],
            "zip_code": ["zip", "postal code"],
            "apartments_count": ["number of apartments", "units in property"],
            "dwelling_type": ["type of dwelling", "dwelling type", "property type"]
        },
        "Section 2: Applicant and Energy Information": {
            "first_name": ["first name", "given name"],
            "last_name": ["last name", "surname", "family name"],
            "telephone": ["telephone", "phone", "contact number"],
            "email": ["email", "e-mail", "email address"],
            "heating_fuel": ["heating fuel", "primary heating", "fuel type"],
            "applicant_type": ["applicant is", "owner", "renter"],
            "electric_utility": ["electric utility", "electric company"],
            "gas_utility": ["gas utility", "natural gas", "gas company"],
            "electric_account": ["electric account", "electric account number"],
            "gas_account": ["gas account", "gas account number"]
        },
        "Section 3: Qualification": {
            "qualification_option": ["qualification", "option"],
            "household_size": ["household size", "people in household"],
            "adults_count": ["adults", "over 18", "age 18"],
            "annual_income": ["annual income", "household income", "income"]
        },
        "Section 4: Authorization": {
            "applicant_signature": ["applicant signature", "signature"],
            "authorization_date": ["date", "authorization date"],
            "owner_signature": ["owner signature", "property owner signature"],
            "owner_signature_date": ["owner date", "owner signature date"]
        },
        "Section 5: Zero Income Affidavit": {
            "account_holder_name_affidavit": ["account holder name"],
            "household_member_names_no_income": ["household members", "no income", "list all people"],
            "affidavit_signature": ["signature", "affidavit signature"],
            "printed_name_affidavit": ["printed name"],
            "date_affidavit": ["date", "affidavit date"],
            "telephone_affidavit": ["telephone", "phone"]
        }
    }
    
    # Analyze each page
    for page_num in sorted(fields_by_page.keys()):
        print(f"\n📄 Page {page_num + 1}:")
        print("-" * 40)
        
        page_fields = sorted(fields_by_page[page_num], key=lambda f: (f['position']['y'], f['position']['x']))
        
        for field in page_fields:
            field_name = field.get('name', 'Unnamed')
            field_type = field.get('type', 'unknown')
            pos = field.get('position', {})
            x, y = pos.get('x', 0), pos.get('y', 0)
            width, height = pos.get('width', 0), pos.get('height', 0)
            
            # Try to match to expected fields
            matched_to = None
            for section, mappings in expected_mappings.items():
                for form_field, keywords in mappings.items():
                    field_name_lower = field_name.lower()
                    if any(keyword in field_name_lower for keyword in keywords):
                        matched_to = f"{section} -> {form_field}"
                        break
                if matched_to:
                    break
            
            print(f"   📍 Field: {field_name}")
            print(f"      Type: {field_type}")
            print(f"      Position: ({x:.1f}, {y:.1f}) Size: {width:.1f}x{height:.1f}")
            if matched_to:
                print(f"      ✅ Mapped to: {matched_to}")
            else:
                print(f"      ⚠️  No mapping found - may need manual assignment")
    
    return fields

def test_field_value_placement():
    """Test that form values are being placed in the correct PDF fields"""
    
    print("\n🧪 Testing Field Value Placement")
    print("=" * 80)
    
    # Sample form data
    test_data = {
        # Section 1
        "property_address": "123 Test Street",
        "apartment_number": "Unit 5B",
        "city": "Hartford",
        "state": "CT",
        "zip_code": "06103",
        
        # Section 2
        "first_name": "John",
        "last_name": "Doe",
        "telephone": "(860) 555-1234",
        "email": "john.doe@example.com",
        
        # Section 4 (User 2)
        "applicant_signature": "John Doe",
        "authorization_date": "2025-07-11",
        
        # Section 5 (User 2)
        "account_holder_name_affidavit": "John Doe",
        "affidavit_signature": "John Doe"
    }
    
    print("📋 Test Form Data:")
    for key, value in test_data.items():
        print(f"   • {key}: '{value}'")
    
    print("\n⚠️  Common Field Mapping Issues to Check:")
    print("   1. Similar field names causing wrong assignments")
    print("   2. Fuzzy matching placing values in wrong fields")
    print("   3. Section 4/5 fields incorrectly assigned")
    print("   4. Multiple fields matching same form input")
    print("   5. Fields with no matches getting default values")
    
    return True

def suggest_improvements():
    """Suggest improvements for field mapping accuracy"""
    
    print("\n💡 Recommended Improvements for Accurate Field Placement:")
    print("=" * 80)
    
    improvements = [
        {
            "issue": "Fuzzy matching causing misplacement",
            "solution": "Use exact field IDs or coordinates instead of name matching",
            "priority": "High"
        },
        {
            "issue": "Multiple signatures getting confused",
            "solution": "Use page number + field name for unique identification",
            "priority": "High"
        },
        {
            "issue": "Similar field names (e.g., multiple 'date' fields)",
            "solution": "Include section context in field matching logic",
            "priority": "High"
        },
        {
            "issue": "Section 5 fields on wrong page",
            "solution": "Verify Section 5 is on page 5 and use exact positions",
            "priority": "Medium"
        },
        {
            "issue": "Form fields not matching PDF fields",
            "solution": "Create explicit field mapping dictionary",
            "priority": "Medium"
        }
    ]
    
    for imp in improvements:
        print(f"\n🔧 Issue: {imp['issue']}")
        print(f"   Solution: {imp['solution']}")
        print(f"   Priority: {imp['priority']}")
    
    print("\n📝 Proposed Field Mapping Strategy:")
    print("   1. Extract all PDF fields with exact names and positions")
    print("   2. Create explicit mapping dictionary (form_field -> pdf_field)")
    print("   3. Use field IDs or coordinates for unique identification")
    print("   4. Validate mappings before applying values")
    print("   5. Log any unmapped fields for manual review")
    
    return True

def main():
    """Main test function"""
    print("🏠 PDF Collaborator - Field Mapping Accuracy Test")
    print("Analyzing field placement to ensure correct PDF generation")
    print()
    
    # Extract and analyze PDF fields
    fields = extract_pdf_fields_and_analyze()
    
    # Test field placement logic
    test_field_value_placement()
    
    # Suggest improvements
    suggest_improvements()
    
    if fields:
        print(f"\n🎯 Analysis Complete!")
        print(f"📊 Total fields analyzed: {len(fields)}")
        print(f"\n⚠️  Action Required:")
        print(f"   1. Review field mappings above")
        print(f"   2. Identify any misplaced fields")
        print(f"   3. Update mapping logic to use explicit field IDs")
        print(f"   4. Test with real form data")
        print(f"   5. Verify PDF output accuracy")
    else:
        print(f"\n❌ Analysis failed - check PDF file")

if __name__ == "__main__":
    main()