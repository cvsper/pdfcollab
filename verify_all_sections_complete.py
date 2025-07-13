#!/usr/bin/env python3
"""
Final verification that all sections of the PDF are properly mapped and filled
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def verify_all_sections_complete():
    """Final verification of complete PDF form filling"""
    
    print("🎯 FINAL VERIFICATION - ALL SECTIONS COMPLETE")
    print("=" * 60)
    
    # Create the most comprehensive test with data for every section
    complete_test_document = {
        'id': 'final_verification',
        'name': 'final_verification.pdf',
        'pdf_fields': [
            # Section 1: Property Information (6 fields)
            {'id': 'prop_addr', 'name': 'Property Address', 'value': '789 Complete Street', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'apt_num', 'name': 'Apartment Number', 'value': 'Suite 12C', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'prop_city', 'name': 'City', 'value': 'Bridgeport', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'prop_state', 'name': 'State', 'value': 'CT', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'prop_zip', 'name': 'ZIP Code', 'value': '06604', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'apt_count', 'name': 'Number of Apartments', 'value': '6', 'type': 'text', 'assigned_to': 'user1'},
            
            # Section 2: Personal Information (5 fields)
            {'id': 'fname', 'name': 'First Name', 'value': 'Ana', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'lname', 'name': 'Last Name', 'value': 'Gonzalez', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'phone_main', 'name': 'Phone Number', 'value': '203-555-7777', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'email_main', 'name': 'Email Address', 'value': 'ana.gonzalez@test.com', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'phone_alt', 'name': 'Telephone', 'value': '203-555-8888', 'type': 'text', 'assigned_to': 'user1'},
            
            # Section 2: Dwelling & Energy (6 fields)
            {'id': 'dwelling', 'name': 'Single Family Home (Checkbox)', 'value': 'true', 'type': 'checkbox', 'assigned_to': 'user1'},
            {'id': 'fuel_elec', 'name': 'Electric Heat (Radio Button)', 'value': 'true', 'type': 'radio', 'assigned_to': 'user1'},
            {'id': 'app_type', 'name': 'Property Owner (Radio Button)', 'value': 'true', 'type': 'radio', 'assigned_to': 'user1'},
            {'id': 'elec_util', 'name': 'Electric Eversource (Radio Button)', 'value': 'true', 'type': 'radio', 'assigned_to': 'user1'},
            {'id': 'gas_util', 'name': 'Gas Util CNG (Radio Button)', 'value': 'true', 'type': 'radio', 'assigned_to': 'user1'},
            {'id': 'elec_acct_type', 'name': 'Electric Account Applicant (Radio Button)', 'value': 'true', 'type': 'radio', 'assigned_to': 'user1'},
            
            # Section 2: Account Numbers (2 fields)
            {'id': 'elec_num', 'name': 'Electric Account Number', 'value': '555666777', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'gas_num', 'name': 'Gas Account Number', 'value': '777888999', 'type': 'text', 'assigned_to': 'user1'},
            
            # Section 3: Qualification (8 fields)
            {'id': 'hh_size', 'name': 'People In Household4', 'value': '5', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'adults', 'name': 'People In Household Overage4', 'value': '3', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'income', 'name': 'Annual Income4', 'value': '52000', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'elec_disc', 'name': 'Elec Discount4 (Checkbox)', 'value': 'true', 'type': 'checkbox', 'assigned_to': 'user1'},
            {'id': 'low_inc', 'name': 'Low Income Program (Checkbox)', 'value': 'true', 'type': 'checkbox', 'assigned_to': 'user1'},
            {'id': 'bill_forg', 'name': 'Bill Forgiveness Program (Checkbox)', 'value': 'true', 'type': 'checkbox', 'assigned_to': 'user1'},
            {'id': 'ebt_prog', 'name': 'EBT (Food Stamps) (Checkbox)', 'value': 'true', 'type': 'checkbox', 'assigned_to': 'user1'},
            {'id': 'multifam', 'name': 'Multifam4 (Checkbox)', 'value': 'true', 'type': 'checkbox', 'assigned_to': 'user1'},
            
            # Section 4: Property Owner Info (7 fields)
            {'id': 'owner_name', 'name': 'Landlord Name', 'value': 'XYZ Real Estate LLC', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'owner_addr', 'name': 'Landlord Address', 'value': '100 Business Park Drive', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'owner_city', 'name': 'Landlord City', 'value': 'Stamford', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'owner_state', 'name': 'Landlord State', 'value': 'CT', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'owner_zip', 'name': 'Landlord ZIP', 'value': '06901', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'owner_phone', 'name': 'Landlord Phone', 'value': '203-555-0000', 'type': 'text', 'assigned_to': 'user1'},
            {'id': 'owner_email', 'name': 'Landlord Email', 'value': 'info@xyzrealestate.com', 'type': 'text', 'assigned_to': 'user1'},
            
            # Section 4: Signatures & Dates (4 fields)
            {'id': 'app_sig', 'name': 'Applicant Signature', 'value': 'Ana Gonzalez', 'type': 'signature', 'assigned_to': 'user2', 'position': {'x': 43, 'y': 470}},
            {'id': 'prop_sig', 'name': 'Property Owner Signature', 'value': 'XYZ Real Estate LLC', 'type': 'signature', 'assigned_to': 'user2', 'position': {'x': 319, 'y': 612}},
            {'id': 'app_date', 'name': 'Date', 'value': '2025-07-13', 'type': 'text', 'assigned_to': 'user2', 'position': {'x': 441, 'y': 471.0}},
            {'id': 'prop_date', 'name': 'Date', 'value': '2025-07-13', 'type': 'text', 'assigned_to': 'user2', 'position': {'x': 321, 'y': 643.0}}
        ]
    }
    
    # Test with comprehensive data
    processor = PDFProcessor()
    input_pdf = 'homworks.pdf'
    output_pdf = 'FINAL_COMPLETE_VERIFICATION.pdf'
    
    if not os.path.exists(input_pdf):
        print(f"❌ {input_pdf} not found")
        return False
    
    print(f"📄 Testing with {len(complete_test_document['pdf_fields'])} fields across ALL sections")
    
    # Generate the PDF
    success = processor.fill_pdf_with_pymupdf(input_pdf, complete_test_document, output_pdf)
    
    if success:
        print(f"\n✅ Final verification PDF generated: {output_pdf}")
        
        # Verify comprehensive coverage
        import fitz
        doc = fitz.open(output_pdf)
        
        # Count filled fields by section
        page3_widgets = list(doc[2].widgets())  # Main form
        page4_widgets = list(doc[3].widgets())  # Qualification
        all_widgets = page3_widgets + page4_widgets
        
        section_counts = {
            'section1_property': 0,
            'section2_personal': 0, 
            'section2_energy': 0,
            'section2_accounts': 0,
            'section3_qualification': 0,
            'section4_owner_info': 0,
            'section4_signatures': 0
        }
        
        total_filled = 0
        for widget in all_widgets:
            if widget.field_value and str(widget.field_value) not in ['', 'False', 'Off']:
                field_name = widget.field_name
                total_filled += 1
                
                # Categorize each field
                if field_name in ['property_address1', 'apt_num1', 'city1', 'state1', 'zip1', 'num_of_apt1']:
                    section_counts['section1_property'] += 1
                elif field_name in ['first_name2', 'last_name2', 'phone2', 'email2', 'phone_num1']:
                    section_counts['section2_personal'] += 1
                elif field_name in ['dwelling_single_fam1', 'fuel_type_elec2', 'owner2', 'electric_eversource2', 'gas_util_cng2', 'elect_acct_applicant2']:
                    section_counts['section2_energy'] += 1
                elif field_name in ['elec_acct_num2', 'gas_acct_num2']:
                    section_counts['section2_accounts'] += 1
                elif field_name in ['people_in_household4', 'people_in_household_overage4', 'annual_income4', 'elec_discount4', 'low_income4', 'bill_forgive4', 'ebt4', 'multifam4']:
                    section_counts['section3_qualification'] += 1
                elif field_name in ['landlord_name3', 'address3', 'city3', 'text_55cits', 'text_56qpfj', 'phone3', 'email3']:
                    section_counts['section4_owner_info'] += 1
                elif field_name in ['signature3', 'property_ower_sig3', 'date3', 'date_property_mang3']:
                    section_counts['section4_signatures'] += 1
        
        doc.close()
        
        print(f"\n📊 FINAL COMPREHENSIVE RESULTS:")
        print(f"   📋 Section 1 - Property Information: {section_counts['section1_property']}/6 fields ({'✅' if section_counts['section1_property'] >= 6 else '⚠️'})")
        print(f"   👤 Section 2 - Personal Information: {section_counts['section2_personal']}/5 fields ({'✅' if section_counts['section2_personal'] >= 5 else '⚠️'})")
        print(f"   ⚡ Section 2 - Energy & Dwelling: {section_counts['section2_energy']}/6 fields ({'✅' if section_counts['section2_energy'] >= 6 else '⚠️'})")
        print(f"   🔢 Section 2 - Account Numbers: {section_counts['section2_accounts']}/2 fields ({'✅' if section_counts['section2_accounts'] >= 2 else '⚠️'})")
        print(f"   💰 Section 3 - Qualification: {section_counts['section3_qualification']}/8 fields ({'✅' if section_counts['section3_qualification'] >= 8 else '⚠️'})")
        print(f"   🏢 Section 4 - Owner Information: {section_counts['section4_owner_info']}/7 fields ({'✅' if section_counts['section4_owner_info'] >= 7 else '⚠️'})")
        print(f"   ✍️ Section 4 - Signatures & Dates: {section_counts['section4_signatures']}/4 fields ({'✅' if section_counts['section4_signatures'] >= 4 else '⚠️'})")
        
        print(f"\n🎯 TOTAL FIELDS FILLED: {total_filled}/38 expected")
        
        # Success criteria
        all_sections_complete = (
            section_counts['section1_property'] >= 6 and
            section_counts['section2_personal'] >= 5 and
            section_counts['section2_energy'] >= 6 and
            section_counts['section2_accounts'] >= 2 and
            section_counts['section3_qualification'] >= 8 and
            section_counts['section4_owner_info'] >= 7 and
            section_counts['section4_signatures'] >= 4
        )
        
        if all_sections_complete and total_filled >= 35:
            print(f"\n🎉 🎉 SUCCESS! ALL SECTIONS COMPLETE! 🎉 🎉")
            print(f"✅ Every section of the PDF form is properly filled")
            print(f"✅ All field mappings are working correctly")
            print(f"✅ User issue resolved: All fields now appear in downloaded PDF")
            return True
        else:
            print(f"\n⚠️  Some sections still need work:")
            if section_counts['section1_property'] < 6:
                print(f"   - Section 1 needs work")
            if section_counts['section2_personal'] < 5:
                print(f"   - Section 2 personal info needs work")
            if section_counts['section2_energy'] < 6:
                print(f"   - Section 2 energy info needs work")
            if section_counts['section2_accounts'] < 2:
                print(f"   - Section 2 accounts need work")
            if section_counts['section3_qualification'] < 8:
                print(f"   - Section 3 qualification needs work")
            if section_counts['section4_owner_info'] < 7:
                print(f"   - Section 4 owner info needs work")
            if section_counts['section4_signatures'] < 4:
                print(f"   - Section 4 signatures need work")
            return False
    else:
        print("❌ Final verification PDF generation failed")
        return False

if __name__ == "__main__":
    success = verify_all_sections_complete()
    if success:
        print("\n🚀 ALL SECTIONS OF THE PDF FORM ARE NOW WORKING!")
        print("🎯 User can now download PDFs with all fields properly filled")
    else:
        print("\n❌ Some sections still need fixes")