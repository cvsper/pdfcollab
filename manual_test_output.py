#!/usr/bin/env python3
"""
Create a test PDF output that stays on disk for manual verification
"""

import os
from pdf_processor import PDFProcessor

def create_test_output():
    """Create a test PDF that we can manually examine"""
    print("🧪 Creating test PDF for manual verification...")
    
    processor = PDFProcessor()
    
    # Use the real PDF with form fields
    input_pdf = 'uploads/c83e2f43-b4b7-4a4d-9b26-de394bc5008b_homeworks.pdf'
    output_pdf = 'test_output_manual_verification.pdf'
    
    # Comprehensive test data
    test_document = {
        'id': 'manual_test_123',
        'name': 'manual_test.pdf',
        'pdf_fields': [
            # Text fields
            {
                'id': 'field_1',
                'name': 'Property Address',
                'pdf_field_name': 'property_address1',
                'value': '🏠 123 Test Street, Apt 456',
                'type': 'text',
                'assigned_to': 'user1',
                'position': {'x': 37, 'y': 156, 'width': 196, 'height': 14},
                'page': 2
            },
            {
                'id': 'field_2',
                'name': 'City',
                'pdf_field_name': 'city1',
                'value': 'Test City',
                'type': 'text',
                'assigned_to': 'user1',
                'position': {'x': 36, 'y': 182, 'width': 148, 'height': 14},
                'page': 2
            },
            {
                'id': 'field_3',
                'name': 'State',
                'pdf_field_name': 'state1',
                'value': 'TS',
                'type': 'text',
                'assigned_to': 'user1',
                'position': {'x': 184, 'y': 182, 'width': 49, 'height': 14},
                'page': 2
            },
            {
                'id': 'field_4',
                'name': 'ZIP Code',
                'pdf_field_name': 'zip1',
                'value': '12345',
                'type': 'text',
                'assigned_to': 'user1',
                'position': {'x': 233, 'y': 182, 'width': 80, 'height': 14},
                'page': 2
            },
            
            # Radio buttons (set some to yes)
            {
                'id': 'field_5',
                'name': 'Electric Heat',
                'pdf_field_name': 'fuel_type_elec2',
                'value': 'yes',
                'type': 'radio',
                'assigned_to': 'user1',
                'position': {'x': 317, 'y': 235, 'width': 10, 'height': 10},
                'page': 2
            },
            {
                'id': 'field_6',
                'name': 'Property Owner',
                'pdf_field_name': 'owner2',
                'value': 'yes',
                'type': 'radio',
                'assigned_to': 'user1',
                'position': {'x': 442, 'y': 235, 'width': 10, 'height': 10},
                'page': 2
            },
            
            # Checkboxes
            {
                'id': 'field_7',
                'name': 'Single Family Home',
                'pdf_field_name': 'dwelling_single_fam1',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 40, 'y': 256, 'width': 10, 'height': 10},
                'page': 2
            },
            {
                'id': 'field_8',
                'name': 'Low Income Program',
                'pdf_field_name': 'low_income4',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1',
                'position': {'x': 156, 'y': 220, 'width': 10, 'height': 10},
                'page': 3
            },
            
            # Signature
            {
                'id': 'field_9',
                'name': 'Signature',
                'pdf_field_name': 'signature3',
                'value': '✍️ Manual Test Signature - John Doe',
                'type': 'signature',
                'assigned_to': 'user2',
                'position': {'x': 43, 'y': 470, 'width': 230, 'height': 14},
                'page': 2
            },
            
            # Date
            {
                'id': 'field_10',
                'name': 'Date',
                'pdf_field_name': 'date3',
                'value': '2025-06-18',
                'type': 'date',
                'assigned_to': 'user1',
                'position': {'x': 441, 'y': 471, 'width': 126, 'height': 14},
                'page': 2
            }
        ]
    }
    
    print(f"📄 Input PDF: {input_pdf}")
    print(f"📁 Output PDF: {output_pdf}")
    print(f"📊 Test fields: {len(test_document['pdf_fields'])}")
    
    # Fill the PDF
    success = processor.fill_pdf_with_pymupdf(input_pdf, test_document, output_pdf)
    
    if success and os.path.exists(output_pdf):
        file_size = os.path.getsize(output_pdf)
        print(f"\n✅ SUCCESS! Test PDF created: {output_pdf}")
        print(f"📏 File size: {file_size:,} bytes")
        print(f"🔍 Open '{output_pdf}' to manually verify:")
        print("   - Property Address should show: '🏠 123 Test Street, Apt 456'")
        print("   - City should show: 'Test City'")
        print("   - State should show: 'TS'")
        print("   - ZIP should show: '12345'")
        print("   - Electric Heat radio button should be selected")
        print("   - Property Owner radio button should be selected")
        print("   - Single Family Home checkbox should be checked")
        print("   - Low Income Program checkbox should be checked")
        print("   - Signature should show: '✍️ Manual Test Signature - John Doe' in cursive")
        print("   - Date should show: '2025-06-18'")
        
        return True
    else:
        print("❌ Failed to create test PDF")
        return False

if __name__ == "__main__":
    create_test_output()