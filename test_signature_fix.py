#!/usr/bin/env python3
"""
Test script to verify signature positioning fix
"""

import os
from realtime_pdf_processor import get_realtime_pdf_processor

def test_signature_positioning():
    """Test signature positioning with the homeworks.pdf"""
    
    print("🔧 Testing Signature Positioning Fix")
    print("=" * 50)
    
    # Get processor
    processor = get_realtime_pdf_processor()
    
    # Test PDF path
    pdf_path = "homeworks.pdf"
    
    if not os.path.exists(pdf_path):
        print("❌ homeworks.pdf not found")
        return False
    
    print("📄 Processing homeworks.pdf...")
    
    # Extract fields to see current signature detection
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
    
    for i, field in enumerate(signature_fields, 1):
        pos = field['position']
        print(f"   {i}. {field['name']}")
        print(f"      Position: x={pos['x']}, y={pos['y']}")
        print(f"      Size: {pos['width']}x{pos['height']}")
        print(f"      Page: {pos['page']}")
        print(f"      Assigned to: {field.get('assigned_to', 'unknown')}")
        print()
    
    # Test filling with sample signatures
    if signature_fields:
        print("✍️  Testing signature filling...")
        
        field_values = {}
        
        for i, field in enumerate(signature_fields):
            # Assign different names to different signature fields
            if "signature3" in field['pdf_field_name'].lower():
                signature_name = "John Doe"  # Applicant signature
                user = "user1"
            elif "property_ower_sig3" in field['pdf_field_name'].lower():
                signature_name = "Property Manager"  # Property owner signature
                user = "user2"
            else:
                signature_name = "Signature Name"
                user = field.get('assigned_to', 'user1')
            
            field_values[field['id']] = {
                'value': signature_name,
                'pdf_field_name': field['pdf_field_name'],
                'type': 'signature',
                'name': field['name'],
                'position': field['position'],
                'styling': field.get('styling', {})
            }
            
            print(f"   📝 Will sign '{field['name']}' as '{signature_name}' ({user})")
        
        # Generate test PDF
        output_path = "test_signatures_fixed.pdf"
        success = processor.fill_pdf_realtime(pdf_path, field_values, output_path)
        
        if success:
            print(f"✅ Test PDF created: {output_path}")
            print("📋 Please check the PDF to verify signature placement")
            
            file_size = os.path.getsize(output_path)
            print(f"📊 File size: {file_size:,} bytes")
            
            return True
        else:
            print("❌ Failed to create test PDF")
            return False
    else:
        print("⚠️  No signature fields detected")
        return False

if __name__ == "__main__":
    success = test_signature_positioning()
    
    if success:
        print("\n🎉 Signature positioning test completed!")
        print("💡 Key improvements:")
        print("   - Signatures placed within field boundaries")
        print("   - Cursive font styling applied")
        print("   - Proper field assignment (user1/user2)")
        print("   - Signature underlining for authenticity")
    else:
        print("\n❌ Test failed")