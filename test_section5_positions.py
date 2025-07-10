#!/usr/bin/env python3
"""
Test Section 5 with the exact widget positions that worked in the other app
"""

import os
import fitz  # PyMuPDF
from datetime import datetime

def create_section5_with_positions():
    """Create Section 5 demo using the exact widget positions that worked"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        print(f"❌ Error: {homeworks_path} not found")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"SECTION5_POSITIONED_DEMO_{timestamp}.pdf"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    
    print("🎯 Section 5 Demo - Using Exact Widget Positions")
    print("=" * 50)
    print(f"✅ Source: {homeworks_path}")
    print(f"📄 Output: {output_filename}")
    
    # The exact positions that worked in your other app
    improved_positions = [
        {"x": 145, "y": 135, "width": 250, "height": 25, "label": "Account Holder Name"},
        {"x": 35, "y": 255, "width": 450, "height": 80, "label": "Household Members"},
        {"x": 40, "y": 470, "width": 200, "height": 30, "label": "Signature"},
        {"x": 305, "y": 480, "width": 230, "height": 25, "label": "Printed Name"},
        {"x": 40, "y": 525, "width": 150, "height": 25, "label": "Date"},
        {"x": 305, "y": 525, "width": 150, "height": 25, "label": "Telephone"}
    ]
    
    # Section 5 data
    section5_data = [
        "John Smith",  # Account Holder Name
        "Mary Smith\nDavid Johnson\nSarah Wilson",  # Household Members
        "Jane Smith",  # Signature
        "Jane Smith",  # Printed Name
        "01/10/2025",  # Date
        "(860) 555-0123"  # Telephone
    ]
    
    try:
        # Open PDF
        doc = fitz.open(homeworks_path)
        print(f"📄 PDF opened: {len(doc)} pages")
        
        # Find the Zero Income Affidavit page (usually page 5)
        affidavit_page = None
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text().lower()
            if "zero income affidavit" in text or "income affidavit" in text:
                affidavit_page = page_num
                break
        
        if affidavit_page is None:
            # Default to last page
            affidavit_page = len(doc) - 1
            print(f"⚠️  Zero Income Affidavit page not found by text, using page {affidavit_page + 1}")
        else:
            print(f"✅ Found Zero Income Affidavit on page {affidavit_page + 1}")
        
        page = doc[affidavit_page]
        
        # Add Section 5 fields using exact positions
        print(f"\n📝 Adding Section 5 fields with exact positions...")
        
        for i, (pos, data) in enumerate(zip(improved_positions, section5_data)):
            x, y, width, height = pos["x"], pos["y"], pos["width"], pos["height"]
            label = pos["label"]
            
            # Create rectangle for the field
            rect = fitz.Rect(x, y, x + width, y + height)
            
            # Determine font size based on field type
            if label == "Household Members":
                fontsize = 9  # Smaller for multi-line text
            else:
                fontsize = 11
            
            # Add freetext annotation for the field
            text_annot = page.add_freetext_annot(
                rect,
                data,
                fontsize=fontsize,
                fontname="helv",
                text_color=(0, 0, 0),
                fill_color=(1, 1, 0.9),  # Light yellow background
                border_color=(0.5, 0.5, 0.5)
            )
            text_annot.update()
            
            # Add a small label above the field
            label_rect = fitz.Rect(x, y - 15, x + width, y)
            label_annot = page.add_freetext_annot(
                label_rect,
                label,
                fontsize=8,
                fontname="helv",
                text_color=(0, 0, 0.8),
                fill_color=(0.9, 0.9, 1),
                border_color=(0.8, 0.8, 1)
            )
            label_annot.update()
            
            print(f"   ✅ {label}: {data}")
            print(f"      📍 Position: x={x}, y={y}, size={width}x{height}")
        
        # Add a header annotation
        header_rect = fitz.Rect(35, 80, 500, 120)
        header_annot = page.add_freetext_annot(
            header_rect,
            "SECTION 5: ZERO INCOME AFFIDAVIT - COMPLETED BY USER 2",
            fontsize=14,
            fontname="helv",
            text_color=(1, 1, 1),
            fill_color=(0, 0, 0.8),  # Blue background
            border_color=(0, 0, 0)
        )
        header_annot.update()
        
        # Add position reference
        ref_rect = fitz.Rect(35, 600, 500, 650)
        ref_text = "Widget positions used: x=145,y=135 | x=35,y=255 | x=40,y=470 | x=305,y=480 | x=40,y=525 | x=305,y=525"
        ref_annot = page.add_freetext_annot(
            ref_rect,
            ref_text,
            fontsize=8,
            fontname="helv",
            text_color=(0.5, 0.5, 0.5),
            fill_color=(1, 1, 1),
            border_color=(0.8, 0.8, 0.8)
        )
        ref_annot.update()
        
        # Save the PDF
        doc.save(output_path)
        doc.close()
        
        file_size = os.path.getsize(output_path)
        
        print(f"\n🎯 Section 5 Positioned Demo Complete!")
        print(f"📁 File: {output_path}")
        print(f"📊 Size: {file_size:,} bytes")
        print(f"📄 Page: {affidavit_page + 1} (Zero Income Affidavit)")
        
        print(f"\n📍 Exact Coordinates Used:")
        for pos in improved_positions:
            print(f"   • {pos['label']}: x={pos['x']}, y={pos['y']}, {pos['width']}x{pos['height']}")
        
        print(f"\n🔍 Open the PDF to see Section 5 fields positioned exactly where they worked!")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_pdf_processor_with_positions():
    """Show how to integrate these positions into the main PDF processor"""
    
    print(f"\n🔧 Integration Guide for PDF Processor:")
    print(f"=" * 40)
    
    code_snippet = '''
# Add this to pdf_processor.py or app.py for Section 5 field positioning

SECTION5_WIDGET_POSITIONS = [
    {"field": "account_holder_name", "x": 145, "y": 135, "width": 250, "height": 25},
    {"field": "zero_income_names", "x": 35, "y": 255, "width": 450, "height": 80},
    {"field": "affidavit_signature", "x": 40, "y": 470, "width": 200, "height": 30},
    {"field": "affidavit_printed_name", "x": 305, "y": 480, "width": 230, "height": 25},
    {"field": "affidavit_date", "x": 40, "y": 525, "width": 150, "height": 25},
    {"field": "affidavit_telephone", "x": 305, "y": 525, "width": 150, "height": 25}
]

def fill_section5_fields(page, user2_data):
    """Fill Section 5 fields using exact positions"""
    for pos in SECTION5_WIDGET_POSITIONS:
        field_name = pos["field"]
        if field_name in user2_data:
            x, y, width, height = pos["x"], pos["y"], pos["width"], pos["height"]
            rect = fitz.Rect(x, y, x + width, y + height)
            
            # Add the field value at exact position
            page.add_freetext_annot(
                rect,
                user2_data[field_name],
                fontsize=10,
                fontname="helv"
            )
'''
    
    print(code_snippet)

def main():
    """Main function"""
    print("🎯 PDF Collaborator - Section 5 Exact Positioning Demo")
    print("Using widget positions that worked perfectly in other app")
    print()
    
    result = create_section5_with_positions()
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"📄 Section 5 positioned using exact coordinates")
        print(f"📁 Open: {result}")
        
        # Show integration guide
        update_pdf_processor_with_positions()
    else:
        print(f"\n❌ Demo failed")

if __name__ == "__main__":
    main()