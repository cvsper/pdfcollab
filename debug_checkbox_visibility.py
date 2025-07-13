#!/usr/bin/env python3
"""
Debug checkbox visibility issues - check if checkboxes are set but not visible
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import fitz  # PyMuPDF
from pdf_processor import PDFProcessor
import uuid

def debug_checkbox_visibility():
    """Debug why checkboxes might not be visually appearing"""
    
    print("🔍 DEBUGGING CHECKBOX VISIBILITY ISSUES")
    print("=" * 60)
    
    # Create a simple test document with only dwelling checkbox
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Set ONLY the apartment checkbox to isolate the issue
    for field in pdf_fields:
        if field['name'] == 'Apartment (Checkbox)':
            field['value'] = 'true'
            field['assigned_to'] = 'user1'
            print(f"✅ Set apartment checkbox: {field['name']} = {field['value']}")
            print(f"   PDF field name: {field.get('pdf_field_name')}")
            print(f"   Field type: {field.get('type')}")
            print(f"   Position: {field.get('position')}")
            break
    
    # Also set property address for reference
    for field in pdf_fields:
        if field['name'] == 'Property Address':
            field['value'] = 'DEBUG TEST - 123 Visibility Street'
            field['assigned_to'] = 'user1'
            break
    
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': pdf_fields,
        'user1_data': {'property_address': 'DEBUG TEST - 123 Visibility Street'},
        'user2_data': {}
    }
    
    # Generate PDF
    output_file = 'CHECKBOX_VISIBILITY_DEBUG.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    if success:
        print(f"\n✅ Debug PDF created: {output_file}")
        
        # Open and analyze the PDF in detail
        doc = fitz.open(output_file)
        page = doc[2]  # Page 3 where checkboxes are
        
        print(f"\n🔍 DETAILED CHECKBOX ANALYSIS:")
        
        # Get all widgets
        widgets = list(page.widgets())
        print(f"📋 Total widgets on page 3: {len(widgets)}")
        
        # Find all checkbox widgets
        checkbox_widgets = []
        for widget in widgets:
            if widget.field_type == 2:  # Checkbox type
                checkbox_widgets.append(widget)
        
        print(f"📋 Total checkbox widgets: {len(checkbox_widgets)}")
        
        # Analyze each checkbox in detail
        for i, widget in enumerate(checkbox_widgets):
            widget_name = widget.field_name
            widget_value = widget.field_value
            widget_rect = widget.rect
            
            print(f"\n📝 Checkbox {i+1}: {widget_name}")
            print(f"   Value: {widget_value}")
            print(f"   Rectangle: {widget_rect}")
            print(f"   Is checked: {widget_value in [True, 1, 'Yes', 'On']}")
            
            # Check if this is our apartment checkbox
            if 'dwelling_apt1' in widget_name or 'apartment' in widget_name.lower():
                print(f"   🎯 THIS IS THE APARTMENT CHECKBOX!")
                
                if widget_value in [True, 1, 'Yes', 'On']:
                    print(f"   ✅ Checkbox is CHECKED")
                    
                    # Check appearance properties
                    try:
                        # Get the widget's appearance
                        appearance = widget.appearance_mode
                        print(f"   Appearance mode: {appearance}")
                        
                        # Check widget flags
                        flags = widget.flags
                        print(f"   Widget flags: {flags}")
                        
                        # Check if widget is hidden
                        is_hidden = (flags & 2) != 0  # Hidden flag
                        is_print = (flags & 4) != 0   # Print flag
                        is_readonly = (flags & 64) != 0  # ReadOnly flag
                        
                        print(f"   Hidden: {is_hidden}")
                        print(f"   Print: {is_print}")
                        print(f"   ReadOnly: {is_readonly}")
                        
                        if is_hidden:
                            print(f"   ⚠️  WARNING: Checkbox is HIDDEN!")
                        if not is_print:
                            print(f"   ⚠️  WARNING: Checkbox won't PRINT!")
                        
                    except Exception as e:
                        print(f"   ⚠️  Could not get appearance info: {e}")
                        
                else:
                    print(f"   ❌ Checkbox is NOT CHECKED")
        
        # Try to force visibility by modifying checkbox appearance
        print(f"\n🔧 ATTEMPTING TO FORCE CHECKBOX VISIBILITY:")
        
        for widget in widgets:
            if 'dwelling_apt1' in widget.field_name:
                try:
                    print(f"   Modifying widget: {widget.field_name}")
                    
                    # Set value explicitly
                    widget.field_value = True
                    
                    # Try to clear hidden flag and set print flag
                    current_flags = widget.flags
                    new_flags = current_flags & ~2  # Clear hidden flag
                    new_flags = new_flags | 4       # Set print flag
                    widget.flags = new_flags
                    
                    # Update the widget
                    widget.update()
                    
                    print(f"   ✅ Updated flags from {current_flags} to {new_flags}")
                    print(f"   ✅ Set field_value to True")
                    
                except Exception as e:
                    print(f"   ❌ Error modifying widget: {e}")
        
        # Save the modified PDF
        modified_output = 'CHECKBOX_VISIBILITY_FIXED.pdf'
        doc.save(modified_output)
        doc.close()
        
        print(f"\n✅ Modified PDF saved: {modified_output}")
        
        # Re-verify the modified PDF
        print(f"\n🔍 VERIFYING MODIFIED PDF:")
        doc2 = fitz.open(modified_output)
        page2 = doc2[2]
        widgets2 = list(page2.widgets())
        
        for widget in widgets2:
            if 'dwelling_apt1' in widget.field_name:
                print(f"   Final state: {widget.field_name} = {widget.field_value}")
                print(f"   Final flags: {widget.flags}")
        
        doc2.close()
        
        return True
    else:
        print(f"❌ Failed to create debug PDF")
        return False

if __name__ == "__main__":
    debug_checkbox_visibility()