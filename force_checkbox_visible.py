#!/usr/bin/env python3
"""
Force checkbox to be visually visible by drawing a checkmark
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import fitz  # PyMuPDF
from pdf_processor import PDFProcessor
import uuid

def force_checkbox_visible():
    """Force checkbox to be visually visible by adding visual checkmark"""
    
    print("🎯 FORCING CHECKBOX VISUAL VISIBILITY")
    print("=" * 60)
    
    # Create a test with dwelling checkbox
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Set apartment checkbox
    for field in pdf_fields:
        if field['name'] == 'Apartment (Checkbox)':
            field['value'] = 'true'
            field['assigned_to'] = 'user1'
            print(f"✅ Set: {field['name']} = {field['value']}")
            break
    
    # Set property address for reference
    for field in pdf_fields:
        if field['name'] == 'Property Address':
            field['value'] = 'VISUAL TEST - 456 Checkmark Street'
            field['assigned_to'] = 'user1'
            break
    
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': pdf_fields,
        'user1_data': {'property_address': 'VISUAL TEST - 456 Checkmark Street'},
        'user2_data': {}
    }
    
    # Generate initial PDF
    temp_output = 'TEMP_CHECKBOX_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, temp_output)
    
    if success:
        print(f"✅ Temporary PDF created: {temp_output}")
        
        # Open the PDF and manually draw checkmarks
        doc = fitz.open(temp_output)
        page = doc[2]  # Page 3
        
        print(f"🎨 DRAWING VISUAL CHECKMARKS:")
        
        # Find checkbox widgets and draw visual checkmarks
        widgets = list(page.widgets())
        
        for widget in widgets:
            if widget.field_type == 2 and widget.field_value in [True, 1, 'Yes', 'On']:
                widget_name = widget.field_name
                widget_rect = widget.rect
                
                print(f"   Drawing checkmark for: {widget_name}")
                print(f"   Position: {widget_rect}")
                
                # Calculate checkmark position
                x1, y1, x2, y2 = widget_rect
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                # Draw a visual checkmark
                # Method 1: Draw text checkmark
                try:
                    page.insert_text(
                        (center_x - 2, center_y + 1),
                        "✓",
                        fontsize=8,
                        color=(0, 0, 0),
                        fontname="helv"
                    )
                    print(f"   ✅ Drew text checkmark at ({center_x:.1f}, {center_y:.1f})")
                except Exception as e:
                    print(f"   ❌ Failed to draw text checkmark: {e}")
                
                # Method 2: Draw lines to form checkmark
                try:
                    # Calculate checkmark lines
                    check_size = min(x2 - x1, y2 - y1) * 0.6
                    left_x = center_x - check_size/2
                    right_x = center_x + check_size/2
                    top_y = center_y - check_size/4
                    bottom_y = center_y + check_size/4
                    
                    # Draw checkmark lines
                    line1_start = fitz.Point(left_x, center_y)
                    line1_end = fitz.Point(center_x - 1, bottom_y)
                    line2_start = fitz.Point(center_x - 1, bottom_y)
                    line2_end = fitz.Point(right_x, top_y)
                    
                    # Draw the lines
                    shape = page.new_shape()
                    shape.draw_line(line1_start, line1_end)
                    shape.draw_line(line2_start, line2_end)
                    shape.finish(color=(0, 0, 0), width=1.5)
                    shape.commit()
                    
                    print(f"   ✅ Drew line checkmark")
                    
                except Exception as e:
                    print(f"   ❌ Failed to draw line checkmark: {e}")
                
                # Method 3: Fill the entire checkbox area
                try:
                    # Draw a filled rectangle to make it obvious
                    fill_rect = fitz.Rect(x1 + 1, y1 + 1, x2 - 1, y2 - 1)
                    page.draw_rect(fill_rect, color=(0, 0, 0), fill=(0.8, 0.8, 0.8))
                    print(f"   ✅ Drew filled rectangle")
                except Exception as e:
                    print(f"   ❌ Failed to draw filled rectangle: {e}")
        
        # Save the visually enhanced PDF
        final_output = 'VISUALLY_ENHANCED_CHECKBOX.pdf'
        doc.save(final_output)
        doc.close()
        
        print(f"\n✅ Visually enhanced PDF saved: {final_output}")
        
        # Clean up temp file
        if os.path.exists(temp_output):
            os.remove(temp_output)
        
        # Verify the final result
        print(f"\n🔍 VERIFYING FINAL RESULT:")
        doc2 = fitz.open(final_output)
        page2 = doc2[2]
        widgets2 = list(page2.widgets())
        
        for widget in widgets2:
            if 'dwelling_apt1' in widget.field_name:
                print(f"   Final checkbox state: {widget.field_name} = {widget.field_value}")
                if widget.field_value in [True, 1, 'Yes', 'On']:
                    print(f"   ✅ Checkbox is checked AND should now be visually obvious!")
                else:
                    print(f"   ❌ Checkbox is not checked")
        
        doc2.close()
        
        print(f"\n🎯 RECOMMENDATION:")
        print(f"   1. Open '{final_output}' in your PDF viewer")
        print(f"   2. Look at page 3 around coordinates (41, 268)")
        print(f"   3. You should see multiple visual indicators for the apartment checkbox")
        print(f"   4. If you still don't see it, the issue might be with the PDF form structure")
        
        return True
    else:
        print(f"❌ Failed to create temporary PDF")
        return False

if __name__ == "__main__":
    force_checkbox_visible()