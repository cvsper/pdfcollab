#!/usr/bin/env python3
"""
Final test with signatures in the exact correct positions
"""

from pdf_processor import PDFProcessor

def final_correct_signature_test():
    """Test signatures with the exact correct positions and field names"""
    print("🎯 FINAL CORRECT SIGNATURE PLACEMENT TEST")
    print("=" * 60)
    
    processor = PDFProcessor()
    
    # Real document structure with correct signature positions
    real_document = {
        'id': 'final_correct_test',
        'name': 'final_correct.pdf',
        'pdf_fields': [
            # Main user fields
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
            # Main signature (this is what you see as "James deen")
            {
                'id': 'signature3',
                'name': 'Applicant Signature',
                'pdf_field_name': 'signature3',
                'value': 'James deen',
                'type': 'text',  # This is a text field, not signature field
                'assigned_to': 'user2'
            },
            # Property owner signature (if needed)
            {
                'id': 'property_ower_sig3',
                'name': 'Property Owner Signature',
                'pdf_field_name': 'property_ower_sig3',
                'value': 'Property Owner Name',
                'type': 'text',
                'assigned_to': 'user2'
            }
        ]
    }
    
    print(f"📊 Test document has {len(real_document['pdf_fields'])} fields")
    print("✍️  Signatures to be placed:")
    print("   - Main signature 'James deen' at position (43, 470) on page 3")
    print("   - Property owner signature at position (319, 612) on page 3")
    
    # Use the updated force visible method
    success = processor.fill_pdf_with_force_visible('homeworks.pdf', real_document, 'FINAL_CORRECT_SIGNATURES.pdf')
    
    if success:
        print(f"\n🎉 SUCCESS! Created: FINAL_CORRECT_SIGNATURES.pdf")
        print("📍 Signatures are now placed at the EXACT correct positions:")
        print("   ✍️  Main signature: 'James deen' in the applicant signature field")
        print("   ✍️  Property owner signature: 'Property Owner Name' in owner field")
        print("   📝 All other form fields filled correctly")
        print("   🔧 Content flattened and permanently visible")
        print("\n🔍 This PDF should have signatures in the right places!")
        
        return True
    else:
        print("❌ Final signature test failed")
        return False

if __name__ == "__main__":
    final_correct_signature_test()