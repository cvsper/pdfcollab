#!/usr/bin/env python3
"""
Test complete field mapping for all sections of the PDF
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def test_complete_field_mapping():
    """Test mapping for all sections of the PDF form"""
    
    print("🧪 TESTING COMPLETE FIELD MAPPING")
    print("=" * 60)
    
    # Create comprehensive test document with fields from all sections
    test_document = {
        'id': 'complete_mapping_test',
        'name': 'complete_mapping_test.pdf',
        'pdf_fields': [
            # Section 1: Property Information
            {
                'id': 'test_property_address',
                'name': 'Property Address',
                'value': '123 Main Street',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_apt_num',
                'name': 'Apartment Number',
                'value': 'Apt 2B',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_city',
                'name': 'City',
                'value': 'Hartford',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_state',
                'name': 'State',
                'value': 'CT',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_zip',
                'name': 'ZIP Code',
                'value': '06103',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_apartments_count',
                'name': 'Number of Apartments',
                'value': '4',
                'type': 'text',
                'assigned_to': 'user1'
            },
            
            # Section 2: Personal Information
            {
                'id': 'test_first_name',
                'name': 'First Name',
                'value': 'John',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_last_name',
                'name': 'Last Name',
                'value': 'Smith',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_phone',
                'name': 'Phone Number',
                'value': '860-555-1234',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_email',
                'name': 'Email Address',
                'value': 'john.smith@email.com',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_telephone',
                'name': 'Telephone',
                'value': '860-555-5678',
                'type': 'text',
                'assigned_to': 'user1'
            },
            
            # Section 2: Dwelling Type
            {
                'id': 'test_single_family',
                'name': 'Single Family Home (Checkbox)',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1'
            },
            
            # Section 2: Heating Fuel
            {
                'id': 'test_electric_heat',
                'name': 'Electric Heat (Radio Button)',
                'value': 'true',
                'type': 'radio',
                'assigned_to': 'user1'
            },
            
            # Section 2: Applicant Type
            {
                'id': 'test_property_owner',
                'name': 'Property Owner (Radio Button)',
                'value': 'true',
                'type': 'radio',
                'assigned_to': 'user1'
            },
            
            # Section 2: Electric Utility
            {
                'id': 'test_electric_eversource',
                'name': 'Electric Eversource (Radio Button)',
                'value': 'true',
                'type': 'radio',
                'assigned_to': 'user1'
            },
            
            # Section 2: Gas Utility
            {
                'id': 'test_gas_cng',
                'name': 'Gas Util CNG (Radio Button)',
                'value': 'true',
                'type': 'radio',
                'assigned_to': 'user1'
            },
            
            # Section 2: Account Information
            {
                'id': 'test_electric_account_applicant',
                'name': 'Electric Account Applicant (Radio Button)',
                'value': 'true',
                'type': 'radio',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_electric_account_num',
                'name': 'Electric Account Number',
                'value': '123456789',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_gas_account_num',
                'name': 'Gas Account Number',
                'value': '987654321',
                'type': 'text',
                'assigned_to': 'user1'
            },
            
            # Section 3: Qualification Information
            {
                'id': 'test_household_size',
                'name': 'People In Household4',
                'value': '4',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_adults_count',
                'name': 'People In Household Overage4',
                'value': '2',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_annual_income',
                'name': 'Annual Income4',
                'value': '45000',
                'type': 'text',
                'assigned_to': 'user1'
            },
            
            # Section 3: Qualification Options
            {
                'id': 'test_elec_discount',
                'name': 'Elec Discount4 (Checkbox)',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_low_income',
                'name': 'Low Income Program (Checkbox)',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1'
            },
            
            # Section 4: Owner/Landlord Information
            {
                'id': 'test_landlord_name',
                'name': 'Landlord Name',
                'value': 'Jane Property Manager',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_landlord_address',
                'name': 'Landlord Address',
                'value': '456 Owner Street',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_landlord_city',
                'name': 'Landlord City',
                'value': 'New Haven',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_landlord_state',
                'name': 'Landlord State',
                'value': 'CT',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_landlord_zip',
                'name': 'Landlord ZIP',
                'value': '06511',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_landlord_phone',
                'name': 'Landlord Phone',
                'value': '203-555-9999',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_landlord_email',
                'name': 'Landlord Email',
                'value': 'jane@property.com',
                'type': 'text',
                'assigned_to': 'user1'
            },
            
            # Section 4: Signatures and Dates
            {
                'id': 'test_applicant_signature',
                'name': 'Applicant Signature',
                'value': 'John Smith',
                'type': 'signature',
                'assigned_to': 'user2',
                'position': {'x': 43, 'y': 470}
            },
            {
                'id': 'test_property_owner_signature',
                'name': 'Property Owner Signature',
                'value': 'Jane Property Manager',
                'type': 'signature',
                'assigned_to': 'user2',
                'position': {'x': 319, 'y': 612}
            },
            {
                'id': 'test_auth_date',
                'name': 'Date',
                'value': '2025-07-13',
                'type': 'text',
                'assigned_to': 'user2',
                'position': {'x': 441, 'y': 471.0}
            },
            {
                'id': 'test_owner_date',
                'name': 'Date',
                'value': '2025-07-13',
                'type': 'text',
                'assigned_to': 'user2',
                'position': {'x': 321, 'y': 643.0}
            }
        ]
    }
    
    # Test the PDF processor
    processor = PDFProcessor()
    
    # Test with homworks.pdf
    input_pdf = 'homworks.pdf'
    output_pdf = 'COMPLETE_FIELD_MAPPING_TEST.pdf'
    
    if not os.path.exists(input_pdf):
        print(f"❌ {input_pdf} not found")
        return False
    
    print(f"📄 Input PDF: {input_pdf}")
    print(f"📄 Output PDF: {output_pdf}")
    print(f"📊 Testing {len(test_document['pdf_fields'])} fields across all sections")
    
    # Fill the PDF
    success = processor.fill_pdf_with_pymupdf(input_pdf, test_document, output_pdf)
    
    if success:
        print(f"\n✅ PDF filled successfully: {output_pdf}")
        
        # Verify all sections
        print("\n🔍 Verifying all sections in output PDF...")
        
        import fitz
        doc = fitz.open(output_pdf)
        
        # Check Page 3 (main form)
        page3 = doc[2]
        widgets3 = list(page3.widgets())
        
        # Check Page 4 (qualification)
        page4 = doc[3]
        widgets4 = list(page4.widgets())
        
        all_widgets = widgets3 + widgets4
        
        # Expected field counts by section
        section_results = {
            'section1_property': 0,
            'section2_personal': 0,
            'section2_dwelling': 0,
            'section2_utilities': 0,
            'section3_qualification': 0,
            'section4_authorization': 0
        }
        
        filled_fields = []
        for widget in all_widgets:
            if widget.field_value and str(widget.field_value) not in ['', 'False', 'Off']:
                field_name = widget.field_name
                field_value = widget.field_value
                filled_fields.append(f"{field_name}: {field_value}")
                
                # Categorize by section
                if field_name in ['property_address1', 'apt_num1', 'city1', 'state1', 'zip1', 'num_of_apt1']:
                    section_results['section1_property'] += 1
                elif field_name in ['first_name2', 'last_name2', 'phone2', 'email2', 'phone_num1']:
                    section_results['section2_personal'] += 1
                elif field_name in ['dwelling_single_fam1', 'fuel_type_elec2', 'owner2']:
                    section_results['section2_dwelling'] += 1
                elif field_name in ['electric_eversource2', 'gas_util_cng2', 'elect_acct_applicant2', 'elec_acct_num2', 'gas_acct_num2']:
                    section_results['section2_utilities'] += 1
                elif field_name in ['people_in_household4', 'people_in_household_overage4', 'annual_income4', 'elec_discount4', 'low_income4']:
                    section_results['section3_qualification'] += 1
                elif field_name in ['signature3', 'property_ower_sig3', 'date3', 'date_property_mang3', 'landlord_name3', 'address3', 'city3', 'text_55cits', 'text_56qpfj', 'phone3', 'email3']:
                    section_results['section4_authorization'] += 1
        
        doc.close()
        
        print(f"\n📊 SECTION VERIFICATION RESULTS:")
        print(f"   📋 Section 1 - Property Info: {section_results['section1_property']} fields filled")
        print(f"   👤 Section 2 - Personal Info: {section_results['section2_personal']} fields filled")
        print(f"   🏠 Section 2 - Dwelling/Fuel: {section_results['section2_dwelling']} fields filled")
        print(f"   ⚡ Section 2 - Utilities: {section_results['section2_utilities']} fields filled")
        print(f"   💰 Section 3 - Qualification: {section_results['section3_qualification']} fields filled")
        print(f"   ✍️ Section 4 - Authorization: {section_results['section4_authorization']} fields filled")
        
        total_filled = sum(section_results.values())
        print(f"\n📈 TOTAL FIELDS FILLED: {total_filled}")
        
        if total_filled >= 25:  # We expect at least 25 fields to be filled
            print(f"\n🎉 SUCCESS! Complete field mapping is working!")
            print(f"✅ All sections are being filled in the PDF")
            return True
        else:
            print(f"\n⚠️  Only {total_filled} fields were filled (expected at least 25)")
            print("\n🔍 Debug: All filled fields:")
            for field in filled_fields:
                print(f"      {field}")
            return False
    else:
        print("❌ PDF filling failed")
        return False

if __name__ == "__main__":
    success = test_complete_field_mapping()
    if success:
        print("\n🎯 Complete field mapping test PASSED!")
    else:
        print("\n❌ Complete field mapping test FAILED.")