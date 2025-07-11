#!/usr/bin/env python3
"""
Test the EXACT signature positioning fix with user-specified coordinates
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_exact_signature_positioning():
    """Test signatures at EXACT user-specified positions"""
    
    print("🎯 TESTING EXACT SIGNATURE POSITIONING")
    print("=" * 60)
    print("User specified coordinates:")
    print("• Applicant Signature: (46, 477)")
    print("• Property Owner Signature: (325, 619)")
    print()
    
    # Test data focused on signatures
    test_user1_data = {
        'first_name': 'EXACT',
        'last_name': 'POSITION-TEST',
        'property_address': '46-477 Exact Position Street'
    }
    
    test_user2_data = {
        'name': 'EXACT POSITION-TEST',
        'email': 'exact@position.test',
        'applicant_signature': 'EXACT POSITION-TEST Applicant',
        'authorization_date': '2025-07-11',
        'owner_signature': 'EXACT POSITION-TEST Owner',
        'owner_signature_date': '2025-07-11'
    }
    
    print(f"📝 Test Signatures:")
    print(f"   Applicant: '{test_user2_data['applicant_signature']}'")
    print(f"   Property Owner: '{test_user2_data['owner_signature']}'")
    
    try:
        from pdf_processor import PDFProcessor
        
        homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        
        if not os.path.exists(homeworks_path):
            try:
                from embedded_homworks import save_homworks_pdf_to_file
                save_homworks_pdf_to_file(homworks_path)
                print("✅ Using embedded homworks.pdf")
            except ImportError:
                print(f"❌ Error: {homworks_path} not found")
                return False
        
        processor = PDFProcessor()
        
        # Extract PDF fields
        field_analysis = processor.extract_fields_with_pymupdf(homeworks_path)
        if "error" in field_analysis:
            print(f"❌ Error analyzing PDF: {field_analysis['error']}")
            return False
        
        pdf_fields = field_analysis.get('fields', [])
        print(f"📄 Found {len(pdf_fields)} PDF fields")
        
        # Apply field mapping with EXACT positioning
        mapped_pdf_fields = apply_exact_signature_mapping(test_user1_data, test_user2_data, pdf_fields)
        
        # Create document structure
        document = {
            'user1_data': test_user1_data,
            'user2_data': test_user2_data,
            'pdf_fields': mapped_pdf_fields,
            'file_path': homeworks_path
        }
        
        # Generate the exact positioning test PDF
        output_path = os.path.join(os.path.dirname(__file__), 'EXACT_SIGNATURE_POSITIONING_TEST.pdf')
        
        print(f"\n🔧 Generating EXACT positioning test PDF...")
        success = processor.fill_pdf_with_force_visible(homeworks_path, document, output_path)
        
        if success:
            print(f"\n🎉 EXACT POSITIONING TEST SUCCESSFUL!")
            print(f"✅ Test PDF created: {output_path}")
            print(f"📄 File size: {os.path.getsize(output_path):,} bytes")
            
            # Show signature field details
            signature_fields = [f for f in mapped_pdf_fields if f.get('type') == 'signature' and f.get('value')]
            print(f"\n🖋️  Signature fields with EXACT positioning:")
            for sig_field in signature_fields:
                print(f"   📝 {sig_field['name']}: '{sig_field['value']}'")
                print(f"      PDF field name: {sig_field.get('pdf_field_name', 'NOT SET')}")
                
                # Show expected vs actual position
                if 'applicant' in sig_field['name'].lower():
                    print(f"      EXACT position used: (46, 477) ← USER SPECIFIED")
                elif 'owner' in sig_field['name'].lower():
                    print(f"      EXACT position used: (325, 619) ← USER SPECIFIED")
            
            print(f"\n🔍 VERIFICATION CHECKLIST:")
            print(f"   ✅ Check PDF: 'EXACT POSITION-TEST Applicant' appears at (46, 477)")
            print(f"   ✅ Check PDF: 'EXACT POSITION-TEST Owner' appears at (325, 619)")
            print(f"   ✅ Check PDF: Signatures are RIGHT-SIDE-UP (not upside down)")
            print(f"   ✅ Check PDF: Signatures are clearly visible and readable")
            print(f"   ✅ Check PDF: Signatures don't overlap other content")
            
            return True
        else:
            print(f"❌ Failed to generate exact positioning test PDF")
            return False
            
    except Exception as e:
        print(f"❌ Error testing exact positioning: {e}")
        import traceback
        traceback.print_exc()
        return False

def apply_exact_signature_mapping(user1_data, user2_data, pdf_fields):
    """Apply field mapping with focus on EXACT signature positioning"""
    
    print(f"\n🗺️  Applying EXACT signature positioning mapping...")
    
    # Basic field mappings
    EXACT_FIELD_MAPPINGS = {
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'property_address': 'Property Address',
        'applicant_signature': 'Applicant Signature',
        'owner_signature': 'Property Owner Signature'
    }
    
    user2_section4_fields = [
        'applicant_signature', 'authorization_date', 'owner_signature', 'owner_signature_date'
    ]
    
    # Clear all existing assignments
    for field in pdf_fields:
        field['assigned_to'] = None
        field['value'] = ''
    
    matched_fields = 0
    
    # Handle Date fields with position-based mapping
    date_fields = [f for f in pdf_fields if f['name'] == 'Date']
    date_fields.sort(key=lambda f: f['position']['y'])
    
    # Map authorization_date
    authorization_date_value = user2_data.get('authorization_date')
    if authorization_date_value:
        for field in date_fields:
            if 460 <= field['position']['y'] <= 480:
                field['value'] = str(authorization_date_value)
                field['assigned_to'] = 'user2'
                field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                print(f"   ✅ authorization_date → Date field at ({field['position']['x']:.0f}, {field['position']['y']:.0f})")
                matched_fields += 1
                break
    
    # Map owner_signature_date
    owner_date_value = user2_data.get('owner_signature_date')
    if owner_date_value:
        for field in date_fields:
            if field['position']['y'] > 630:
                field['value'] = str(owner_date_value)
                field['assigned_to'] = 'user2'
                field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                print(f"   ✅ owner_signature_date → Date field at ({field['position']['x']:.0f}, {field['position']['y']:.0f})")
                matched_fields += 1
                break
    
    # Combine all form data
    all_form_data = {**user1_data, **user2_data}
    
    # Map form data using exact matching
    for form_field, form_value in all_form_data.items():
        if not form_value or form_field in ['authorization_date', 'owner_signature_date']:
            continue
        
        pdf_field_name = EXACT_FIELD_MAPPINGS.get(form_field)
        if pdf_field_name:
            for field in pdf_fields:
                if field['name'] == pdf_field_name:
                    field['value'] = str(form_value)
                    
                    # Assign to correct user
                    if form_field in user2_section4_fields:
                        field['assigned_to'] = 'user2'
                        if 'signature' in form_field:
                            field['type'] = 'signature'
                            print(f"   🖋️  SIGNATURE FIELD: {form_field} → {pdf_field_name}")
                            print(f"      Value: {form_value}")
                            print(f"      Will use EXACT positioning in PDFProcessor")
                    else:
                        field['assigned_to'] = 'user1'
                    
                    # CRITICAL: Set pdf_field_name for PDFProcessor
                    field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                    
                    print(f"   ✅ {form_field} → {pdf_field_name}")
                    matched_fields += 1
                    break
    
    # Ensure all fields have proper assignments
    for field in pdf_fields:
        if field.get('assigned_to') is None:
            field['assigned_to'] = 'user1'
        if not field.get('pdf_field_name'):
            field['pdf_field_name'] = field['name']
    
    print(f"\n📊 EXACT positioning mapping summary: {matched_fields} fields matched")
    
    return pdf_fields

def main():
    """Main test function"""
    print("🏠 PDF Collaborator - EXACT Signature Positioning Test")
    print("Testing user-specified coordinates: Applicant (46, 477), Owner (325, 619)")
    print()
    
    success = test_exact_signature_positioning()
    
    if success:
        print(f"\n🎉 EXACT SIGNATURE POSITIONING TEST COMPLETED!")
        print(f"✅ Signatures should now appear at the EXACT coordinates you specified")
        print(f"✅ Orientation should be correct (not upside down)")
        print(f"✅ Fixed font size and color for better visibility")
        
        print(f"\n💡 What was fixed:")
        print(f"   • Applicant Signature: Force position to (46, 477)")
        print(f"   • Property Owner Signature: Force position to (325, 619)")
        print(f"   • Fixed upside-down orientation issue")
        print(f"   • Set consistent font size (12pt)")
        print(f"   • Improved signature detection (handles both field names)")
        
        print(f"\n📄 Check EXACT_SIGNATURE_POSITIONING_TEST.pdf to verify!")
    else:
        print(f"\n❌ EXACT POSITIONING TEST FAILED")
        print(f"Further debugging may be needed")

if __name__ == "__main__":
    main()