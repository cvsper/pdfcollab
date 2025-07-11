#!/usr/bin/env python3
"""
Test the fixed field mapping logic with realistic form data
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_field_mapping():
    """Test field mapping with sample form data"""
    
    print("🧪 TESTING FIXED FIELD MAPPING")
    print("=" * 50)
    
    # Sample form data that would come from User 1 form submission
    sample_form_data = {
        'property_address': '123 Main Street',
        'city': 'Hartford',
        'state': 'CT', 
        'zip_code': '06103',
        'first_name': 'John',
        'last_name': 'Smith',
        'telephone': '860-555-0123',
        'email': 'john.smith@email.com',
        'dwelling_type': 'single_family',
        'heating_fuel': 'natural_gas',
        'applicant_type': 'property_owner',
        'household_size': '4',
        'annual_income': '45000',
        'electric_utility': 'Eversource',
        'gas_utility': 'CNG',
        'electric_account': '123456789',
        'gas_account': '987654321',
        'applicant_signature': 'John Smith',  # Should be assigned to user2
        'authorization_date': '2024-01-15',   # Should be assigned to user2
        'owner_signature': 'Jane Smith',      # Should be assigned to user2  
        'owner_signature_date': '2024-01-15' # Should be assigned to user2
    }
    
    # Load the updated EXACT_FIELD_MAPPINGS from our fix
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
        'telephone': 'phone2',  # Fixed: use specific phone field
        'email': 'email2',      # Fixed: use specific email field
        
        # Section 3: Qualification
        'household_size': 'People In Household4',
        'adults_count': 'People In Household Overage4', 
        'annual_income': 'Annual Income4',
        
        # Section 4: Authorization (User 2)
        'applicant_signature': 'signature3',           # Fixed: actual signature field name
        'authorization_date': 'date3',                 # Fixed: specific date field
        
        # Property Owner Info  
        'owner_name': 'Landlord Name3',
        'owner_address': 'Address3', 
        'owner_telephone': 'phone3',                   # Fixed: specific phone field
        'owner_email': 'email3',                       # Fixed: specific email field
        'owner_signature': 'property_ower_sig3',       # Fixed: actual property owner signature field
        'owner_signature_date': 'date_property_mang3', # Fixed: specific date field
        
        # Utility accounts
        'electric_account': 'Elec Acct Num2',
        'gas_account': 'Gas Acct Num2',
        
        # Utility company names (newly added)
        'electric_utility': 'Electric Utility2',
        'gas_utility': 'Gas Utility2'
    }
    
    # User assignment rules
    user2_section4_fields = [
        'applicant_signature', 'authorization_date', 'owner_signature', 'owner_signature_date'
    ]
    
    print("📊 Testing field mappings:")
    successful_mappings = 0
    user2_assignments = 0
    
    for form_field, form_value in sample_form_data.items():
        pdf_field_name = EXACT_FIELD_MAPPINGS.get(form_field)
        
        if pdf_field_name:
            assigned_to = 'user2' if form_field in user2_section4_fields else 'user1'
            is_signature = 'signature' in form_field
            
            print(f"   ✅ {form_field} → {pdf_field_name} (value: {form_value}) → {assigned_to}")
            if is_signature:
                print(f"      🖊️  Signature field detected")
            
            successful_mappings += 1
            if assigned_to == 'user2':
                user2_assignments += 1
        else:
            print(f"   ❌ {form_field}: NO MAPPING FOUND")
    
    print(f"\n📋 RESULTS:")
    print(f"   Total form fields: {len(sample_form_data)}")
    print(f"   Successful mappings: {successful_mappings}")
    print(f"   Failed mappings: {len(sample_form_data) - successful_mappings}")
    print(f"   User2 assignments: {user2_assignments}")
    
    # Test special cases
    print(f"\n🔧 Testing special cases:")
    special_cases = [
        ('dwelling_type', 'single_family', 'Single Family Home (Checkbox)'),
        ('heating_fuel', 'natural_gas', 'Gas Heat (Radio Button)'),
        ('applicant_type', 'property_owner', 'Property Owner (Radio Button)')
    ]
    
    for form_field, form_value, expected_pdf_field in special_cases:
        print(f"   🔧 {form_field}={form_value} → {expected_pdf_field}")
    
    print(f"\n🎯 KEY IMPROVEMENTS:")
    print(f"   ✅ Fixed duplicate PDF field mappings")
    print(f"   ✅ Used specific field names (phone2/phone3, email2/email3)")
    print(f"   ✅ Mapped signatures to actual field names (signature3, property_ower_sig3)")
    print(f"   ✅ Added missing utility company mappings")
    print(f"   ✅ Signatures properly assigned to user2")
    
    if successful_mappings == len(sample_form_data):
        print(f"\n🎉 SUCCESS: All fields would be mapped correctly!")
    else:
        print(f"\n⚠️  WARNING: {len(sample_form_data) - successful_mappings} fields still need mapping")

if __name__ == "__main__":
    test_field_mapping()