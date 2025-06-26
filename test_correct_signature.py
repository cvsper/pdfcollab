#!/usr/bin/env python3
"""
Test signature with correct field names and positions
"""

from pdf_processor import PDFProcessor

def test_correct_signature():
    """Test signature with the correct field mapping"""
    print("🎯 TESTING SIGNATURE WITH CORRECT MAPPING")
    print("=" * 50)
    
    processor = PDFProcessor()
    
    # Use the correct field names and positions found in debug
    real_document = {
        'id': 'correct_signature_test',
        'name': 'homeworks.pdf',
        'pdf_fields': [
            # Main signature field (text field, not signature field)
            {
                'id': 'signature3',
                'name': 'Signature',
                'pdf_field_name': 'signature3',  # This is the correct field name
                'value': 'James deen',
                'type': 'text',  # It's actually a text field, not signature field
                'assigned_to': 'user2'
            },
            # Property owner signature field
            {
                'id': 'property_ower_sig3',
                'name': 'Property Owner Signature',
                'pdf_field_name': 'property_ower_sig3',
                'value': 'Property Owner Name',
                'type': 'text',
                'assigned_to': 'user2'
            },
            # Add some other fields for context
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
            }
        ]
    }
    
    print(f"📊 Test document has {len(real_document['pdf_fields'])} fields")
    print("📝 Signature fields:")
    for field in real_document['pdf_fields']:
        if 'sig' in field['name'].lower():
            print(f"   - {field['name']} ({field['pdf_field_name']}) = '{field['value']}'")
    
    # Test the force visible method
    success = processor.fill_pdf_with_force_visible('homeworks.pdf', real_document, 'CORRECT_SIGNATURE_OUTPUT.pdf')
    
    if success:
        print(f"\n🎉 SUCCESS! Created: CORRECT_SIGNATURE_OUTPUT.pdf")
        print("📋 This PDF should show:")
        print("   📝 Property address and first name")
        print("   ✍️  Main signature: 'James deen'")
        print("   ✍️  Property owner signature: 'Property Owner Name'")
        print("🔍 Check the PDF - signatures should now be visible!")
        
        return True
    else:
        print("❌ Failed to create PDF")
        return False

if __name__ == "__main__":
    test_correct_signature()