#!/usr/bin/env python3
"""
Test the improved signature processor with fallback placement
"""

from pdf_processor import PDFProcessor

def test_improved_signature():
    """Test improved signature with fallback placements"""
    print("🎯 TESTING IMPROVED SIGNATURE PROCESSOR")
    print("=" * 50)
    
    processor = PDFProcessor()
    
    # Test with signature as both 'signature' and 'text' type
    test_document = {
        'id': 'improved_signature_test',
        'name': 'improved_test.pdf',
        'pdf_fields': [
            # Add some regular fields for context
            {
                'id': 'property_address1',
                'name': 'Property Address',
                'pdf_field_name': 'property_address1',
                'value': '9604 Capendon Ave, Apt 301',
                'type': 'text',
                'assigned_to': 'user1'
            },
            # Signature field as text type (what actually works)
            {
                'id': 'signature3',
                'name': 'Signature',
                'pdf_field_name': 'signature3',
                'value': 'James deen',
                'type': 'text',  # This is how it actually exists in the PDF
                'assigned_to': 'user2'
            },
            # Also test as signature type to trigger fallback logic
            {
                'id': 'signature_fallback',
                'name': 'Signature Fallback',
                'pdf_field_name': 'signature3',
                'value': 'James deen FALLBACK',
                'type': 'signature',  # This will trigger the fallback placement
                'assigned_to': 'user2'
            }
        ]
    }
    
    print(f"📊 Test document has {len(test_document['pdf_fields'])} fields")
    
    # Test the improved force visible method
    success = processor.fill_pdf_with_force_visible('homeworks.pdf', test_document, 'IMPROVED_SIGNATURE_OUTPUT.pdf')
    
    if success:
        print(f"\n🎉 SUCCESS! Created: IMPROVED_SIGNATURE_OUTPUT.pdf")
        print("📋 This PDF should have:")
        print("   📝 Property address filled")
        print("   ✍️  Signature in the form field")
        print("   ✍️  Signature overlay at expected position")
        print("   🔴 RED backup signature at bottom of page")
        print("   🔧 All content flattened and permanently visible")
        print("\n🔍 The signature should now be impossible to miss!")
        
        return True
    else:
        print("❌ Improved signature test failed")
        return False

if __name__ == "__main__":
    test_improved_signature()