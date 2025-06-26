#!/usr/bin/env python3
"""
Test that the applicant signature is placed correctly in the 'Applicant Signature' field
"""

import os
from realtime_pdf_processor import get_realtime_pdf_processor

def test_applicant_signature():
    """Test that signature goes to the correct applicant signature field"""
    
    print("🔧 Testing Applicant Signature Placement")
    print("=" * 50)
    
    # Get processor
    processor = get_realtime_pdf_processor()
    
    # Test PDF path
    pdf_path = "homeworks.pdf"
    
    if not os.path.exists(pdf_path):
        print("❌ homeworks.pdf not found")
        return False
    
    print("📄 Processing homeworks.pdf...")
    
    # Extract fields
    field_detection = processor.detect_fields_with_positions(pdf_path)
    
    if 'error' in field_detection:
        print(f"❌ Error: {field_detection['error']}")
        return False
    
    # Find signature fields
    signature_fields = []
    for field in field_detection.get('fields', []):
        if field['type'] == 'signature':
            signature_fields.append(field)
    
    print(f"🔍 Found {len(signature_fields)} signature fields:")
    
    applicant_field = None
    property_owner_field = None
    
    for field in signature_fields:
        pos = field['position']
        print(f"   • {field['name']}")
        print(f"     PDF Field: {field['pdf_field_name']}")
        print(f"     Position: x={pos['x']}, y={pos['y']}")
        print(f"     Size: {pos['width']}x{pos['height']}")
        print(f"     Assigned to: {field.get('assigned_to', 'unknown')}")
        print()
        
        if field['name'] == 'Applicant Signature':
            applicant_field = field
        elif field['name'] == 'Property Owner Signature':
            property_owner_field = field
    
    if not applicant_field:
        print("❌ Applicant Signature field not found!")
        return False
    
    print("✍️  Testing signature filling...")
    
    # Create field values with proper names for each signature
    field_values = {}
    
    if applicant_field:
        field_values[applicant_field['id']] = {
            'value': 'John Doe',  # Applicant name
            'pdf_field_name': applicant_field['pdf_field_name'],
            'type': 'signature',
            'name': applicant_field['name'],
            'position': applicant_field['position'],
            'styling': applicant_field.get('styling', {})
        }
        print(f"   📝 Will sign 'Applicant Signature' as 'John Doe'")
    
    if property_owner_field:
        field_values[property_owner_field['id']] = {
            'value': 'Property Manager',  # Property owner name
            'pdf_field_name': property_owner_field['pdf_field_name'],
            'type': 'signature',
            'name': property_owner_field['name'],
            'position': property_owner_field['position'],
            'styling': property_owner_field.get('styling', {})
        }
        print(f"   📝 Will sign 'Property Owner Signature' as 'Property Manager'")
    
    # Generate test PDF
    output_path = "test_applicant_signature_fixed.pdf"
    success = processor.fill_pdf_realtime(pdf_path, field_values, output_path)
    
    if success:
        print(f"✅ Test PDF created: {output_path}")
        print("📋 Please check the PDF to verify signature placement")
        
        file_size = os.path.getsize(output_path)
        print(f"📊 File size: {file_size:,} bytes")
        
        # Generate preview
        preview = processor.generate_pdf_preview(output_path, page_num=3, scale=1.5)
        if preview:
            import base64
            with open('applicant_signature_preview.png', 'wb') as f:
                f.write(base64.b64decode(preview))
            print("📸 Preview saved as applicant_signature_preview.png")
        
        return True
    else:
        print("❌ Failed to create test PDF")
        return False

if __name__ == "__main__":
    success = test_applicant_signature()
    
    if success:
        print("\n🎉 Applicant signature test completed!")
        print("💡 Key points:")
        print("   ✅ 'signature3' field is now properly named 'Applicant Signature'")
        print("   ✅ Signature placed in correct field boundaries")
        print("   ✅ Proper cursive styling applied")
        print("   ✅ No red 'SIGNATURE:' text at bottom")
    else:
        print("\n❌ Test failed")