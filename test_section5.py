#!/usr/bin/env python3
"""
Test script to demonstrate Section 5 functionality
This script creates a test document with Section 5 fields filled out
and generates a downloadable PDF to verify the implementation.
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
import app
from pdf_processor import PDFProcessor

def create_test_document_with_section5():
    """Create a test document with Section 5 fields filled out"""
    
    print("🧪 Creating test document with Section 5 fields...")
    
    # Create a test document structure (similar to what would be in the database)
    test_document = {
        'id': 'test_section5_001',
        'name': 'Test_Section5_Demo.pdf',
        'file_path': os.path.join(os.getcwd(), 'homworks.pdf'),
        'status': 'completed',
        'created_at': datetime.now().isoformat(),
        'completed_at': datetime.now().isoformat(),
        'user1_data': {
            'name': 'John Test User',
            'email': 'john@test.com'
        },
        'user2_data': {
            'name': 'Jane Affidavit User', 
            'email': 'jane@test.com'
        },
        'pdf_fields': []
    }
    
    # Add some sample fields from other sections (User 1 fields)
    user1_fields = [
        {
            'id': 'field_001',
            'name': 'First Name',
            'pdf_field_name': 'first_name',
            'type': 'text',
            'value': 'John',
            'assigned_to': 'user1',
            'page': 0,
            'position': {'x': 100, 'y': 500, 'width': 150, 'height': 25},
            'source': 'extracted'
        },
        {
            'id': 'field_002', 
            'name': 'Last Name',
            'pdf_field_name': 'last_name',
            'type': 'text',
            'value': 'Doe',
            'assigned_to': 'user1',
            'page': 0,
            'position': {'x': 260, 'y': 500, 'width': 150, 'height': 25},
            'source': 'extracted'
        },
        {
            'id': 'field_003',
            'name': 'Phone Number',
            'pdf_field_name': 'phone_number',
            'type': 'tel',
            'value': '555-123-4567',
            'assigned_to': 'user1',
            'page': 0,
            'position': {'x': 100, 'y': 470, 'width': 150, 'height': 25},
            'source': 'extracted'
        }
    ]
    
    # Add Section 5 fields (User 2 fields) - these are the manual affidavit fields
    section5_fields = [
        {
            'id': 'affidavit_field_0',
            'name': 'Account Holder Name (Affidavit)',
            'pdf_field_name': 'account_holder_name_affidavit',
            'type': 'text',
            'value': 'Jane Doe (Account Holder)',
            'assigned_to': 'user2',
            'page': 4,  # Page 5 (0-indexed)
            'position': {'x': 145, 'y': 135, 'width': 250, 'height': 25},  # Final position: right and adjusted down 5 points
            'source': 'manual_affidavit'
        },
        {
            'id': 'affidavit_field_1',
            'name': 'Household Member Names (No Income)',
            'pdf_field_name': 'household_member_names_no_income',
            'type': 'textarea',
            'value': 'Robert Doe (Son, Age 19, Student)\nMary Doe (Daughter, Age 20, Unemployed)',
            'assigned_to': 'user2',
            'page': 4,  # Page 5 (0-indexed)
            'position': {'x': 35, 'y': 255, 'width': 450, 'height': 80},
            'source': 'manual_affidavit'
        },
        {
            'id': 'affidavit_field_2',
            'name': 'Affidavit Signature',
            'pdf_field_name': 'affidavit_signature',
            'type': 'signature',
            'value': 'typed:Jane M. Doe',
            'assigned_to': 'user2',
            'page': 4,  # Page 5 (0-indexed)
            'position': {'x': 40, 'y': 470, 'width': 200, 'height': 30},
            'source': 'manual_affidavit'
        },
        {
            'id': 'affidavit_field_3',
            'name': 'Printed Name (Affidavit)',
            'pdf_field_name': 'printed_name_affidavit',
            'type': 'text',
            'value': 'JANE MARIE DOE',
            'assigned_to': 'user2',
            'page': 4,  # Page 5 (0-indexed)
            'position': {'x': 305, 'y': 480, 'width': 230, 'height': 25},
            'source': 'manual_affidavit'
        },
        {
            'id': 'affidavit_field_4',
            'name': 'Date (Affidavit)',
            'pdf_field_name': 'date_affidavit',
            'type': 'date',
            'value': '2025-07-10',
            'assigned_to': 'user2',
            'page': 4,  # Page 5 (0-indexed)
            'position': {'x': 40, 'y': 525, 'width': 150, 'height': 25},
            'source': 'manual_affidavit'
        },
        {
            'id': 'affidavit_field_5',
            'name': 'Telephone (Affidavit)',
            'pdf_field_name': 'telephone_affidavit',
            'type': 'tel',
            'value': '555-987-6543',
            'assigned_to': 'user2',
            'page': 4,  # Page 5 (0-indexed)
            'position': {'x': 305, 'y': 525, 'width': 150, 'height': 25},
            'source': 'manual_affidavit'
        }
    ]
    
    # Combine all fields
    test_document['pdf_fields'] = user1_fields + section5_fields
    
    print(f"✅ Created test document with {len(test_document['pdf_fields'])} fields:")
    print(f"   - User 1 fields: {len(user1_fields)}")
    print(f"   - Section 5 fields: {len(section5_fields)}")
    
    # Show field details
    print("\n📋 Field Details:")
    for field in test_document['pdf_fields']:
        assignment_icon = "👤" if field['assigned_to'] == 'user1' else "👥"
        print(f"   {assignment_icon} {field['name']}: '{field['value']}' → {field['assigned_to']}")
    
    return test_document

def generate_test_pdf(test_document):
    """Generate a completed PDF using the test document data"""
    
    print(f"\n🎯 Generating completed PDF...")
    
    try:
        # Use the app's PDF generation function
        output_path = app.generate_completed_pdf(test_document)
        
        if output_path and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Successfully generated test PDF: {output_path}")
            print(f"📄 File size: {file_size:,} bytes")
            return output_path
        else:
            print(f"❌ Failed to generate PDF or file not found")
            return None
            
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def verify_section5_fields(pdf_path):
    """Verify that Section 5 fields are present in the generated PDF"""
    
    print(f"\n🔍 Verifying Section 5 fields in PDF...")
    
    try:
        import fitz
        doc = fitz.open(pdf_path)
        
        section5_field_names = [
            'account_holder_name_affidavit',
            'household_member_names_no_income', 
            'affidavit_signature',
            'printed_name_affidavit',
            'date_affidavit',
            'telephone_affidavit'
        ]
        
        found_fields = []
        total_widgets = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            total_widgets += len(widgets)
            
            for widget in widgets:
                field_name = widget.field_name
                if field_name and any(s5_field in field_name.lower() for s5_field in section5_field_names):
                    found_fields.append({
                        'name': field_name,
                        'value': widget.field_value,
                        'page': page_num,
                        'type': widget.field_type_string
                    })
        
        doc.close()
        
        print(f"📊 PDF Analysis Results:")
        print(f"   - Total widgets found: {total_widgets}")
        print(f"   - Section 5 fields found: {len(found_fields)}")
        
        if found_fields:
            print(f"\n✅ Section 5 Fields in PDF:")
            for field in found_fields:
                print(f"   - {field['name']}: '{field['value']}' (Page {field['page']}, Type: {field['type']})")
        else:
            print(f"\n❌ No Section 5 fields found in PDF!")
            
        return len(found_fields) > 0
        
    except Exception as e:
        print(f"❌ Error verifying PDF: {e}")
        return False

def main():
    """Main test function"""
    
    print("="*60)
    print("🧪 SECTION 5 FUNCTIONALITY TEST")
    print("="*60)
    
    # Check if the original PDF exists
    original_pdf = os.path.join(os.getcwd(), 'homworks.pdf')
    if not os.path.exists(original_pdf):
        print(f"❌ Original PDF not found: {original_pdf}")
        print("Please make sure 'homworks.pdf' exists in the current directory")
        return
    
    print(f"✅ Original PDF found: {original_pdf}")
    
    # Step 1: Create enhanced PDF with Section 5 widgets
    print(f"\n" + "="*40)
    print("STEP 1: Creating Enhanced PDF")
    print("="*40)
    
    enhanced_pdf_path = original_pdf.replace('.pdf', '_enhanced.pdf')
    success = app.create_enhanced_pdf_with_section5(original_pdf, enhanced_pdf_path)
    
    if success and os.path.exists(enhanced_pdf_path):
        print(f"✅ Enhanced PDF created: {enhanced_pdf_path}")
    else:
        print(f"❌ Failed to create enhanced PDF")
        return
    
    # Step 2: Create test document with filled Section 5 data
    print(f"\n" + "="*40)
    print("STEP 2: Creating Test Document")
    print("="*40)
    
    test_document = create_test_document_with_section5()
    test_document['file_path'] = enhanced_pdf_path  # Use enhanced PDF
    
    # Step 3: Generate completed PDF
    print(f"\n" + "="*40)
    print("STEP 3: Generating Completed PDF")
    print("="*40)
    
    output_pdf = generate_test_pdf(test_document)
    
    if not output_pdf:
        print("❌ Test failed - could not generate PDF")
        return
    
    # Step 4: Verify Section 5 fields are present
    print(f"\n" + "="*40)
    print("STEP 4: Verifying Section 5 Fields")
    print("="*40)
    
    verification_success = verify_section5_fields(output_pdf)
    
    # Final results
    print(f"\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    if verification_success:
        print("✅ SUCCESS: Section 5 fields are working correctly!")
        print(f"📄 Test PDF generated: {output_pdf}")
        print(f"🔍 You can now download and examine this PDF to see Section 5 fields")
    else:
        print("❌ FAILURE: Section 5 fields are not appearing correctly")
    
    print(f"\n📁 Files created:")
    print(f"   - Enhanced PDF: {enhanced_pdf_path}")
    print(f"   - Test Output PDF: {output_pdf}")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Download the test PDF: {output_pdf}")
    print(f"   2. Open it and look for Section 5 fields with filled data")
    print(f"   3. Verify all 6 Section 5 fields are visible and properly filled")

if __name__ == "__main__":
    main()