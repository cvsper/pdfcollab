#!/usr/bin/env python3
"""
Debug signature placement to identify and fix positioning issues
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def analyze_signature_fields():
    """Analyze all signature fields and their exact positions"""
    
    print("🔍 SIGNATURE PLACEMENT ANALYSIS")
    print("=" * 60)
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        try:
            from embedded_homworks import save_homworks_pdf_to_file
            save_homworks_pdf_to_file(homeworks_path)
            print("✅ Using embedded homworks.pdf")
        except ImportError:
            print(f"❌ Error: {homeworks_path} not found")
            return False
    
    # Extract PDF fields
    processor = PDFProcessor()
    field_analysis = processor.extract_fields_with_pymupdf(homeworks_path)
    
    if "error" in field_analysis:
        print(f"❌ Error: {field_analysis['error']}")
        return False
    
    pdf_fields = field_analysis.get('fields', [])
    
    # Find all signature fields
    signature_fields = []
    date_fields = []
    
    for field in pdf_fields:
        field_name = field.get('name', '')
        field_type = field.get('type', '')
        position = field.get('position', {})
        page = field.get('page', 0)
        
        if 'signature' in field_name.lower() or field_type == 'signature':
            signature_fields.append({
                'name': field_name,
                'type': field_type,
                'page': page + 1,
                'x': position.get('x', 0),
                'y': position.get('y', 0),
                'width': position.get('width', 0),
                'height': position.get('height', 0),
                'rect': f"({position.get('x', 0):.1f}, {position.get('y', 0):.1f}, {position.get('width', 0):.1f}, {position.get('height', 0):.1f})"
            })
        
        if 'date' in field_name.lower():
            date_fields.append({
                'name': field_name,
                'type': field_type,
                'page': page + 1,
                'x': position.get('x', 0),
                'y': position.get('y', 0),
                'rect': f"({position.get('x', 0):.1f}, {position.get('y', 0):.1f})"
            })
    
    print(f"📋 Found {len(signature_fields)} signature fields:")
    for i, field in enumerate(signature_fields):
        print(f"   {i+1}. {field['name']}")
        print(f"      Type: {field['type']}")
        print(f"      Page: {field['page']}")
        print(f"      Position: ({field['x']:.1f}, {field['y']:.1f})")
        print(f"      Size: {field['width']:.1f} x {field['height']:.1f}")
        print(f"      Rect: {field['rect']}")
        
        # Determine context
        if field['y'] > 600:
            context = "Property Owner area (bottom)"
        elif 450 <= field['y'] <= 500:
            context = "Applicant Authorization area (middle)"
        else:
            context = "Other area"
        print(f"      Context: {context}")
        print()
    
    print(f"📅 Found {len(date_fields)} date fields (for reference):")
    for i, field in enumerate(date_fields):
        print(f"   {i+1}. {field['name']} at {field['rect']} on page {field['page']}")
    
    return signature_fields, date_fields

def test_signature_positioning():
    """Test signature positioning with current logic"""
    
    print(f"\n🧪 TESTING CURRENT SIGNATURE POSITIONING")
    print("=" * 60)
    
    # Test data with signatures
    test_data = {
        'applicant_signature': 'John Doe Test Signature',
        'owner_signature': 'Property Owner Test Signature'
    }
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    try:
        from pdf_processor import PDFProcessor
        processor = PDFProcessor()
        
        # Extract fields to see current mapping
        field_analysis = processor.extract_fields_with_pymupdf(homeworks_path)
        pdf_fields = field_analysis.get('fields', [])
        
        # Apply field mapping
        mapped_fields = []
        
        for field in pdf_fields:
            field_name = field.get('name', '')
            if field_name == 'Applicant Signature':
                field['value'] = test_data['applicant_signature']
                field['type'] = 'signature'
                field['assigned_to'] = 'user2'
                mapped_fields.append(field)
                print(f"✅ Mapped applicant_signature to: {field_name}")
                print(f"   Position: ({field['position']['x']:.1f}, {field['position']['y']:.1f})")
                print(f"   Size: {field['position']['width']:.1f} x {field['position']['height']:.1f}")
            
            elif field_name == 'Property Owner Signature':
                field['value'] = test_data['owner_signature']
                field['type'] = 'signature'
                field['assigned_to'] = 'user2'
                mapped_fields.append(field)
                print(f"✅ Mapped owner_signature to: {field_name}")
                print(f"   Position: ({field['position']['x']:.1f}, {field['position']['y']:.1f})")
                print(f"   Size: {field['position']['width']:.1f} x {field['position']['height']:.1f}")
        
        if not mapped_fields:
            print("❌ No signature fields were mapped!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing signature positioning: {e}")
        return False

def create_signature_test_pdf():
    """Create a test PDF focused on signature placement"""
    
    print(f"\n🔧 CREATING SIGNATURE-FOCUSED TEST PDF")
    print("=" * 60)
    
    # Minimal test data focused on signatures
    test_user1_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'property_address': '123 Test Street'
    }
    
    test_user2_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'applicant_signature': 'Test User Signature',
        'authorization_date': '2025-07-11',
        'owner_signature': 'Property Owner Signature',
        'owner_signature_date': '2025-07-11'
    }
    
    try:
        from pdf_processor import PDFProcessor
        
        homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        processor = PDFProcessor()
        
        # Create document structure
        document = {
            'user1_data': test_user1_data,
            'user2_data': test_user2_data
        }
        
        # Add pdf_fields with proper mapping
        field_analysis = processor.extract_fields_with_pymupdf(homeworks_path)
        pdf_fields = field_analysis.get('fields', [])
        
        # Map the signature fields specifically
        for field in pdf_fields:
            field_name = field.get('name', '')
            if field_name == 'Applicant Signature':
                field['value'] = test_user2_data['applicant_signature']
                field['type'] = 'signature'
                field['assigned_to'] = 'user2'
                field['pdf_field_name'] = field_name
                print(f"📝 Mapping: applicant_signature → {field_name}")
                print(f"   Value: {field['value']}")
                print(f"   Position: ({field['position']['x']:.1f}, {field['position']['y']:.1f})")
            
            elif field_name == 'Property Owner Signature':
                field['value'] = test_user2_data['owner_signature']
                field['type'] = 'signature'
                field['assigned_to'] = 'user2'
                field['pdf_field_name'] = field_name
                print(f"📝 Mapping: owner_signature → {field_name}")
                print(f"   Value: {field['value']}")
                print(f"   Position: ({field['position']['x']:.1f}, {field['position']['y']:.1f})")
        
        document['pdf_fields'] = pdf_fields
        
        # Generate test PDF
        output_path = os.path.join(os.path.dirname(__file__), 'SIGNATURE_PLACEMENT_TEST.pdf')
        
        print(f"\n🔧 Generating signature test PDF...")
        success = processor.fill_pdf_with_force_visible(homeworks_path, document, output_path)
        
        if success:
            print(f"\n✅ Signature test PDF created: {output_path}")
            print(f"📄 File size: {os.path.getsize(output_path):,} bytes")
            
            print(f"\n🔍 Please check the PDF for:")
            print(f"   • Applicant Signature appears as: '{test_user2_data['applicant_signature']}'")
            print(f"   • Property Owner Signature appears as: '{test_user2_data['owner_signature']}'")
            print(f"   • Both signatures are in the correct locations")
            print(f"   • Signatures are not overlapping or misplaced")
            
            return True
        else:
            print(f"❌ Failed to create signature test PDF")
            return False
    
    except Exception as e:
        print(f"❌ Error creating signature test PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main analysis function"""
    print("🏠 PDF Collaborator - Signature Placement Debug")
    print("Analyzing and fixing signature positioning issues")
    print()
    
    # Step 1: Analyze signature fields
    signature_analysis = analyze_signature_fields()
    
    if not signature_analysis:
        print("❌ Could not analyze signature fields")
        return
    
    signature_fields, date_fields = signature_analysis
    
    # Step 2: Test current positioning logic
    positioning_test = test_signature_positioning()
    
    # Step 3: Create focused test PDF
    pdf_test = create_signature_test_pdf()
    
    print(f"\n📊 SIGNATURE ANALYSIS SUMMARY:")
    print(f"   Signature fields found: {len(signature_fields)}")
    print(f"   Positioning logic test: {'✅ PASS' if positioning_test else '❌ FAIL'}")
    print(f"   Test PDF creation: {'✅ PASS' if pdf_test else '❌ FAIL'}")
    
    if signature_fields:
        print(f"\n💡 SIGNATURE FIELD DETAILS:")
        for field in signature_fields:
            print(f"   📝 {field['name']}: Page {field['page']} at ({field['x']:.1f}, {field['y']:.1f})")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Check SIGNATURE_PLACEMENT_TEST.pdf for current positioning")
        print(f"   2. Verify signatures appear in the correct fields")
        print(f"   3. If incorrect, we'll fix the field mapping logic")
        print(f"   4. Ensure signature styling (font, size) is appropriate")

if __name__ == "__main__":
    main()