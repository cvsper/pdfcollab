#!/usr/bin/env python3
"""
Simple test to verify dwelling checkbox is actually working in the PDF
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid
import fitz  # PyMuPDF

def simple_dwelling_test():
    """Simple test to verify dwelling checkbox works"""
    
    print("🎯 SIMPLE DWELLING CHECKBOX TEST")
    print("=" * 50)
    
    # Create minimal test document
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': [],
        'user1_data': {
            'property_address': '123 Main Street',
            'dwelling_type': 'apartment'
        },
        'user2_data': {}
    }
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Set only the dwelling checkbox and property address
    for field in pdf_fields:
        # Set property address for reference
        if field['name'] == 'Property Address':
            field['value'] = '123 Main Street'
            field['assigned_to'] = 'user1'
            print(f"✅ Set property address: {field['value']}")
        
        # Set apartment checkbox
        elif field['name'] == 'Apartment (Checkbox)':
            field['value'] = 'true'
            field['assigned_to'] = 'user1'
            print(f"✅ Set apartment checkbox: {field['value']}")
            print(f"   PDF field name: {field.get('pdf_field_name')}")
    
    test_document['pdf_fields'] = pdf_fields
    
    # Generate test PDF
    output_file = 'SIMPLE_DWELLING_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ Simple test PDF created: {output_file}")
        
        # Verify the PDF by reading it back
        print("\n🔍 VERIFYING PDF CONTENTS:")
        try:
            doc = fitz.open(output_file)
            
            # Check page 3 where dwelling checkboxes are located
            page = doc[2]  # Page 3 (0-indexed)
            
            # Get all widgets on this page
            widgets = page.widgets()
            print(f"📋 Found {len(widgets)} widgets on page 3")
            
            dwelling_found = False
            for widget in widgets:
                widget_name = widget.field_name
                widget_value = widget.field_value
                widget_type = widget.field_type_string
                
                # Check for dwelling checkbox
                if 'dwelling_apt1' in widget_name or 'Apartment' in str(widget_name):
                    dwelling_found = True
                    print(f"🏠 DWELLING WIDGET FOUND:")
                    print(f"   Name: {widget_name}")
                    print(f"   Value: {widget_value}")
                    print(f"   Type: {widget_type}")
                    print(f"   Checked: {widget_value == True or widget_value == 1}")
                
                # Also show property address for comparison
                elif 'property_address1' in widget_name or 'Property Address' in str(widget_name):
                    print(f"📍 PROPERTY ADDRESS WIDGET:")
                    print(f"   Name: {widget_name}")
                    print(f"   Value: {widget_value}")
                    print(f"   Type: {widget_type}")
            
            if not dwelling_found:
                print("❌ No dwelling checkbox widget found!")
                
                # List all checkbox widgets
                print("\n📝 ALL CHECKBOX WIDGETS:")
                for widget in widgets:
                    if widget.field_type == 2:  # Checkbox type
                        print(f"   {widget.field_name}: {widget.field_value}")
            
            doc.close()
            
        except Exception as e:
            print(f"❌ Error verifying PDF: {e}")
    
    else:
        print(f"❌ Failed to create test PDF")
    
    return success

if __name__ == "__main__":
    simple_dwelling_test()