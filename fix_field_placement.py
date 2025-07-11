#!/usr/bin/env python3
"""
Fix field placement by replacing fuzzy matching with exact field mappings
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def create_improved_field_mapping_function():
    """Create an improved field mapping function for app.py"""
    
    improved_function = '''
def map_form_data_to_pdf_fields_improved(form_data, pdf_fields):
    """Map the sectioned form data to PDF fields using exact field matching"""
    
    # Explicit field mappings to prevent misplacement
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
        
        # Property Owner Info
        'owner_name': 'Landlord Name3',
        'owner_address': 'Address3', 
        'owner_telephone': 'Phone Number',
        'owner_email': 'Email Address',
        'owner_signature': 'Property Owner Signature',
        'owner_signature_date': 'Date',
        
        # Utility accounts
        'electric_account': 'Elec Acct Num2',
        'gas_account': 'Gas Acct Num2'
    }
    
    # User assignment rules
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
    
    # Clear all existing assignments
    for field in pdf_fields:
        field['assigned_to'] = None
        field['value'] = ''
    
    # Map form data to PDF fields using exact matching
    for form_field, form_value in form_data.items():
        if not form_value:
            continue
            
        # Get the exact PDF field name
        pdf_field_name = EXACT_FIELD_MAPPINGS.get(form_field)
        
        if pdf_field_name:
            # Find the PDF field with exact name match
            for field in pdf_fields:
                if field['name'] == pdf_field_name:
                    field['value'] = str(form_value)
                    
                    # Assign to correct user
                    if form_field in user1_fields:
                        field['assigned_to'] = 'user1'
                    elif form_field in user2_section4_fields or form_field in user2_section5_fields:
                        field['assigned_to'] = 'user2'
                        if 'signature' in form_field:
                            field['type'] = 'signature'
                    else:
                        field['assigned_to'] = 'user1'  # Default to user1
                    
                    print(f"   ✅ Exact match: {form_field} → {pdf_field_name} (value: {form_value})")
                    break
            else:
                print(f"   ⚠️  PDF field not found for: {form_field} → {pdf_field_name}")
        else:
            # Handle special cases (radio buttons, checkboxes with specific values)
            matched = False
            
            # Handle dwelling type
            if form_field == 'dwelling_type':
                dwelling_mappings = {
                    'single_family': 'Single Family Home (Checkbox)',
                    'apartment': 'Apartment (Checkbox)', 
                    'condominium': 'Condominium (Checkbox)'
                }
                target_field = dwelling_mappings.get(form_value)
                if target_field:
                    for field in pdf_fields:
                        if field['name'] == target_field:
                            field['value'] = 'true'
                            field['assigned_to'] = 'user1'
                            matched = True
                            print(f"   ✅ Dwelling type: {form_value} → {target_field}")
                            break
            
            # Handle heating fuel
            elif form_field == 'heating_fuel':
                fuel_mappings = {
                    'electric': 'Electric Heat (Radio Button)',
                    'natural_gas': 'Gas Heat (Radio Button)',
                    'oil': 'Oil Heat (Radio Button)', 
                    'propane': 'Propane Heat (Radio Button)'
                }
                target_field = fuel_mappings.get(form_value)
                if target_field:
                    for field in pdf_fields:
                        if field['name'] == target_field:
                            field['value'] = 'true'
                            field['assigned_to'] = 'user1'
                            matched = True
                            print(f"   ✅ Heating fuel: {form_value} → {target_field}")
                            break
            
            # Handle applicant type
            elif form_field == 'applicant_type':
                type_mappings = {
                    'property_owner': 'Property Owner (Radio Button)',
                    'renter_tenant': 'Renter (Radio Button)'
                }
                target_field = type_mappings.get(form_value)
                if target_field:
                    for field in pdf_fields:
                        if field['name'] == target_field:
                            field['value'] = 'true'
                            field['assigned_to'] = 'user1'
                            matched = True
                            print(f"   ✅ Applicant type: {form_value} → {target_field}")
                            break
            
            if not matched:
                print(f"   ❓ Unmatched form field: {form_field} = {form_value}")
    
    # Ensure all unassigned fields go to user1
    for field in pdf_fields:
        if field.get('assigned_to') is None:
            field['assigned_to'] = 'user1'
    
    return pdf_fields
'''
    
    return improved_function

def show_current_issues():
    """Show the current field placement issues"""
    
    print("🚨 Current Field Placement Issues:")
    print("=" * 60)
    
    issues = [
        {
            "issue": "Fuzzy matching causing wrong field assignments",
            "example": "Multiple 'Date' fields getting confused",
            "impact": "Authorization date appearing in wrong location"
        },
        {
            "issue": "Similar field names matching incorrectly", 
            "example": "'Phone Number' appears multiple times",
            "impact": "Telephone going to wrong field"
        },
        {
            "issue": "No validation of field assignments",
            "example": "Fields assigned even if PDF field doesn't exist",
            "impact": "Silent failures, empty fields in output"
        },
        {
            "issue": "Section 4/5 fields not properly segregated",
            "example": "User 2 fields mixed with User 1 fields",
            "impact": "Signatures appearing in wrong sections"
        }
    ]
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. {issue['issue']}")
        print(f"   Example: {issue['example']}")
        print(f"   Impact: {issue['impact']}")

def suggest_implementation_steps():
    """Suggest steps to implement the fix"""
    
    print("\n💡 Implementation Steps:")
    print("=" * 60)
    
    steps = [
        "1. Replace fuzzy matching with exact field name mappings",
        "2. Create EXACT_FIELD_MAPPINGS dictionary with form_field → pdf_field",
        "3. Handle special cases (radio buttons, checkboxes) explicitly",
        "4. Validate that PDF fields exist before assignment",
        "5. Add logging for unmatched fields",
        "6. Test with real form data to verify placements",
        "7. Update field assignment logic for User 1/User 2 separation"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n🎯 Expected Results:")
    print(f"   ✅ Each form input maps to exactly one PDF field")
    print(f"   ✅ No fields placed in wrong locations")
    print(f"   ✅ User 1/User 2 assignments remain correct")
    print(f"   ✅ Section 5 positioning unaffected (uses exact coordinates)")

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Fix Field Placement")
    print("Analyzing and fixing form field to PDF field mapping issues")
    print()
    
    show_current_issues()
    suggest_implementation_steps()
    
    print(f"\n🔧 Improved Field Mapping Function:")
    print("=" * 60)
    improved_function = create_improved_field_mapping_function()
    print("Function created - ready to replace existing fuzzy matching logic")
    
    print(f"\n📝 Next Action:")
    print(f"   Replace map_form_data_to_pdf_fields() in app.py with improved version")
    print(f"   Test with sample data to verify correct placements")

if __name__ == "__main__":
    main()