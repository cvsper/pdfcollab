#!/usr/bin/env python3
"""
Test the old PDF processor's signature handling after fix
"""

import os
from pdf_processor import PDFProcessor

def test_old_processor_signature():
    """Test signature handling with the old PDF processor"""
    
    print("🔧 Testing Old PDF Processor Signature Fix")
    print("=" * 50)
    
    # Create processor instance
    processor = PDFProcessor()
    
    # Test PDF path
    pdf_path = "homeworks.pdf"
    
    if not os.path.exists(pdf_path):
        print("❌ homeworks.pdf not found")
        return False
    
    print("📄 Processing homeworks.pdf with old processor...")
    
    # Extract fields
    result = processor.extract_fields_with_pymupdf(pdf_path)
    
    if not result.get('success'):
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return False
    
    fields = result.get('fields', [])
    
    # Find signature fields
    signature_fields = []
    for field in fields:
        if field['type'] == 'signature':
            signature_fields.append(field)
    
    print(f"🔍 Found {len(signature_fields)} signature fields:")
    
    for i, field in enumerate(signature_fields, 1):
        pos = field['position']
        print(f"   {i}. {field.get('display_name', field['name'])}")
        print(f"      PDF Name: {field['name']}")
        print(f"      Type: {field['type']}")
        print(f"      Position: x={pos['x']}, y={pos['y']}")
        print(f"      Size: {pos['width']}x{pos['height']}")
        print(f"      Assigned to: {field.get('assigned_to', 'unknown')}")
        print()
    
    # Test filling with sample document
    if signature_fields:
        print("✍️  Testing signature filling with old processor...")
        
        # Create mock document with signature fields
        document = {
            'name': 'Test Document',
            'file_path': pdf_path,
            'pdf_fields': []
        }
        
        for i, field in enumerate(signature_fields):
            # Assign different names to different signature fields
            if field['name'] == 'signature3':
                signature_name = "John Doe"
                user = "user1"
            elif field['name'] == 'property_ower_sig3':
                signature_name = "Property Manager"
                user = "user2"
            else:
                signature_name = f"Test Signature {i+1}"
                user = field.get('assigned_to', 'user1')
            
            document['pdf_fields'].append({
                'name': field.get('display_name', field['name']),
                'pdf_field_name': field['name'],
                'type': 'signature',
                'value': signature_name,
                'position': field['position'],
                'page': field.get('page', 2),  # Default to page 3
                'assigned_to': user
            })
            
            print(f"   📝 Will sign '{field.get('display_name', field['name'])}' as '{signature_name}' ({user})")
        
        # Generate test PDF
        output_path = "test_old_processor_signatures.pdf"
        success = processor.fill_pdf_with_force_visible(pdf_path, document, output_path)
        
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
    success = test_old_processor_signature()
    
    if success:
        print("\n🎉 Old processor signature test completed!")
        print("💡 Key improvements:")
        print("   - Removed backup red 'SIGNATURE:' text at bottom")
        print("   - Text fields with 'signature' in name treated as signature type")
        print("   - Proper signature placement within field boundaries")
    else:
        print("\n❌ Test failed")