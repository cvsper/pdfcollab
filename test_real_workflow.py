#!/usr/bin/env python3
"""
Test the REAL workflow that the web application uses
"""

import os
import json
from pdf_processor import PDFProcessor

def test_real_workflow():
    """Test using the exact same workflow as the web application"""
    print("🌐 TESTING REAL WEB APPLICATION WORKFLOW")
    print("=" * 60)
    
    processor = PDFProcessor()
    
    input_pdf = 'uploads/c83e2f43-b4b7-4a4d-9b26-de394bc5008b_homeworks.pdf'
    output_pdf = 'REAL_WORKFLOW_TEST.pdf'
    
    # Create document in the EXACT format the web app uses
    document = {
        "id": "real_workflow_test",
        "name": "Real Workflow Test",
        "pdf_fields": [
            {
                "id": "field_1",
                "name": "Property Address",
                "pdf_field_name": "property_address1",
                "value": "REAL WORKFLOW - 456 Test Avenue",
                "type": "text",
                "assigned_to": "user1",
                "position": {"x": 37, "y": 156, "width": 196, "height": 14},
                "page": 2
            },
            {
                "id": "field_2", 
                "name": "City",
                "pdf_field_name": "city1",
                "value": "REAL TEST CITY",
                "type": "text",
                "assigned_to": "user1",
                "position": {"x": 36, "y": 182, "width": 148, "height": 14},
                "page": 2
            },
            {
                "id": "field_3",
                "name": "Electric Heat",
                "pdf_field_name": "fuel_type_elec2", 
                "value": "yes",
                "type": "radio",
                "assigned_to": "user1",
                "position": {"x": 317, "y": 235, "width": 10, "height": 10},
                "page": 2
            },
            {
                "id": "field_4",
                "name": "Property Owner",
                "pdf_field_name": "owner2",
                "value": "yes", 
                "type": "radio",
                "assigned_to": "user1",
                "position": {"x": 442, "y": 235, "width": 10, "height": 10},
                "page": 2
            },
            {
                "id": "field_5",
                "name": "Gas Heat (should be blank)",
                "pdf_field_name": "fuel_type_gas2",
                "value": "no",
                "type": "radio", 
                "assigned_to": "user1",
                "position": {"x": 345, "y": 235, "width": 10, "height": 10},
                "page": 2
            },
            {
                "id": "field_6",
                "name": "Single Family Home",
                "pdf_field_name": "dwelling_single_fam1",
                "value": "true",
                "type": "checkbox",
                "assigned_to": "user1",
                "position": {"x": 40, "y": 256, "width": 10, "height": 10},
                "page": 2
            },
            {
                "id": "field_7",
                "name": "Apartment",
                "pdf_field_name": "dwelling_apt1", 
                "value": "true",
                "type": "checkbox",
                "assigned_to": "user1",
                "position": {"x": 41, "y": 268, "width": 10, "height": 10},
                "page": 2
            },
            {
                "id": "field_8",
                "name": "Condominium (should be unchecked)",
                "pdf_field_name": "dwelling_condo1",
                "value": "false",
                "type": "checkbox",
                "assigned_to": "user1", 
                "position": {"x": 41, "y": 280, "width": 10, "height": 10},
                "page": 2
            },
            {
                "id": "field_9",
                "name": "Main Signature",
                "pdf_field_name": "signature3",
                "value": "REAL WORKFLOW SIGNATURE - John Doe Jr",
                "type": "signature",
                "assigned_to": "user2",
                "position": {"x": 43, "y": 470, "width": 230, "height": 14},
                "page": 2
            }
        ]
    }
    
    print(f"📄 Input PDF: {input_pdf}")
    print(f"📁 Output PDF: {output_pdf}")
    print(f"📊 Fields to fill: {len(document['pdf_fields'])}")
    
    print("\n🎯 EXPECTED VISIBLE RESULTS:")
    print("   📝 Property Address: 'REAL WORKFLOW - 456 Test Avenue'")
    print("   📝 City: 'REAL TEST CITY'")
    print("   🔘 Electric Heat radio: SELECTED")
    print("   🔘 Property Owner radio: SELECTED") 
    print("   ⚪ Gas Heat radio: BLANK")
    print("   ✅ Single Family Home checkbox: CHECKED")
    print("   ✅ Apartment checkbox: CHECKED")
    print("   ☐ Condominium checkbox: UNCHECKED")
    print("   ✍️  Signature: 'REAL WORKFLOW SIGNATURE - John Doe Jr' in cursive")
    
    print("\n" + "=" * 60)
    print("🔄 PROCESSING WITH REAL WORKFLOW...")
    
    # Use the same method the web app uses
    success = processor.fill_pdf_with_pymupdf(input_pdf, document, output_pdf)
    
    if not success:
        print("❌ FAILED - PDF processing failed")
        return False
    
    if not os.path.exists(output_pdf):
        print("❌ FAILED - Output PDF not created")
        return False
    
    file_size = os.path.getsize(output_pdf)
    print(f"\n✅ PDF CREATED: {output_pdf} ({file_size:,} bytes)")
    
    print("\n" + "=" * 60)
    print("🎉 REAL WORKFLOW TEST COMPLETED!")
    print(f"\n📁 MANUAL VERIFICATION:")
    print(f"   1. Open '{output_pdf}' in a PDF viewer")
    print(f"   2. Check page 3 (the main form page)")
    print(f"   3. Verify all fields are filled as expected")
    
    print(f"\n🔍 If fields are NOT visible:")
    print(f"   - Try different PDF viewers (Adobe Reader, Preview, etc.)")
    print(f"   - The issue might be viewer-specific")
    print(f"   - Some viewers don't show form field changes immediately")
    
    return True

if __name__ == "__main__":
    test_real_workflow()