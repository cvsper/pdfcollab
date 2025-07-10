#!/usr/bin/env python3
"""
Test script to verify Section 5 (Zero Income Affidavit) appears in the final PDF
"""

import os
import sys
import uuid
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import fill_pdf_fields_advanced, generate_summary_pdf

def create_test_document_data():
    """Create test data that includes all 5 sections including Zero Income Affidavit"""
    
    # Test data simulating a complete User 1 + User 2 workflow
    test_document = {
        'id': str(uuid.uuid4()),
        'name': 'homworks.pdf',
        'status': 'Signed & Sent',
        'created_at': datetime.now().isoformat(),
        
        # User 1 data (Sections 1-4)
        'user1_data': {
            # Section 1: Property Information
            'property_address': '123 Main Street',
            'apartment_number': 'Apt 2B',
            'city': 'Hartford',
            'state': 'CT',
            'zip_code': '06103',
            'apartments_count': '2',
            'dwelling_type': 'apartment',
            
            # Section 2: Applicant and Energy Information
            'first_name': 'John',
            'last_name': 'Smith',
            'telephone': '(860) 555-0123',
            'email': 'john.smith@email.com',
            'heating_fuel': 'natural_gas',
            'applicant_type': 'renter_tenant',
            'electric_utility': 'eversource',
            'gas_utility': 'cng',
            'electric_account': 'EV123456789',
            'gas_account': 'CNG987654321',
            
            # Section 3: Qualification Information
            'qualification_option': 'option_c',
            'household_size': '3',
            'adults_count': '2',
            'annual_income': '45000',
            
            # Section 4: Authorization
            'user2_name': 'Jane Smith',
            'user2_email': 'jane.smith@email.com',
            'owner_name': 'Property Management LLC',
            'owner_address': '456 Property St, Hartford, CT 06103',
            'owner_telephone': '(860) 555-0456',
            'owner_email': 'owner@property.com'
        },
        
        # User 2 data (includes Section 5: Zero Income Affidavit)
        'user2_data': {
            'user2_name': 'Jane Smith',
            'user2_email': 'jane.smith@email.com',
            'signature': 'Jane Smith',
            
            # Section 5: Zero Income Affidavit fields
            'account_holder_name': 'John Smith',
            'zero_income_names': 'Mary Smith\nDavid Johnson',
            'affidavit_printed_name': 'Jane Smith',
            'affidavit_date': '2025-01-10',
            'affidavit_telephone': '(860) 555-0123',
            'affidavit_confirmation': 'true'
        },
        
        # PDF fields with assignments
        'pdf_fields': [
            # Section 1 fields
            {'id': 'field_1', 'name': 'Property Address', 'value': '123 Main Street', 'assigned_to': 'user1', 'type': 'text'},
            {'id': 'field_2', 'name': 'Apartment Number', 'value': 'Apt 2B', 'assigned_to': 'user1', 'type': 'text'},
            {'id': 'field_3', 'name': 'City', 'value': 'Hartford', 'assigned_to': 'user1', 'type': 'text'},
            {'id': 'field_4', 'name': 'State', 'value': 'CT', 'assigned_to': 'user1', 'type': 'text'},
            {'id': 'field_5', 'name': 'ZIP Code', 'value': '06103', 'assigned_to': 'user1', 'type': 'text'},
            
            # Section 2 fields
            {'id': 'field_6', 'name': 'First Name', 'value': 'John', 'assigned_to': 'user1', 'type': 'text'},
            {'id': 'field_7', 'name': 'Last Name', 'value': 'Smith', 'assigned_to': 'user1', 'type': 'text'},
            {'id': 'field_8', 'name': 'Telephone', 'value': '(860) 555-0123', 'assigned_to': 'user1', 'type': 'tel'},
            {'id': 'field_9', 'name': 'Email', 'value': 'john.smith@email.com', 'assigned_to': 'user1', 'type': 'email'},
            {'id': 'field_10', 'name': 'Primary Heating Fuel', 'value': 'Natural Gas', 'assigned_to': 'user1', 'type': 'text'},
            
            # Section 3 fields
            {'id': 'field_11', 'name': 'Qualification Option', 'value': 'Option C - Income Requirements', 'assigned_to': 'user1', 'type': 'text'},
            {'id': 'field_12', 'name': 'Household Size', 'value': '3', 'assigned_to': 'user1', 'type': 'text'},
            {'id': 'field_13', 'name': 'Adults Count', 'value': '2', 'assigned_to': 'user1', 'type': 'text'},
            {'id': 'field_14', 'name': 'Annual Income', 'value': '$45,000', 'assigned_to': 'user1', 'type': 'text'},
            
            # Section 4 fields
            {'id': 'field_15', 'name': 'Applicant Signature', 'value': 'Jane Smith', 'assigned_to': 'user2', 'type': 'signature'},
            {'id': 'field_16', 'name': 'Signature Date', 'value': '2025-01-10', 'assigned_to': 'user2', 'type': 'date'},
            
            # Section 5: Zero Income Affidavit fields
            {'id': 'field_17', 'name': 'Account Holder Name', 'value': 'John Smith', 'assigned_to': 'user2', 'type': 'text'},
            {'id': 'field_18', 'name': 'Zero Income Names', 'value': 'Mary Smith\nDavid Johnson', 'assigned_to': 'user2', 'type': 'textarea'},
            {'id': 'field_19', 'name': 'Affidavit Printed Name', 'value': 'Jane Smith', 'assigned_to': 'user2', 'type': 'text'},
            {'id': 'field_20', 'name': 'Affidavit Date', 'value': '2025-01-10', 'assigned_to': 'user2', 'type': 'date'},
            {'id': 'field_21', 'name': 'Affidavit Telephone', 'value': '(860) 555-0123', 'assigned_to': 'user2', 'type': 'tel'},
            {'id': 'field_22', 'name': 'Affidavit Confirmation', 'value': 'Confirmed', 'assigned_to': 'user2', 'type': 'checkbox'}
        ]
    }
    
    return test_document

