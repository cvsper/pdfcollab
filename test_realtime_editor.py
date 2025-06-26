#!/usr/bin/env python3
"""
Test the Real-Time PDF Editor functionality
"""

import requests
import json
import time
import uuid
from realtime_pdf_processor import get_realtime_pdf_processor

def test_realtime_pdf_processor():
    """Test the real-time PDF processor with the homeworks.pdf file"""
    print("🎯 TESTING REAL-TIME PDF PROCESSOR")
    print("=" * 60)
    
    processor = get_realtime_pdf_processor()
    
    # Test 1: Extract PDF info
    print("\n1️⃣ EXTRACTING PDF INFO")
    print("-" * 30)
    
    pdf_info = processor.extract_pdf_info('homeworks.pdf')
    if 'error' in pdf_info:
        print(f"❌ Error: {pdf_info['error']}")
        return False
    
    print(f"✅ PDF Info extracted:")
    print(f"   📄 Pages: {pdf_info['page_count']}")
    print(f"   📏 Page 1 size: {pdf_info['pages'][0]['width']} x {pdf_info['pages'][0]['height']}")
    print(f"   📊 File size: {pdf_info['file_size']:,} bytes")
    
    # Test 2: Detect fields with positions
    print("\n2️⃣ DETECTING FIELDS WITH POSITIONS")
    print("-" * 30)
    
    field_detection = processor.detect_fields_with_positions('homeworks.pdf')
    if 'error' in field_detection:
        print(f"❌ Error: {field_detection['error']}")
        return False
    
    fields = field_detection['fields']
    print(f"✅ Detected {len(fields)} fields:")
    
    # Show field summary by type
    field_types = {}
    for field in fields:
        field_type = field['type']
        if field_type not in field_types:
            field_types[field_type] = []
        field_types[field_type].append(field)
    
    for field_type, type_fields in field_types.items():
        print(f"   📝 {field_type.upper()}: {len(type_fields)} fields")
        for field in type_fields[:3]:  # Show first 3 of each type
            pos = field['position']
            print(f"      - {field['name']} at ({pos['x']:.1f}, {pos['y']:.1f}) on page {pos['page']}")
        if len(type_fields) > 3:
            print(f"      ... and {len(type_fields) - 3} more")
    
    # Test 3: Create sample field data and fill PDF
    print("\n3️⃣ TESTING REAL-TIME PDF FILLING")
    print("-" * 30)
    
    # Create realistic field values based on detected fields
    field_values = {}
    for field in fields[:10]:  # Test with first 10 fields
        field_values[field['id']] = {
            'value': get_sample_value_for_field(field),
            'pdf_field_name': field['pdf_field_name'],
            'type': field['type'],
            'name': field['name'],
            'position': field['position'],
            'styling': field.get('styling', {})
        }
    
    print(f"📋 Created sample data for {len(field_values)} fields")
    
    # Fill PDF with real-time processor
    output_path = 'REALTIME_TEST_OUTPUT.pdf'
    success = processor.fill_pdf_realtime('homeworks.pdf', field_values, output_path)
    
    if success:
        import os
        file_size = os.path.getsize(output_path)
        print(f"✅ Real-time PDF created: {output_path} ({file_size:,} bytes)")
        print("🎉 Real-time PDF processor test completed successfully!")
        return True
    else:
        print("❌ Real-time PDF filling failed")
        return False

def get_sample_value_for_field(field):
    """Generate realistic sample values based on field type and name"""
    field_type = field['type']
    field_name = field['name'].lower()
    
    if field_type == 'text':
        if 'name' in field_name:
            if 'first' in field_name:
                return 'John'
            elif 'last' in field_name:
                return 'Smith'
            else:
                return 'John Smith'
        elif 'address' in field_name:
            return '123 Main Street, Apt 456'
        elif 'city' in field_name:
            return 'New York'
        elif 'state' in field_name:
            return 'NY'
        elif 'zip' in field_name:
            return '10001'
        elif 'phone' in field_name:
            return '(555) 123-4567'
        elif 'email' in field_name:
            return 'john.smith@example.com'
        else:
            return f'Sample text for {field["name"]}'
    
    elif field_type == 'email':
        return 'john.smith@example.com'
    
    elif field_type == 'tel':
        return '(555) 123-4567'
    
    elif field_type == 'date':
        return '2024-06-19'
    
    elif field_type in ['checkbox', 'radio']:
        return 'true'
    
    elif field_type == 'signature':
        return 'John Smith'
    
    else:
        return f'Sample value for {field["name"]}'

def test_field_validation():
    """Test field data validation"""
    print("\n4️⃣ TESTING FIELD VALIDATION")
    print("-" * 30)
    
    processor = get_realtime_pdf_processor()
    
    # Test valid field data
    valid_field = {
        'id': str(uuid.uuid4()),
        'name': 'Test Field',
        'type': 'text',
        'position': {
            'x': 100,
            'y': 200,
            'width': 150,
            'height': 25,
            'page': 1
        },
        'value': 'Test Value'
    }
    
    try:
        validated = processor.validate_field_data(valid_field)
        print("✅ Valid field data passed validation")
    except Exception as e:
        print(f"❌ Valid field data failed validation: {e}")
        return False
    
    # Test invalid field data
    invalid_field = {
        'id': str(uuid.uuid4()),
        'name': 'Test Field',
        'type': 'invalid_type',
        'position': {
            'x': 100,
            'y': 200,
            # Missing width, height, page
        }
    }
    
    try:
        validated = processor.validate_field_data(invalid_field)
        print("❌ Invalid field data should have failed validation")
        return False
    except Exception as e:
        print(f"✅ Invalid field data correctly failed validation: {e}")
    
    print("🎉 Field validation test completed successfully!")
    return True

def test_preview_generation():
    """Test PDF preview generation"""
    print("\n5️⃣ TESTING PREVIEW GENERATION")
    print("-" * 30)
    
    processor = get_realtime_pdf_processor()
    
    # Generate preview for first page
    preview_base64 = processor.generate_pdf_preview('homeworks.pdf', page_num=1, scale=1.0)
    
    if preview_base64:
        print(f"✅ Preview generated: {len(preview_base64)} characters of base64 data")
        
        # Save preview to file for inspection
        import base64
        with open('preview_test.png', 'wb') as f:
            f.write(base64.b64decode(preview_base64))
        print("📄 Preview saved as 'preview_test.png'")
        
        return True
    else:
        print("❌ Preview generation failed")
        return False

def main():
    """Run all real-time PDF editor tests"""
    print("🚀 REAL-TIME PDF EDITOR TEST SUITE")
    print("=" * 70)
    
    # Check if homeworks.pdf exists
    if not os.path.exists('homeworks.pdf'):
        print("❌ homeworks.pdf not found. Please ensure the test PDF exists.")
        return False
    
    tests = [
        test_realtime_pdf_processor,
        test_field_validation,
        test_preview_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ Test passed\n")
            else:
                print("❌ Test failed\n")
        except Exception as e:
            print(f"❌ Test error: {e}\n")
    
    print("=" * 70)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Real-time PDF editor is ready!")
        print("\n🚀 NEXT STEPS:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start the server: python app.py")
        print("3. Open browser: http://localhost:5006/realtime-editor")
        print("4. Upload a PDF and start editing in real-time!")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    import os
    main()