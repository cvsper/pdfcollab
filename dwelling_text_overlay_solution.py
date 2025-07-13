#!/usr/bin/env python3
"""
Replace invisible dwelling checkbox with visible text overlay
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import fitz  # PyMuPDF
from pdf_processor import PDFProcessor
import uuid

def dwelling_text_overlay_solution():
    """Replace invisible checkbox with obvious text overlay"""
    
    print("📝 DWELLING TEXT OVERLAY SOLUTION")
    print("=" * 60)
    print("Replacing invisible checkbox with visible text")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Simple test data
    form_data = {
        'property_address': 'TEXT OVERLAY TEST - 999 Visible Street',
        'dwelling_type': 'apartment',
        'first_name': 'VISIBLE',
        'last_name': 'TESTER'
    }
    
    print(f"📝 Testing dwelling_type: {form_data['dwelling_type']}")
    
    # Apply basic mappings
    for field in pdf_fields:
        if field['name'] == 'Property Address':
            field['value'] = form_data['property_address']
            field['assigned_to'] = 'user1'
        elif field['name'] == 'First Name':
            field['value'] = form_data['first_name']
            field['assigned_to'] = 'user1'
        elif field['name'] == 'Last Name':
            field['value'] = form_data['last_name']
            field['assigned_to'] = 'user1'
        # DON'T set the checkbox - we'll add text instead
    
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': pdf_fields,
        'user1_data': form_data,
        'user2_data': {}
    }
    
    # Generate initial PDF (without dwelling checkbox)
    temp_output = 'TEMP_TEXT_OVERLAY.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, temp_output)
    
    if success:
        print(f"✅ Base PDF created: {temp_output}")
        
        # Open PDF and add text overlays for dwelling type
        doc = fitz.open(temp_output)
        page = doc[2]  # Page 3
        
        print(f"\\n📝 ADDING TEXT OVERLAY FOR DWELLING TYPE:")
        
        # Get the dwelling checkboxes positions
        widgets = list(page.widgets())
        dwelling_positions = {}
        
        for widget in widgets:
            if 'dwelling_single_fam1' in widget.field_name:
                dwelling_positions['single_family'] = widget.rect
                print(f"   Found Single Family position: {widget.rect}")
            elif 'dwelling_apt1' in widget.field_name:
                dwelling_positions['apartment'] = widget.rect
                print(f"   Found Apartment position: {widget.rect}")
            elif 'dwelling_condo1' in widget.field_name:
                dwelling_positions['condominium'] = widget.rect
                print(f"   Found Condominium position: {widget.rect}")
        
        # Add text overlay for the selected dwelling type
        selected_dwelling = form_data['dwelling_type']
        if selected_dwelling in dwelling_positions:
            rect = dwelling_positions[selected_dwelling]
            x1, y1, x2, y2 = rect
            
            print(f"   Adding text overlay for '{selected_dwelling}' at {rect}")
            
            # Method 1: Large bold text overlay
            try:
                text_x = x1 - 5
                text_y = y2 + 2
                
                page.insert_text(
                    (text_x, text_y),
                    "☑ SELECTED",
                    fontsize=12,
                    color=(1, 0, 0),  # Red color
                    fontname="helv-bold"
                )
                print(f"   ✅ Added '☑ SELECTED' text")
            except Exception as e:
                print(f"   ❌ Text method 1 failed: {e}")
            
            # Method 2: Draw a big red circle
            try:
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                radius = max(x2 - x1, y2 - y1) * 2
                
                circle_center = fitz.Point(center_x, center_y)
                page.draw_circle(circle_center, radius, color=(1, 0, 0), width=3)
                print(f"   ✅ Added red circle")
            except Exception as e:
                print(f"   ❌ Circle method failed: {e}")
            
            # Method 3: Draw a bright colored rectangle
            try:
                highlight_rect = fitz.Rect(x1 - 10, y1 - 5, x2 + 60, y2 + 5)
                page.draw_rect(highlight_rect, color=(0, 1, 0), fill=(1, 1, 0), width=2)
                print(f"   ✅ Added yellow highlight rectangle")
            except Exception as e:
                print(f"   ❌ Rectangle method failed: {e}")
            
            # Method 4: Add large text next to all dwelling options
            dwelling_labels = {
                'single_family': 'Single Family Home',
                'apartment': 'Apartment', 
                'condominium': 'Condominium'
            }
            
            for dwelling_type, position in dwelling_positions.items():
                try:
                    x1, y1, x2, y2 = position
                    label = dwelling_labels.get(dwelling_type, dwelling_type)
                    
                    if dwelling_type == selected_dwelling:
                        # Selected option - big red text
                        text = f"✓ {label.upper()} ← SELECTED"
                        color = (1, 0, 0)  # Red
                        fontsize = 11
                    else:
                        # Unselected option - gray text
                        text = f"☐ {label}"
                        color = (0.5, 0.5, 0.5)  # Gray
                        fontsize = 9
                    
                    page.insert_text(
                        (x2 + 5, y2),
                        text,
                        fontsize=fontsize,
                        color=color,
                        fontname="helv-bold"
                    )
                    print(f"   ✅ Added label: {text}")
                    
                except Exception as e:
                    print(f"   ❌ Label method failed for {dwelling_type}: {e}")
        
        # Add a big header to make it obvious
        try:
            page.insert_text(
                (50, 240),
                "DWELLING TYPE SELECTION:",
                fontsize=14,
                color=(0, 0, 1),  # Blue
                fontname="helv-bold"
            )
            print(f"   ✅ Added section header")
        except Exception as e:
            print(f"   ❌ Header failed: {e}")
        
        # Save the enhanced PDF
        final_output = 'DWELLING_TEXT_OVERLAY_SOLUTION.pdf'
        doc.save(final_output)
        doc.close()
        
        # Clean up temp file
        if os.path.exists(temp_output):
            os.remove(temp_output)
        
        print(f"\\n✅ TEXT OVERLAY PDF CREATED: {final_output}")
        
        print(f"\\n🎯 WHAT YOU SHOULD SEE:")
        print(f"   1. Open '{final_output}' in your PDF viewer")
        print(f"   2. Go to page 3")
        print(f"   3. Look for 'DWELLING TYPE SELECTION:' header in blue")
        print(f"   4. You should see:")
        print(f"      - ☐ Single Family Home")
        print(f"      - ✓ APARTMENT ← SELECTED (in red)")
        print(f"      - ☐ Condominium")
        print(f"   5. There should be a yellow highlight and red circle around the apartment option")
        
        return True
    else:
        print(f"❌ Failed to create base PDF")
        return False

if __name__ == "__main__":
    success = dwelling_text_overlay_solution()
    if success:
        print("\\n🎉 TEXT OVERLAY SOLUTION COMPLETE!")
        print("📝 This bypasses the invisible checkbox issue with visible text")
    else:
        print("\\n❌ Text overlay solution failed!")