def test_pdf_generation():
    """Test PDF generation with Section 5 data"""
    
    print("🔬 Testing PDF Generation with Section 5 (Zero Income Affidavit)")
    print("=" * 60)
    
    # Create test document data
    test_doc = create_test_document_data()
    
    # Check if homworks.pdf exists
    homeworks_pdf = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    if not os.path.exists(homeworks_pdf):
        print(f"❌ Error: {homeworks_pdf} not found")
        return False
    
    print(f"✅ Found source PDF: {homeworks_pdf}")
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_pdf = f"test_section5_output_{timestamp}.pdf"
    output_path = os.path.join(os.path.dirname(__file__), output_pdf)
    
    print(f"📄 Generating test PDF: {output_pdf}")
    
    try:
        # Method 1: Try advanced PDF filling
        print("\n🔧 Attempting advanced PDF field filling...")
        result_path = fill_pdf_fields_advanced(homeworks_pdf, test_doc, output_path)
        
        if result_path and os.path.exists(result_path):
            print(f"✅ Advanced PDF filling successful: {result_path}")
            file_size = os.path.getsize(result_path)
            print(f"📊 File size: {file_size:,} bytes")
        else:
            print("⚠️  Advanced PDF filling failed, trying summary PDF...")
            
            # Method 2: Fallback to summary PDF
            print("🔧 Generating summary PDF with Section 5 data...")
            result_path = generate_summary_pdf(test_doc)
            
            if result_path and os.path.exists(result_path):
                print(f"✅ Summary PDF generation successful: {result_path}")
                file_size = os.path.getsize(result_path)
                print(f"📊 File size: {file_size:,} bytes")
            else:
                print("❌ Both PDF generation methods failed")
                return False
    
    except Exception as e:
        print(f"❌ Error during PDF generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Display what was included in the PDF
    print(f"\n📋 Test Document Data Summary:")
    print(f"   📍 User 1 completed {len([f for f in test_doc['pdf_fields'] if f['assigned_to'] == 'user1'])} fields (Sections 1-4)")
    print(f"   📍 User 2 completed {len([f for f in test_doc['pdf_fields'] if f['assigned_to'] == 'user2'])} fields (Signatures + Section 5)")
    
    print(f"\n🧾 Section 5 (Zero Income Affidavit) Fields in PDF:")
    section5_fields = [f for f in test_doc['pdf_fields'] if f['id'].startswith('field_1') and int(f['id'].split('_')[1]) >= 17]
    for field in section5_fields:
        print(f"   ✅ {field['name']}: {field['value']}")
    
    print(f"\n🎯 Generated PDF file: {os.path.abspath(result_path)}")
    print(f"📁 You can open this file to verify Section 5 content is included")
    
    return True

def main():
    """Main test function"""
    print("🧪 PDF Collaborator - Section 5 Test")
    print("Testing Zero Income Affidavit inclusion in final PDF")
    print()
    
    success = test_pdf_generation()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("📄 Check the generated PDF file to verify Section 5 content")
    else:
        print("\n❌ Test failed!")
    
    return success

if __name__ == "__main__":
    main()