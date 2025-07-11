#!/usr/bin/env python3
"""
Test the complete user workflow that a real user would experience
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def test_real_user_workflow():
    """Test the complete workflow that simulates a real user submission"""
    
    print("🧪 TESTING REAL USER WORKFLOW")
    print("=" * 50)
    
    # Step 1: Extract PDF fields like the app does
    processor = PDFProcessor()
    
    pdf_path = 'homworks.pdf'
    if not os.path.exists(pdf_path):
        print(f"❌ {pdf_path} not found")
        return False
    
    print("📄 Step 1: Extracting PDF fields (like app.py does)...")
    result = processor.extract_fields_with_pymupdf(pdf_path)
    if "error" in result:
        print(f"❌ Error extracting fields: {result['error']}")
        return False
    
    pdf_fields = result['fields']
    print(f"✅ Extracted {len(pdf_fields)} PDF fields")
    
    # Step 2: Simulate User 1 form submission with Section 4 data
    print("\n👤 Step 2: Simulating User 1 form submission...")
    
    user1_form_data = {
        # Basic info
        'property_address': '123 Main Street',
        'first_name': 'John',
        'last_name': 'Smith',
        'telephone': '555-1234',
        'email': 'john@example.com',
        
        # Section 3: Qualification - THIS IS THE KEY PART
        'qualification_option': 'option_a',  # User selects Option A
        'utility_program': ['electric_discount', 'low_income_discount', 'bill_forgiveness'],  # Multiple selections
        'household_size': '4',
        'annual_income': '45000',
        
        # User 2 info
        'user2_name': 'Jane Smith',
        'user2_email': 'jane@example.com'
    }
    
    print(f"📝 User 1 selected qualification option: {user1_form_data['qualification_option']}")
    print(f"📝 User 1 selected utility programs: {user1_form_data['utility_program']}")
    
    # Step 3: Apply the exact same field mapping logic as app.py
    print("\n🔧 Step 3: Applying field mapping logic (like app.py)...")
    
    # First, handle basic field mappings
    EXACT_FIELD_MAPPINGS = {
        'property_address': 'property_address1',
        'first_name': 'first_name2',
        'last_name': 'last_name2',
        'telephone': 'phone2',
        'email': 'email2',
        'household_size': 'people_in_household4',
        'annual_income': 'annual_income4'
    }
    
    mapped_fields = 0
    for form_field, pdf_field_name in EXACT_FIELD_MAPPINGS.items():
        if form_field in user1_form_data and user1_form_data[form_field]:
            # Find the PDF field and set its value
            for field in pdf_fields:
                if field.get('pdf_field_name') == pdf_field_name or field.get('name') == pdf_field_name:
                    field['value'] = user1_form_data[form_field]
                    field['assigned_to'] = 'user1'
                    mapped_fields += 1
                    print(f"   ✅ Mapped {form_field} → {pdf_field_name}: '{user1_form_data[form_field]}'")
                    break
    
    # Step 4: Handle qualification checkboxes (the critical part)
    print(f"\n🎯 Step 4: Handling qualification checkboxes...")
    
    # Option A: Utility programs
    utility_programs = user1_form_data.get('utility_program', [])
    if utility_programs:
        print(f"   📋 Processing Option A - Utility programs: {utility_programs}")
        program_mappings = {
            'electric_discount': 'Elec Discount4 (Checkbox)',
            'matching_payment': 'Matching Payment Eversource4 (Checkbox)',  
            'low_income_discount': 'Low Income Program (Checkbox)',
            'bill_forgiveness': 'Bill Forgiveness Program (Checkbox)',
            'matching_payment_united': 'Matching Pay United4 (Checkbox)'
        }
        
        for program in utility_programs:
            target_field_name = program_mappings.get(program)
            if target_field_name:
                field_found = False
                for field in pdf_fields:
                    if field['name'] == target_field_name:
                        field['value'] = 'true'
                        field['assigned_to'] = 'user1'
                        field_found = True
                        mapped_fields += 1
                        print(f"   ✅ Qualification: {program} → {target_field_name}")
                        break
                if not field_found:
                    print(f"   ❌ Field NOT FOUND: {program} → {target_field_name}")
    
    print(f"\n📊 Total fields mapped: {mapped_fields}")
    
    # Step 5: Create document structure for PDF generation
    print(f"\n📄 Step 5: Creating document for PDF generation...")
    
    fields_with_values = [field for field in pdf_fields if field.get('value')]
    print(f"📋 Fields with values: {len(fields_with_values)}")
    
    for field in fields_with_values:
        print(f"   📝 {field['name']}: '{field['value']}' → {field.get('assigned_to', 'unassigned')}")
    
    # Step 6: Add User 2 signatures and dates (simulate User 2 completion)
    print(f"\n👥 Step 6: Simulating User 2 completion...")
    
    # Find signature and date fields
    for field in pdf_fields:
        if field['name'] == 'Applicant Signature':
            field['value'] = 'John Smith'
            field['assigned_to'] = 'user2'
            print(f"   ✅ Added Applicant Signature: 'John Smith'")
        elif field['name'] == 'Property Owner Signature':
            field['value'] = 'Jane Smith'
            field['assigned_to'] = 'user2'
            print(f"   ✅ Added Property Owner Signature: 'Jane Smith'")
        elif field['name'] == 'Date' and field.get('position', {}).get('y', 0) > 460:
            field['value'] = '2025-07-11'
            field['assigned_to'] = 'user2'
            print(f"   ✅ Added Date: '2025-07-11' at y={field.get('position', {}).get('y', 0)}")
    
    # Step 7: Generate the final PDF
    print(f"\n🎯 Step 7: Generating final PDF...")
    
    test_document = {
        'id': 'real_user_test',
        'name': 'real_user_test.pdf',
        'pdf_fields': [field for field in pdf_fields if field.get('value')]
    }
    
    print(f"📊 Document contains {len(test_document['pdf_fields'])} filled fields")
    
    output_pdf = 'REAL_USER_WORKFLOW_TEST.pdf'
    success = processor.fill_pdf_with_pymupdf(pdf_path, test_document, output_pdf)
    
    if success:
        print(f"\n✅ PDF generated successfully: {output_pdf}")
        
        # Step 8: Verify Section 4 fields in the output
        print(f"\n🔍 Step 8: Verifying Section 4 fields in output PDF...")
        
        import fitz
        doc = fitz.open(output_pdf)
        page4 = doc[3]  # Page 4
        widgets = list(page4.widgets())
        
        section4_results = []
        expected_section4_fields = ['elec_discount4', 'low_income4', 'bill_forgive4', 'people_in_household4', 'annual_income4']
        
        for widget in widgets:
            if widget.field_name in expected_section4_fields and widget.field_value and str(widget.field_value) not in ['', 'False', 'Off']:
                section4_results.append(f"{widget.field_name}: {widget.field_value}")
        
        doc.close()
        
        print(f"📊 Section 4 verification results:")
        if section4_results:
            print(f"   ✅ Found {len(section4_results)} Section 4 fields in PDF:")
            for result in section4_results:
                print(f"      ✅ {result}")
            
            if len(section4_results) >= 4:  # We expect at least 4 fields (3 checkboxes + household + income)
                print(f"\n🎉 SUCCESS! Section 4 fields are working in the real user workflow!")
                return True
            else:
                print(f"\n⚠️  Only {len(section4_results)} Section 4 fields found (expected at least 4)")
                return False
        else:
            print(f"   ❌ No Section 4 fields found in output PDF")
            
            # Debug: Show what fields ARE filled
            doc = fitz.open(output_pdf)
            page4 = doc[3]
            widgets = list(page4.widgets())
            filled_fields = [w for w in widgets if w.field_value and str(w.field_value) not in ['', 'False', 'Off']]
            print(f"\n🐛 DEBUG: All filled fields on page 4:")
            for w in filled_fields:
                print(f"      {w.field_name}: {w.field_value}")
            doc.close()
            return False
    else:
        print(f"❌ PDF generation failed")
        return False

if __name__ == "__main__":
    success = test_real_user_workflow()
    if success:
        print("\n🎯 Real user workflow test PASSED! Section 4 is working.")
    else:
        print("\n❌ Real user workflow test FAILED. Section 4 needs investigation.")