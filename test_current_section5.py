#!/usr/bin/env python3
"""
Test current Section 5 positions to debug placement issues
"""

import os
import fitz  # PyMuPDF
from datetime import datetime

def test_current_section5_positions():
    """Test the current Section 5 positions from app.py"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        print(f"❌ Error: {homeworks_path} not found")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"CURRENT_SECTION5_TEST_{timestamp}.pdf"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    
    print("🔍 Testing Current Section 5 Positions")
    print("=" * 50)
    
    # Current positions from app.py
    SECTION5_WIDGET_POSITIONS = [
        {"field": "account_holder_name_affidavit", "x": 155, "y": 145, "width": 250, "height": 25},
        {"field": "household_member_names_no_income", "x": 45, "y": 265, "width": 450, "height": 80},
        {"field": "affidavit_signature", "x": 50, "y": 480, "width": 200, "height": 30},
        {"field": "printed_name_affidavit", "x": 315, "y": 490, "width": 230, "height": 25},
        {"field": "date_affidavit", "x": 50, "y": 535, "width": 150, "height": 25},
        {"field": "telephone_affidavit", "x": 315, "y": 535, "width": 150, "height": 25}
    ]
    
    # Test data
    test_data = {
        "account_holder_name_affidavit": "John Smith",
        "household_member_names_no_income": "Robert Smith (Age 22)\nMary Smith (Age 19)",
        "affidavit_signature": "John Smith",
        "printed_name_affidavit": "JOHN SMITH",
        "date_affidavit": "07/10/2025",
        "telephone_affidavit": "(860) 555-1234"
    }
    
    try:
        doc = fitz.open(homeworks_path)
        print(f"📄 PDF opened: {len(doc)} pages")
        
        # Test on different pages to find the right one
        for test_page in [4, 3, 2]:  # Try pages 5, 4, 3
            print(f"\n🧪 Testing on page {test_page + 1}...")
            
            # Create a test copy
            test_doc = fitz.open(homeworks_path)
            page = test_doc[test_page]
            
            # Add reference grid
            for y in range(0, 800, 50):
                page.draw_line(fitz.Point(0, y), fitz.Point(600, y), color=(0.9, 0.9, 0.9))
                page.insert_text(fitz.Point(5, y), f"{y}", fontsize=8, color=(0.5, 0.5, 0.5))
            
            for x in range(0, 600, 50):
                page.draw_line(fitz.Point(x, 0), fitz.Point(x, 800), color=(0.9, 0.9, 0.9))
                page.insert_text(fitz.Point(x, 10), f"{x}", fontsize=8, color=(0.5, 0.5, 0.5))
            
            # Add fields at current positions
            for pos in SECTION5_WIDGET_POSITIONS:
                field_name = pos["field"]
                x, y, width, height = pos["x"], pos["y"], pos["width"], pos["height"]
                value = test_data.get(field_name, "TEST")
                
                # Draw rectangle to show field boundary
                rect = fitz.Rect(x, y, x + width, y + height)
                page.draw_rect(rect, color=(1, 0, 0), width=1)
                
                # Add field value
                fontsize = 9 if field_name == "household_member_names_no_income" else 11
                text_annot = page.add_freetext_annot(
                    rect,
                    value,
                    fontsize=fontsize,
                    fontname="helv",
                    text_color=(0, 0, 0),
                    fill_color=(1, 1, 0.8),
                    border_color=(0, 0, 0)
                )
                text_annot.update()
                
                # Add label
                label_text = f"{field_name} ({x},{y})"
                page.insert_text(fitz.Point(x, y - 5), label_text, fontsize=7, color=(0, 0, 1))
            
            # Save test page
            test_output = output_path.replace(".pdf", f"_page{test_page + 1}.pdf")
            test_doc.save(test_output)
            test_doc.close()
            print(f"   📄 Saved: {test_output}")
        
        doc.close()
        
        print(f"\n📊 Current positions being used:")
        for pos in SECTION5_WIDGET_POSITIONS:
            print(f"   • {pos['field']}: x={pos['x']}, y={pos['y']}")
        
        print(f"\n❓ Questions to check:")
        print(f"   1. Are the fields appearing on the correct page?")
        print(f"   2. Are they overlapping with existing content?")
        print(f"   3. Do they need to move up/down/left/right?")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Section 5 Position Debug")
    print()
    
    if test_current_section5_positions():
        print(f"\n✅ Test PDFs created - check them to see field positions")
        print(f"📋 Grid lines show coordinates for reference")
        print(f"🔴 Red boxes show field boundaries")
    else:
        print(f"\n❌ Test failed")

if __name__ == "__main__":
    main()