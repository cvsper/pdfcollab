#!/usr/bin/env python3
"""
Test PDF with adjusted Section 5 positions (+10 right, +20 down)
"""

import os
import fitz  # PyMuPDF
from datetime import datetime

def create_test_pdf_adjusted_positions():
    """Create test PDF with adjusted Section 5 positions"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        print(f"❌ Error: {homeworks_path} not found")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"ADJUSTED_SECTION5_TEST_{timestamp}.pdf"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    
    print("🎯 Testing Adjusted Section 5 Positions")
    print("=" * 50)
    print(f"✅ Source: {homeworks_path}")
    print(f"📄 Output: {output_filename}")
    print(f"📍 Adjustment: +10 right, +20 down")
    
    # Adjusted Section 5 field positions (+10 right, +20 down)
    section5_fields = [
        {
            'field_name': 'account_holder_name_affidavit',
            'label': 'Account Holder Name (Affidavit)',
            'value': 'Jane Doe (Account Holder)',
            'old_position': {'x': 145, 'y': 135},
            'new_position': {'x': 155, 'y': 155, 'width': 250, 'height': 25}
        },
        {
            'field_name': 'household_member_names_no_income',
            'label': 'Household Member Names (No Income)',
            'value': 'Robert Doe (Son, Age 19, Student)\nMary Doe (Daughter, Age 20, Unemployed)',
            'old_position': {'x': 35, 'y': 255},
            'new_position': {'x': 45, 'y': 275, 'width': 450, 'height': 80}
        },
        {
            'field_name': 'affidavit_signature',
            'label': 'Affidavit Signature',
            'value': 'typed:Jane M. Doe',
            'old_position': {'x': 40, 'y': 470},
            'new_position': {'x': 50, 'y': 490, 'width': 200, 'height': 30}
        },
        {
            'field_name': 'printed_name_affidavit',
            'label': 'Printed Name (Affidavit)',
            'value': 'JANE MARIE DOE',
            'old_position': {'x': 305, 'y': 480},
            'new_position': {'x': 315, 'y': 500, 'width': 230, 'height': 25}
        },
        {
            'field_name': 'date_affidavit',
            'label': 'Date (Affidavit)',
            'value': '2025-07-10',
            'old_position': {'x': 40, 'y': 525},
            'new_position': {'x': 50, 'y': 545, 'width': 150, 'height': 25}
        },
        {
            'field_name': 'telephone_affidavit',
            'label': 'Telephone (Affidavit)',
            'value': '555-987-6543',
            'old_position': {'x': 305, 'y': 525},
            'new_position': {'x': 315, 'y': 545, 'width': 150, 'height': 25}
        }
    ]
    
    try:
        # Open PDF
        doc = fitz.open(homeworks_path)
        print(f"📄 PDF opened: {len(doc)} pages")
        
        # Use page 5 (index 4) for Zero Income Affidavit
        affidavit_page = 4
        
        if affidavit_page >= len(doc):
            affidavit_page = len(doc) - 1
            print(f"⚠️  Using last page ({affidavit_page + 1}) for affidavit")
        else:
            print(f"✅ Using page {affidavit_page + 1} for Zero Income Affidavit")
        
        page = doc[affidavit_page]
        
        # Add Section 5 fields with adjusted positions
        print(f"\n📝 Adding Section 5 fields with adjusted positions...")
        
        filled_count = 0
        for field_data in section5_fields:
            field_name = field_data['field_name']
            label = field_data['label']
            value = field_data['value']
            old_pos = field_data['old_position']
            new_pos = field_data['new_position']
            
            x, y, width, height = new_pos['x'], new_pos['y'], new_pos['width'], new_pos['height']
            
            # Create rectangle for the field
            rect = fitz.Rect(x, y, x + width, y + height)
            
            # Determine font size based on field type
            if field_name == "household_member_names_no_income":
                fontsize = 9  # Smaller for multi-line text
            else:
                fontsize = 11
            
            # Add freetext annotation for the field
            text_annot = page.add_freetext_annot(
                rect,
                value,
                fontsize=fontsize,
                fontname="helv",
                text_color=(0, 0, 0),
                fill_color=(0.9, 1, 0.9),  # Light green background
                border_color=(0, 0.8, 0)
            )
            text_annot.update()
            
            # Add a small label above the field
            label_rect = fitz.Rect(x, y - 15, x + width, y)
            label_annot = page.add_freetext_annot(
                label_rect,
                f"{label}",
                fontsize=8,
                fontname="helv",
                text_color=(0, 0, 0.8),
                fill_color=(0.9, 0.9, 1),
                border_color=(0.8, 0.8, 1)
            )
            label_annot.update()
            
            filled_count += 1
            print(f"   ✅ {label}: {value}")
            print(f"      📍 Old: x={old_pos['x']}, y={old_pos['y']}")
            print(f"      📍 New: x={x}, y={y} (+{x-old_pos['x']}, +{y-old_pos['y']})")
        
        # Add a header annotation
        header_rect = fitz.Rect(35, 80, 500, 120)
        header_annot = page.add_freetext_annot(
            header_rect,
            "SECTION 5: ADJUSTED POSITIONS (+10 RIGHT, +20 DOWN)",
            fontsize=14,
            fontname="helv",
            text_color=(1, 1, 1),
            fill_color=(0, 0.8, 0),  # Green background
            border_color=(0, 0, 0)
        )
        header_annot.update()
        
        # Add position adjustment summary
        summary_rect = fitz.Rect(35, 600, 500, 700)
        summary_text = """POSITION ADJUSTMENTS APPLIED:
• All fields moved 10 points RIGHT (+10 x)
• All fields moved 20 points DOWN (+20 y)
• Width and height unchanged
• Updated coordinates now active in app.py"""
        
        summary_annot = page.add_freetext_annot(
            summary_rect,
            summary_text,
            fontsize=9,
            fontname="helv",
            text_color=(0, 0, 0),
            fill_color=(1, 1, 0.9),  # Light yellow background
            border_color=(0.8, 0.8, 0)
        )
        summary_annot.update()
        
        # Save the PDF
        doc.save(output_path)
        doc.close()
        
        file_size = os.path.getsize(output_path)
        
        print(f"\n🎯 Adjusted Positions Test Complete!")
        print(f"📁 File: {output_path}")
        print(f"📊 Size: {file_size:,} bytes")
        print(f"📄 Page: {affidavit_page + 1} (Zero Income Affidavit)")
        print(f"✅ Fields filled: {filled_count}")
        
        print(f"\n📍 Position Adjustments Applied:")
        print(f"   • All X coordinates: +10 (moved right)")
        print(f"   • All Y coordinates: +20 (moved down)")
        
        print(f"\n🔍 Open the PDF to verify the adjusted positions!")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🎯 PDF Collaborator - Adjusted Section 5 Positions Test")
    print("Testing Section 5 fields moved 10 right, 20 down")
    print()
    
    result = create_test_pdf_adjusted_positions()
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"📄 Adjusted Section 5 positions tested successfully")
        print(f"📁 Open: {result}")
        print(f"\n✅ All fields moved:")
        print(f"   • 10 points RIGHT (+10 x)")
        print(f"   • 20 points DOWN (+20 y)")
        print(f"\n🔧 Updated coordinates are now active in app.py")
    else:
        print(f"\n❌ Test failed")

if __name__ == "__main__":
    main()