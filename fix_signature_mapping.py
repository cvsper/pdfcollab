#!/usr/bin/env python3
"""
Fix signature mapping issue - signatures not appearing in correct location
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def analyze_field_mapping_issue():
    """Analyze why signature fields aren't being filled"""
    
    print("🔍 ANALYZING SIGNATURE FIELD MAPPING ISSUE")
    print("=" * 60)
    
    try:
        from pdf_processor import PDFProcessor
        
        homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        processor = PDFProcessor()
        
        # Extract fields to understand the structure
        field_analysis = processor.extract_fields_with_pymupdf(homeworks_path)
        pdf_fields = field_analysis.get('fields', [])
        
        print(f"📋 Found {len(pdf_fields)} PDF fields")
        
        # Find signature fields specifically
        signature_fields = []
        for field in pdf_fields:
            if 'signature' in field.get('name', '').lower() or field.get('type') == 'signature':
                signature_fields.append(field)
                print(f"📝 Signature field found:")
                print(f"   Name: {field.get('name')}")
                print(f"   Type: {field.get('type')}")
                print(f"   Position: ({field['position']['x']:.1f}, {field['position']['y']:.1f})")
                print(f"   PDF field name: {field.get('pdf_field_name', 'NOT SET')}")
                print()
        
        # Test the mapping structure expected by PDFProcessor
        print(f"🧪 Testing PDFProcessor field mapping structure:")
        
        # Create test document structure with proper pdf_fields
        test_document = {
            'pdf_fields': []
        }
        
        for field in pdf_fields:
            if field.get('name') == 'Applicant Signature':
                # Create proper mapping for applicant signature
                mapped_field = {
                    'name': field['name'],
                    'pdf_field_name': field['name'],  # This is the key!
                    'value': 'Test Applicant Signature',
                    'type': 'signature',
                    'position': field['position'],
                    'assigned_to': 'user2',
                    'page': field.get('page', 0)
                }
                test_document['pdf_fields'].append(mapped_field)
                print(f"✅ Created mapping for Applicant Signature:")
                print(f"   pdf_field_name: {mapped_field['pdf_field_name']}")
                print(f"   value: {mapped_field['value']}")
                
            elif field.get('name') == 'Property Owner Signature':
                # Create proper mapping for property owner signature
                mapped_field = {
                    'name': field['name'],
                    'pdf_field_name': field['name'],  # This is the key!
                    'value': 'Test Property Owner Signature',
                    'type': 'signature',
                    'position': field['position'],
                    'assigned_to': 'user2',
                    'page': field.get('page', 0)
                }
                test_document['pdf_fields'].append(mapped_field)
                print(f"✅ Created mapping for Property Owner Signature:")
                print(f"   pdf_field_name: {mapped_field['pdf_field_name']}")
                print(f"   value: {mapped_field['value']}")
        
        print(f"\\n📊 Test document structure:")
        print(f"   pdf_fields count: {len(test_document['pdf_fields'])}")
        
        return test_document, signature_fields
        
    except Exception as e:
        print(f"❌ Error analyzing field mapping: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def create_corrected_signature_test():
    """Create a signature test with corrected field mapping"""
    
    print(f"\\n🔧 CREATING CORRECTED SIGNATURE TEST")
    print("=" * 60)
    
    test_document, signature_fields = analyze_field_mapping_issue()
    
    if not test_document:
        print("❌ Could not create test document")
        return False
    
    try:
        from pdf_processor import PDFProcessor
        
        homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        processor = PDFProcessor()
        
        # Generate corrected test PDF
        output_path = os.path.join(os.path.dirname(__file__), 'CORRECTED_SIGNATURE_TEST.pdf')
        
        print(f"📄 Input PDF: {homeworks_path}")
        print(f"📄 Output PDF: {output_path}")
        print(f"📋 Fields to fill: {len(test_document['pdf_fields'])}")
        
        # Show what we're trying to fill
        for field in test_document['pdf_fields']:
            print(f"   📝 {field['pdf_field_name']}: '{field['value']}'")
        
        print(f"\\n🔧 Generating corrected signature test...")
        success = processor.fill_pdf_with_force_visible(homeworks_path, test_document, output_path)
        
        if success:
            print(f"\\n✅ CORRECTED signature test PDF created!")
            print(f"📄 File: {output_path}")
            print(f"📄 Size: {os.path.getsize(output_path):,} bytes")
            
            print(f"\\n🔍 Expected results:")
            print(f"   • 'Test Applicant Signature' at position (43, 470)")
            print(f"   • 'Test Property Owner Signature' at position (319, 612)")
            print(f"   • Both signatures should be visible and properly positioned")
            
            return True
        else:
            print(f"❌ Failed to create corrected signature test")
            return False
            
    except Exception as e:
        print(f"❌ Error creating corrected test: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_app_signature_mapping():
    """Identify and suggest fixes for app.py signature mapping"""
    
    print(f"\\n🛠️  SIGNATURE MAPPING FIX FOR APP.PY")
    print("=" * 60)
    
    print(f"🔍 The issue appears to be in the field mapping structure.")
    print(f"\\n❌ Current Problem:")
    print(f"   • PDFProcessor expects 'pdf_field_name' in field mapping")
    print(f"   • Signature fields need proper pdf_field_name to be found")
    print(f"   • app.py may not be setting pdf_field_name correctly")
    
    print(f"\\n✅ Required Fix:")
    print(f"   • Ensure signature fields have pdf_field_name = field name")
    print(f"   • Update field mapping to include proper pdf_field_name")
    print(f"   • Verify signature fields are marked with type='signature'")
    
    # Show the correct mapping structure
    correct_mapping = '''
# In app.py map_form_data_to_pdf_fields function:
for field in pdf_fields:
    if field['name'] == 'Applicant Signature':
        field['value'] = user2_data.get('applicant_signature', '')
        field['type'] = 'signature'
        field['assigned_to'] = 'user2'
        field['pdf_field_name'] = field['name']  # ← This is critical!
        
    elif field['name'] == 'Property Owner Signature':
        field['value'] = user2_data.get('owner_signature', '')
        field['type'] = 'signature'
        field['assigned_to'] = 'user2'
        field['pdf_field_name'] = field['name']  # ← This is critical!
'''
    
    print(f"\\n💡 Correct mapping structure:")
    print(correct_mapping)
    
    return correct_mapping

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Fix Signature Mapping")
    print("Identifying and fixing signature placement issues")
    print()
    
    # Step 1: Analyze the mapping issue
    test_doc, sig_fields = analyze_field_mapping_issue()
    
    # Step 2: Create corrected test
    if test_doc:
        corrected_test = create_corrected_signature_test()
    else:
        corrected_test = False
    
    # Step 3: Provide fix guidance
    fix_guidance = fix_app_signature_mapping()
    
    print(f"\\n📊 SIGNATURE FIX SUMMARY:")
    print(f"   Field analysis: {'✅ PASS' if test_doc else '❌ FAIL'}")
    print(f"   Corrected test: {'✅ PASS' if corrected_test else '❌ FAIL'}")
    print(f"   Fix guidance: {'✅ PROVIDED' if fix_guidance else '❌ MISSING'}")
    
    if corrected_test:
        print(f"\\n🎯 NEXT STEPS:")
        print(f"   1. Check CORRECTED_SIGNATURE_TEST.pdf to verify signatures appear")
        print(f"   2. Apply the pdf_field_name fix to app.py mapping function")
        print(f"   3. Test with real workflow to confirm signatures work")
        print(f"   4. Verify signature styling and positioning are correct")
    else:
        print(f"\\n❌ SIGNATURE MAPPING NEEDS INVESTIGATION")
        print(f"   The field mapping structure may need further debugging")

if __name__ == "__main__":
    main()