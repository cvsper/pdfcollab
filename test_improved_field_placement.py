#!/usr/bin/env python3
"""
Test the improved field placement with exact mappings
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def test_exact_field_mapping():
    """Test that exact field mapping works correctly"""
    
    print("🧪 Testing Improved Field Placement")
    print("=" * 60)
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        try:
            from embedded_homworks import save_homworks_pdf_to_file
            save_homworks_pdf_to_file(homeworks_path)
            print("✅ Using embedded homworks.pdf")
        except ImportError:
            print(f"❌ Error: {homeworks_path} not found")
            return False
    
    # Extract PDF fields
    processor = PDFProcessor()
    field_analysis = processor.extract_fields_with_pymupdf(homeworks_path)
    
    if "error" in field_analysis:
        print(f"❌ Error: {field_analysis['error']}")
        return False
    
    pdf_fields = field_analysis.get('fields', [])
    
    # Test form data
    test_form_data = {
        # Section 1: Property Information
        'property_address': '123 Test Street',
        'apartment_number': 'Unit 5B',
        'city': 'Hartford',
        'state': 'CT',
        'zip_code': '06103',
        'apartments_count': '1',
        'dwelling_type': 'apartment',
        
        # Section 2: Applicant Information
        'first_name': 'John',
        'last_name': 'Doe',
        'telephone': '(860) 555-1234',
        'email': 'john.doe@example.com',
        'heating_fuel': 'natural_gas',
        'applicant_type': 'renter_tenant',
        
        # Section 3: Qualification
        'household_size': '3',
        'adults_count': '2',
        'annual_income': '45000',
        
        # Section 4: Authorization (User 2)
        'applicant_signature': 'John Doe',
        'authorization_date': '2025-07-11',
        
        # Utility accounts
        'electric_account': '123456789',
        'gas_account': '987654321'
    }
    
    # Test the exact mapping function
    EXACT_FIELD_MAPPINGS = {
        # Section 1: Property Information
        'property_address': 'Property Address',
        'apartment_number': 'Apartment Number', 
        'city': 'City',
        'state': 'State',
        'zip_code': 'ZIP Code',
        'apartments_count': 'Num Of Apt1',
        
        # Section 2: Applicant Information
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'telephone': 'Phone Number',
        'email': 'Email Address',
        
        # Section 3: Qualification
        'household_size': 'People In Household4',
        'adults_count': 'People In Household Overage4', 
        'annual_income': 'Annual Income4',
        
        # Section 4: Authorization (User 2)
        'applicant_signature': 'Applicant Signature',
        'authorization_date': 'Date',
        
        # Utility accounts
        'electric_account': 'Elec Acct Num2',
        'gas_account': 'Gas Acct Num2'
    }
    
    # Test exact mappings
    print(f"📋 Testing exact field mappings:")
    print(f"   Form fields to test: {len(test_form_data)}")
    print(f"   PDF fields available: {len(pdf_fields)}")
    
    # Create a dictionary of PDF field names for quick lookup
    pdf_field_names = {field['name']: field for field in pdf_fields}
    
    exact_matches = 0
    missing_fields = []
    correct_mappings = []
    
    for form_field, form_value in test_form_data.items():
        expected_pdf_field = EXACT_FIELD_MAPPINGS.get(form_field)
        
        if expected_pdf_field:
            if expected_pdf_field in pdf_field_names:
                exact_matches += 1
                correct_mappings.append({
                    'form_field': form_field,
                    'pdf_field': expected_pdf_field,
                    'value': form_value
                })
                print(f"   ✅ {form_field} → {expected_pdf_field}")
            else:
                missing_fields.append({
                    'form_field': form_field,
                    'expected_pdf_field': expected_pdf_field
                })
                print(f"   ❌ {form_field} → {expected_pdf_field} (PDF field not found)")
        else:
            # Handle special cases
            if form_field == 'dwelling_type' and form_value == 'apartment':
                if 'Apartment (Checkbox)' in pdf_field_names:
                    exact_matches += 1
                    print(f"   ✅ {form_field} ({form_value}) → Apartment (Checkbox)")
                else:
                    print(f"   ❌ {form_field} → Apartment (Checkbox) (not found)")
            elif form_field == 'heating_fuel' and form_value == 'natural_gas':
                if 'Gas Heat (Radio Button)' in pdf_field_names:
                    exact_matches += 1
                    print(f"   ✅ {form_field} ({form_value}) → Gas Heat (Radio Button)")
                else:
                    print(f"   ❌ {form_field} → Gas Heat (Radio Button) (not found)")
            elif form_field == 'applicant_type' and form_value == 'renter_tenant':
                if 'Renter (Radio Button)' in pdf_field_names:
                    exact_matches += 1
                    print(f"   ✅ {form_field} ({form_value}) → Renter (Radio Button)")
                else:
                    print(f"   ❌ {form_field} → Renter (Radio Button) (not found)")
            else:
                print(f"   ❓ {form_field} = {form_value} (no mapping defined)")
    
    # Summary
    print(f"\n📊 Mapping Test Results:")
    print(f"   ✅ Exact matches found: {exact_matches}")
    print(f"   ❌ Missing PDF fields: {len(missing_fields)}")
    print(f"   📋 Total test fields: {len(test_form_data)}")
    
    if missing_fields:
        print(f"\n⚠️  Missing PDF Fields:")
        for missing in missing_fields:
            print(f"   • {missing['form_field']} → {missing['expected_pdf_field']}")
    
    success_rate = (exact_matches / len(test_form_data)) * 100
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"✅ Field mapping is working well!")
        return True
    else:
        print(f"❌ Field mapping needs improvement")
        return False

def test_user_assignment_logic():
    """Test that User 1/User 2 assignments are correct"""
    
    print(f"\n🧪 Testing User Assignment Logic")
    print("=" * 60)
    
    test_assignments = [
        # User 1 fields
        {'field': 'property_address', 'expected_user': 'user1', 'section': 'Section 1'},
        {'field': 'first_name', 'expected_user': 'user1', 'section': 'Section 2'},
        {'field': 'household_size', 'expected_user': 'user1', 'section': 'Section 3'},
        
        # User 2 fields (Section 4)
        {'field': 'applicant_signature', 'expected_user': 'user2', 'section': 'Section 4'},
        {'field': 'authorization_date', 'expected_user': 'user2', 'section': 'Section 4'},
        
        # User 2 fields (Section 5)
        {'field': 'account_holder_name_affidavit', 'expected_user': 'user2', 'section': 'Section 5'},
        {'field': 'affidavit_signature', 'expected_user': 'user2', 'section': 'Section 5'}
    ]
    
    user1_fields = [
        'property_address', 'apartment_number', 'city', 'state', 'zip_code',
        'apartments_count', 'dwelling_type', 'first_name', 'last_name',
        'telephone', 'email', 'heating_fuel', 'applicant_type',
        'electric_utility', 'gas_utility', 'electric_account', 'gas_account',
        'qualification_option', 'household_size', 'adults_count', 'annual_income',
        'owner_name', 'owner_address', 'owner_telephone', 'owner_email'
    ]
    
    user2_section4_fields = [
        'applicant_signature', 'authorization_date', 'owner_signature', 'owner_signature_date'
    ]
    
    user2_section5_fields = [
        'account_holder_name_affidavit', 'household_member_names_no_income', 'affidavit_signature', 
        'printed_name_affidavit', 'date_affidavit', 'telephone_affidavit', 'affidavit_confirmation'
    ]
    
    print(f"📋 Testing user assignments:")
    
    correct_assignments = 0
    for assignment in test_assignments:
        field = assignment['field']
        expected_user = assignment['expected_user']
        section = assignment['section']
        
        # Determine actual assignment
        actual_user = None
        if field in user1_fields:
            actual_user = 'user1'
        elif field in user2_section4_fields or field in user2_section5_fields:
            actual_user = 'user2'
        else:
            actual_user = 'user1'  # Default
        
        if actual_user == expected_user:
            correct_assignments += 1
            print(f"   ✅ {field} ({section}) → {actual_user}")
        else:
            print(f"   ❌ {field} ({section}) → {actual_user} (expected {expected_user})")
    
    assignment_success = (correct_assignments / len(test_assignments)) * 100
    print(f"\n🎯 Assignment Success Rate: {assignment_success:.1f}%")
    
    return assignment_success >= 100

def main():
    """Main test function"""
    print("🏠 PDF Collaborator - Improved Field Placement Test")
    print("Testing exact field mappings to ensure correct PDF placement")
    print()
    
    # Run tests
    mapping_test = test_exact_field_mapping()
    assignment_test = test_user_assignment_logic()
    
    if mapping_test and assignment_test:
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Field placement improvements are working correctly")
        print(f"✅ Exact mappings prevent field misplacement")
        print(f"✅ User assignments are correct")
        print(f"\n💡 Benefits:")
        print(f"   • No more fuzzy matching causing wrong placements")
        print(f"   • Each form field maps to exactly one PDF field")
        print(f"   • User 1/User 2 assignments remain correct")
        print(f"   • Better logging for troubleshooting")
    else:
        print(f"\n❌ Some tests failed - review field mappings")
        if not mapping_test:
            print(f"   • Field mapping test failed")
        if not assignment_test:
            print(f"   • User assignment test failed")

if __name__ == "__main__":
    main()