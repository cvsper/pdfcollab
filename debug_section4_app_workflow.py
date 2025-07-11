#!/usr/bin/env python3
"""
Debug Section 4 fields in the actual app workflow
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def debug_section4_app_workflow():
    """Debug how Section 4 fields are handled in the app workflow"""
    
    print("🐛 DEBUGGING SECTION 4 APP WORKFLOW")
    print("=" * 50)
    
    # First, let's extract the PDF fields like the app does
    processor = PDFProcessor()
    
    pdf_path = 'homworks.pdf'
    if not os.path.exists(pdf_path):
        print(f"❌ {pdf_path} not found")
        return False
    
    # Extract fields like the app does
    result = processor.extract_fields_with_pymupdf(pdf_path)
    if "error" in result:
        print(f"❌ Error extracting fields: {result['error']}")
        return False
    
    pdf_fields = result['fields']
    print(f"📋 Extracted {len(pdf_fields)} PDF fields")
    
    # Look for Section 4 checkbox fields specifically
    section4_checkboxes = []
    for field in pdf_fields:
        field_name = field.get('name', '')
        if ('4' in field_name and 'Checkbox' in field_name) or any(keyword in field_name for keyword in ['Elec Discount', 'Low Income', 'EBT', 'Multifam']):
            section4_checkboxes.append(field)
    
    print(f"\n🔍 Found {len(section4_checkboxes)} Section 4 checkbox fields:")
    for field in section4_checkboxes:
        print(f"   📋 {field['name']} (pdf_field: {field.get('pdf_field_name', 'N/A')})")
    
    # Simulate form data like the app receives
    simulated_form_data = {
        'qualification_option': 'option_a',
        'utility_program': ['electric_discount', 'low_income_discount'],
        'documentation': ['ebt_award'],
    }
    
    print(f"\n📝 Simulating form submission: {simulated_form_data}")
    
    # Apply the same logic as the app
    print(f"\n🔧 Applying app's qualification option mapping...")
    
    # Option A: Utility programs
    utility_programs = simulated_form_data.get('utility_program', [])
    if utility_programs:
        print(f"   📋 Option A - Utility programs selected: {utility_programs}")
        program_mappings = {
            'electric_discount': 'Elec Discount4 (Checkbox)',
            'matching_payment': 'Matching Payment Eversource4 (Checkbox)',  
            'low_income_discount': 'Low Income Program (Checkbox)',
            'bill_forgiveness': 'Bill Forgiveness Program (Checkbox)',
            'matching_payment_united': 'Matching Pay United4 (Checkbox)'
        }
        
        for program in utility_programs:
            target_field = program_mappings.get(program)
            if target_field:
                field_found = False
                for field in pdf_fields:
                    if field['name'] == target_field:
                        field['value'] = 'true'
                        field['assigned_to'] = 'user1'
                        field_found = True
                        print(f"   ✅ Utility program: {program} → {target_field}")
                        break
                if not field_found:
                    print(f"   ❌ Field not found for utility program: {program} → {target_field}")
    
    # Option B: Documentation
    documentation = simulated_form_data.get('documentation', [])
    if documentation:
        print(f"   📋 Option B - Documentation selected: {documentation}")
        doc_mappings = {
            'ebt_award': 'EBT (Food Stamps) (Checkbox)',
            'energy_assistance': 'Energy Award Letter4 (Checkbox)',
            'section_8': 'Section Eight4 (Checkbox)'
        }
        
        for doc in documentation:
            target_field = doc_mappings.get(doc)
            if target_field:
                field_found = False
                for field in pdf_fields:
                    if field['name'] == target_field:
                        field['value'] = 'true'
                        field['assigned_to'] = 'user1'
                        field_found = True
                        print(f"   ✅ Documentation: {doc} → {target_field}")
                        break
                if not field_found:
                    print(f"   ❌ Field not found for documentation: {doc} → {target_field}")
    
    # Now test PDF generation with the mapped fields
    print(f"\n🎯 Testing PDF generation with mapped Section 4 fields...")
    
    # Create document structure like the app does
    test_document = {
        'id': 'section4_app_test',
        'name': 'section4_app_test.pdf',
        'pdf_fields': [field for field in pdf_fields if field.get('value')]
    }
    
    print(f"📊 Document has {len(test_document['pdf_fields'])} fields with values:")
    for field in test_document['pdf_fields']:
        print(f"   ✅ {field['name']}: '{field['value']}'")
    
    # Generate PDF
    output_pdf = 'SECTION4_APP_WORKFLOW_TEST.pdf'
    success = processor.fill_pdf_with_pymupdf(pdf_path, test_document, output_pdf)
    
    if success:
        print(f"\n✅ PDF generated: {output_pdf}")
        
        # Verify the results
        import fitz
        doc = fitz.open(output_pdf)
        page4 = doc[3]  # Page 4
        widgets = list(page4.widgets())
        
        filled_section4_fields = []
        for widget in widgets:
            if widget.field_value and str(widget.field_value) not in ['', 'False', 'Off']:
                if any(field in widget.field_name for field in ['elec_discount4', 'low_income4', 'ebt4']):
                    filled_section4_fields.append(f"{widget.field_name}: {widget.field_value}")
        
        doc.close()
        
        print(f"\n🔍 Verification - Section 4 fields filled in PDF:")
        if filled_section4_fields:
            for field in filled_section4_fields:
                print(f"   ✅ {field}")
            print(f"\n🎉 SUCCESS! {len(filled_section4_fields)} Section 4 fields are working in the app workflow")
            return True
        else:
            print("   ❌ No Section 4 fields found in output PDF")
            return False
    else:
        print("❌ PDF generation failed")
        return False

if __name__ == "__main__":
    success = debug_section4_app_workflow()
    if success:
        print("\n🎯 Section 4 app workflow debugging completed successfully!")
    else:
        print("\n❌ Section 4 app workflow has issues that need fixing")