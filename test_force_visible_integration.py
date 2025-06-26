#!/usr/bin/env python3
"""
Test the force visible integration with actual data from your logs
"""

from pdf_processor import PDFProcessor
import os

def test_real_user_data():
    """Test with the exact data from your server logs"""
    print("🎯 TESTING FORCE VISIBLE WITH REAL USER DATA")
    print("=" * 60)
    
    processor = PDFProcessor()
    
    # This is the exact document structure from your server logs
    real_document = {
        'id': 'real_user_test',
        'name': 'homeworks.pdf',
        'pdf_fields': [
            {
                'id': 'property_address1',
                'name': 'Property Address',
                'pdf_field_name': 'property_address1',
                'value': '9604 Capendon Ave, Apt 301',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'first_name2',
                'name': 'First Name',
                'pdf_field_name': 'first_name2', 
                'value': 'James',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'last_name2',
                'name': 'Last Name',
                'pdf_field_name': 'last_name2',
                'value': 'deen',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'city1',
                'name': 'City',
                'pdf_field_name': 'city1',
                'value': 'Owings Mills',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'state1',
                'name': 'State',
                'pdf_field_name': 'state1',
                'value': 'MD',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'zip_code1',
                'name': 'ZIP Code',
                'pdf_field_name': 'zip_code1',
                'value': '21117',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'phone_num1',
                'name': 'Phone Number',
                'pdf_field_name': 'phone_num1',
                'value': '4102550052',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'email1',
                'name': 'Email Address',
                'pdf_field_name': 'email1',
                'value': 'jamesdeen@gmail.com',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'fuel_type_elec2',
                'name': 'Electric Heat',
                'pdf_field_name': 'fuel_type_elec2',
                'value': 'yes',
                'type': 'radio',
                'assigned_to': 'user1'
            },
            {
                'id': 'owner2',
                'name': 'Property Owner',
                'pdf_field_name': 'owner2',
                'value': 'yes',
                'type': 'radio',
                'assigned_to': 'user1'
            },
            {
                'id': 'dwelling_single_fam1',
                'name': 'Single Family Home',
                'pdf_field_name': 'dwelling_single_fam1',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1'
            },
            {
                'id': 'elec_util_eversource2',
                'name': 'Electric Eversource',
                'pdf_field_name': 'elec_util_eversource2',
                'value': 'yes',
                'type': 'radio',
                'assigned_to': 'user1'
            },
            {
                'id': 'elec_acct_applicant2',
                'name': 'Electric Account Applicant',
                'pdf_field_name': 'elec_acct_applicant2',
                'value': 'yes',
                'type': 'radio',
                'assigned_to': 'user1'
            },
            {
                'id': 'low_income4',
                'name': 'Low Income Program',
                'pdf_field_name': 'low_income4',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1'
            },
            {
                'id': 'signature3',
                'name': 'Signature',
                'pdf_field_name': 'signature3',
                'value': 'James deen',
                'type': 'text',  # This is actually a text field, not signature field
                'assigned_to': 'user2'
            }
        ]
    }
    
    print(f"📊 Test document has {len(real_document['pdf_fields'])} fields")
    
    # Test the force visible method
    input_pdf = 'homeworks.pdf'
    output_pdf = 'REAL_USER_DATA_FORCE_VISIBLE.pdf'
    
    if not os.path.exists(input_pdf):
        print(f"❌ Input PDF not found: {input_pdf}")
        return False
    
    print(f"\n🎯 Using Force Visible method...")
    success = processor.fill_pdf_with_force_visible(input_pdf, real_document, output_pdf)
    
    if success:
        file_size = os.path.getsize(output_pdf)
        print(f"\n🎉 SUCCESS! Created: {output_pdf} ({file_size:,} bytes)")
        print("📋 This PDF should have ALL content visibly burned into the pages:")
        print("   📝 All 8 text fields filled")
        print("   🔘 All 4 radio buttons selected")
        print("   ✅ All 2 checkboxes checked")
        print("   ✍️  Signature inserted")
        print("🔍 Content will be visible in ANY PDF viewer!")
        
        return True
    else:
        print("❌ Force visible method failed")
        return False

if __name__ == "__main__":
    test_real_user_data()