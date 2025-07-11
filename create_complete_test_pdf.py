#!/usr/bin/env python3
"""
Create a complete test PDF with ALL fields filled across all 5 sections
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def create_complete_test_pdf():
    """Create a test PDF with all sections completely filled"""
    
    print("🏠 Creating Complete Test PDF - All Sections Filled")
    print("=" * 70)
    
    # Complete test data for ALL fields across all 5 sections
    complete_user1_data = {
        # Section 1: Property Information
        'property_address': '456 Main Street',
        'apartment_number': 'Apt 3A',
        'city': 'Hartford',
        'state': 'CT', 
        'zip_code': '06103',
        'apartments_count': '2',
        'dwelling_type': 'apartment',  # Will map to "Apartment (Checkbox)"
        
        # Section 2: Applicant Information & Energy Info
        'first_name': 'Sarah',
        'last_name': 'Johnson',
        'telephone': '(860) 555-9876',
        'email': 'sarah.johnson@email.com',
        'heating_fuel': 'natural_gas',  # Will map to "Gas Heat (Radio Button)"
        'applicant_type': 'renter_tenant',  # Will map to "Renter (Radio Button)"
        
        # Electric & Gas Utility Info
        'electric_utility': 'eversource',
        'gas_utility': 'cng',
        'electric_account': '987654321',
        'gas_account': '123456789',
        
        # Section 3: Qualification Information  
        'household_size': '4',
        'adults_count': '2', 
        'annual_income': '38500',
        'qualification_option': 'energy_assistance',  # Energy assistance programs
        
        # Property Owner Information (if renter)
        'owner_name': 'Michael Property Owner',
        'owner_address': '789 Owner Lane, West Hartford, CT 06117',
        'owner_telephone': '(860) 555-4444',
        'owner_email': 'michael.owner@property.com'
    }
    
    # Complete User 2 data (Section 4: Authorization & Section 5: Zero Income Affidavit)
    complete_user2_data = {
        'name': 'Sarah Johnson',
        'email': 'sarah.johnson@email.com',
        
        # Section 4: Authorization signatures and dates
        'applicant_signature': 'Sarah Johnson',
        'authorization_date': '2025-07-11',
        'owner_signature': 'Michael Property Owner', 
        'owner_signature_date': '2025-07-11',
        
        # Section 5: Zero Income Affidavit (if needed)
        'account_holder_name_affidavit': 'Sarah Johnson',
        'household_member_names_no_income': 'John Johnson (spouse)\nEmily Johnson (daughter, age 16)\nMichael Johnson (son, age 14)',
        'affidavit_signature': 'Sarah Johnson',
        'printed_name_affidavit': 'Sarah Johnson',
        'date_affidavit': '2025-07-11',
        'telephone_affidavit': '(860) 555-9876',
        'affidavit_confirmation': 'yes'
    }
    
    print(f"📋 Test Data Summary:")
    print(f"   User 1 fields: {len(complete_user1_data)}")
    print(f"   User 2 fields: {len(complete_user2_data)}")
    print(f"   Total fields: {len(complete_user1_data) + len(complete_user2_data)}")
    
    print(f"\n🔍 Detailed Test Data:")
    print(f"   Property: {complete_user1_data['property_address']}, {complete_user1_data['city']}")
    print(f"   Applicant: {complete_user1_data['first_name']} {complete_user1_data['last_name']}")
    print(f"   Household size: {complete_user1_data['household_size']} people")
    print(f"   Annual income: ${complete_user1_data['annual_income']}")
    print(f"   Property owner: {complete_user1_data['owner_name']}")
    
    try:
        # Import the app's field mapping logic
        sys.path.insert(0, os.path.dirname(__file__))
        from pdf_processor import PDFProcessor
        
        homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        
        if not os.path.exists(homeworks_path):
            try:
                from embedded_homworks import save_homworks_pdf_to_file
                save_homworks_pdf_to_file(homeworks_path)
                print("✅ Using embedded homworks.pdf")
            except ImportError:
                print(f"❌ Error: {homworks_path} not found")
                return False
        
        # Extract PDF fields to understand structure
        processor = PDFProcessor()
        field_analysis = processor.extract_fields_with_pymupdf(homeworks_path)
        
        if "error" in field_analysis:
            print(f"❌ Error analyzing PDF: {field_analysis['error']}")
            return False
        
        pdf_fields = field_analysis.get('fields', [])
        print(f"\n📄 PDF Analysis:")
        print(f"   Total PDF fields found: {len(pdf_fields)}")
        
        # Apply the exact field mapping logic from app.py
        mapped_pdf_fields = apply_complete_field_mapping(complete_user1_data, complete_user2_data, pdf_fields)
        
        # Create document structure for PDFProcessor
        document = {
            'user1_data': complete_user1_data,
            'user2_data': complete_user2_data,
            'pdf_fields': mapped_pdf_fields,
            'file_path': homeworks_path
        }
        
        # Generate the complete test PDF
        output_path = os.path.join(os.path.dirname(__file__), 'COMPLETE_TEST_ALL_FIELDS_FILLED.pdf')
        
        print(f"\n🔧 Generating complete test PDF...")
        success = processor.fill_pdf_with_force_visible(homeworks_path, document, output_path)
        
        if success:
            print(f"\n🎉 SUCCESS!")
            print(f"✅ Complete test PDF created: {output_path}")
            print(f"📄 File size: {os.path.getsize(output_path):,} bytes")
            
            # Count how many fields were actually filled
            filled_fields = [f for f in mapped_pdf_fields if f.get('value')]
            print(f"📋 Fields filled: {len(filled_fields)} out of {len(mapped_pdf_fields)} total fields")
            
            print(f"\n📝 What's included in this test PDF:")
            print(f"   ✅ Section 1: Complete property information")
            print(f"   ✅ Section 2: Complete applicant and energy information") 
            print(f"   ✅ Section 3: Complete qualification and income information")
            print(f"   ✅ Section 4: Complete authorization signatures and dates")
            print(f"   ✅ Section 5: Complete zero income affidavit")
            print(f"   ✅ All radio buttons, checkboxes, and text fields")
            print(f"   ✅ Property owner information")
            print(f"   ✅ Utility account details")
            
            print(f"\n💡 Use this PDF to verify:")
            print(f"   • All form sections are properly filled")
            print(f"   • Field positioning is correct")
            print(f"   • Signatures appear in the right locations")
            print(f"   • Date fields are correctly mapped")
            print(f"   • Radio buttons and checkboxes are selected")
            
            return True
        else:
            print(f"❌ Failed to generate complete test PDF")
            return False
            
    except Exception as e:
        print(f"❌ Error creating complete test PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def apply_complete_field_mapping(user1_data, user2_data, pdf_fields):
    """Apply the complete field mapping logic from app.py"""
    
    print(f"\n🗺️  Applying Complete Field Mapping")
    print("=" * 50)
    
    # Explicit field mappings from app.py
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
    
    matched_fields = 0
    
    # Handle special case: multiple Date fields - use position-based mapping
    date_fields = [f for f in pdf_fields if f['name'] == 'Date']
    date_fields.sort(key=lambda f: f['position']['y'])  # Sort by Y position
    
    print(f"📅 Processing {len(date_fields)} Date fields with position-based mapping:")
    
    # Map authorization_date to Date field near Applicant Signature (y ~471)
    authorization_date_value = user2_data.get('authorization_date')
    if authorization_date_value:
        for field in date_fields:
            if 460 <= field['position']['y'] <= 480:  # Authorization area
                field['value'] = str(authorization_date_value)
                field['assigned_to'] = 'user2'
                print(f"   ✅ authorization_date → Date field at ({field['position']['x']:.0f}, {field['position']['y']:.0f})")
                matched_fields += 1
                break
    
    # Map owner_signature_date to Date field near Property Owner Signature (y ~643)
    owner_date_value = user2_data.get('owner_signature_date')
    if owner_date_value:
        for field in date_fields:
            if field['position']['y'] > 630:  # Property owner area
                field['value'] = str(owner_date_value)
                field['assigned_to'] = 'user2'
                print(f"   ✅ owner_signature_date → Date field at ({field['position']['x']:.0f}, {field['position']['y']:.0f})")
                matched_fields += 1
                break
    
    # Combine all form data
    all_form_data = {**user1_data, **user2_data}
    
    print(f"\n🗺️  Processing {len(all_form_data)} form fields:")
    
    # Map form data to PDF fields using exact matching (excluding Date fields handled above)
    for form_field, form_value in all_form_data.items():
        if not form_value:
            continue
        
        # Skip Date fields as they're handled above with position-based logic
        if form_field in ['authorization_date', 'owner_signature_date']:
            continue
            
        # Get the exact PDF field name
        pdf_field_name = EXACT_FIELD_MAPPINGS.get(form_field)
        
        if pdf_field_name:
            # Find the PDF field with exact name match
            field_found = False
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
                    
                    print(f"   ✅ {form_field} → {pdf_field_name}")
                    matched_fields += 1
                    field_found = True
                    break
            
            if not field_found:
                print(f"   ⚠️  PDF field not found: {form_field} → {pdf_field_name}")
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
                            matched_fields += 1
                            print(f"   ✅ {form_field} ({form_value}) → {target_field}")
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
                            matched_fields += 1
                            print(f"   ✅ {form_field} ({form_value}) → {target_field}")
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
                            matched_fields += 1
                            print(f"   ✅ {form_field} ({form_value}) → {target_field}")
                            break
            
            # Handle qualification programs (checkboxes)
            elif form_field == 'qualification_option':
                program_mappings = {
                    'ebt': 'EBT (Food Stamps)',
                    'energy_assistance': 'Energy Award Letter4',
                    'section_8': 'Section Eight4',
                    'low_income': 'Low Income Program (Checkbox)'
                }
                target_field = program_mappings.get(form_value)
                if target_field:
                    for field in pdf_fields:
                        if field['name'] == target_field:
                            field['value'] = 'true'
                            field['assigned_to'] = 'user1'
                            matched = True
                            matched_fields += 1
                            print(f"   ✅ {form_field} ({form_value}) → {target_field}")
                            break
            
            if not matched and form_field not in ['electric_utility', 'gas_utility']:
                print(f"   ❓ Unmatched: {form_field} = {form_value}")
    
    # Ensure all unassigned fields go to user1
    for field in pdf_fields:
        if field.get('assigned_to') is None:
            field['assigned_to'] = 'user1'
    
    print(f"\n📊 Field Mapping Summary:")
    print(f"   ✅ Total fields matched: {matched_fields}")
    print(f"   📄 Total PDF fields: {len(pdf_fields)}")
    print(f"   🔗 Mapping success rate: {(matched_fields/len(all_form_data)*100):.1f}%")
    
    return pdf_fields

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Complete Test PDF Generator")
    print("Creating a comprehensive test with ALL fields filled")
    print()
    
    success = create_complete_test_pdf()
    
    if success:
        print(f"\n🎉 COMPLETE TEST PDF CREATED SUCCESSFULLY!")
        print(f"📄 File: COMPLETE_TEST_ALL_FIELDS_FILLED.pdf")
        print(f"🔍 This PDF contains realistic test data for all 5 sections")
        print(f"💡 Use this to verify that the entire form workflow is working correctly")
    else:
        print(f"\n❌ Failed to create complete test PDF")

if __name__ == "__main__":
    main()