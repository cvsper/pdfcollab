#!/usr/bin/env python3
"""
Force PDF fields to be visible by flattening form and adding text overlays
"""

import fitz
import os
from pdf_processor import PDFProcessor

def force_visible_fill_pdf(input_pdf, test_data, output_pdf):
    """Fill PDF and ensure content is visually present by flattening and overlaying text"""
    print("🎯 FORCE VISIBLE PDF FILLING")
    print("=" * 50)
    
    try:
        # Step 1: Open PDF
        doc = fitz.open(input_pdf)
        print(f"📄 Opened PDF: {input_pdf}")
        
        # Step 2: Fill form fields normally first
        processor = PDFProcessor()
        processor.fill_pdf_with_pymupdf(input_pdf, test_data, "temp_filled.pdf")
        
        # Step 3: Reopen the filled PDF
        doc.close()
        doc = fitz.open("temp_filled.pdf")
        
        # Step 4: Force visual content by adding text overlays
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            print(f"\n📄 Processing page {page_num + 1}")
            
            for widget in widgets:
                field_name = widget.field_name
                field_value = widget.field_value
                widget_type = processor.get_widget_type(widget)
                rect = widget.rect
                
                if field_value and str(field_value) not in ['', 'False', 'Off']:
                    # Force visible text overlay for all filled fields
                    if widget_type == 'text':
                        # Add black text overlay
                        page.insert_text(
                            (rect.x0 + 2, rect.y0 + rect.height - 2),
                            str(field_value),
                            fontsize=min(rect.height - 2, 12),
                            color=(0, 0, 0)  # Black
                        )
                        print(f"   📝 Added text overlay: '{field_value}' for {field_name}")
                        
                    elif widget_type == 'checkbox':
                        # Add large checkmark
                        page.insert_text(
                            (rect.x0 + 1, rect.y0 + rect.height * 0.8),
                            "✓",
                            fontsize=min(rect.height, 14),
                            color=(0, 0.7, 0)  # Green
                        )
                        print(f"   ✅ Added checkmark for {field_name}")
                        
                    elif widget_type == 'radio':
                        # Add filled circle
                        page.insert_text(
                            (rect.x0 + 1, rect.y0 + rect.height * 0.8),
                            "●",
                            fontsize=min(rect.height, 12),
                            color=(0, 0, 0.7)  # Blue
                        )
                        print(f"   🔘 Added radio dot for {field_name}")
        
        # Step 5: Handle signature fields with special overlay
        if 'pdf_fields' in test_data:
            for field in test_data['pdf_fields']:
                if field.get('type') == 'signature' and field.get('value'):
                    page_num = field.get('page', 0)
                    if page_num < len(doc):
                        page = doc[page_num]
                        pos = field.get('position', {})
                        
                        # Use position or find signature widget
                        x = pos.get('x', 50)
                        y = pos.get('y', 500)
                        
                        # Add signature text
                        signature_text = field['value'].replace('typed:', '').strip()
                        page.insert_text(
                            (x, y),
                            signature_text,
                            fontsize=14,
                            color=(0, 0, 0.8)  # Dark blue
                        )
                        print(f"   ✍️  Added signature overlay: '{signature_text}'")
        
        # Step 6: Flatten the PDF (make form fields non-editable)
        print("\n🔧 Flattening PDF to make content permanent...")
        
        # Create new document to flatten
        new_doc = fitz.open()
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Convert page to image and back to ensure flattening
            mat = fitz.Matrix(2, 2)  # 2x scale for quality
            pix = page.get_pixmap(matrix=mat)
            
            # Create new page from image
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(new_page.rect, pixmap=pix)
        
        doc.close()
        
        # Step 7: Save final PDF
        new_doc.save(output_pdf)
        new_doc.close()
        
        # Clean up temp file
        if os.path.exists("temp_filled.pdf"):
            os.remove("temp_filled.pdf")
        
        file_size = os.path.getsize(output_pdf)
        print(f"\n✅ FORCE VISIBLE PDF CREATED: {output_pdf} ({file_size:,} bytes)")
        print("🎉 Content is now permanently visible and cannot be hidden!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in force visible fill: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_force_visible():
    """Test the force visible approach"""
    
    # Create test data with actual field names from the PDF
    test_document = {
        'id': 'force_visible_test',
        'name': 'force_visible_test.pdf',
        'pdf_fields': [
            {
                'id': 'test_property_address',
                'name': 'Property Address',
                'pdf_field_name': 'property_address1',
                'value': 'FORCED VISIBLE: 123 Test Street',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_apartment',
                'name': 'Apartment Number',
                'pdf_field_name': 'apt_num1',
                'value': 'FORCED VISIBLE: Apt 301',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_electric_heat',
                'name': 'Electric Heat',
                'pdf_field_name': 'fuel_type_elec2',
                'value': 'yes',
                'type': 'radio',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_single_family',
                'name': 'Single Family Home',
                'pdf_field_name': 'dwelling_single_fam1',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_signature',
                'name': 'Signature',
                'pdf_field_name': 'signature3',
                'value': 'FORCED VISIBLE SIGNATURE - John Smith',
                'type': 'signature',
                'assigned_to': 'user2',
                'position': {'x': 43, 'y': 470},
                'page': 2
            }
        ]
    }
    
    success = force_visible_fill_pdf(
        'homeworks.pdf',
        test_document,
        'FORCE_VISIBLE_OUTPUT.pdf'
    )
    
    if success:
        print("\n🎯 SUCCESS! Check 'FORCE_VISIBLE_OUTPUT.pdf'")
        print("📋 This PDF has content permanently burned into the pages")
        print("🔍 Content will be visible in ANY PDF viewer")
    
    return success

if __name__ == "__main__":
    test_force_visible()