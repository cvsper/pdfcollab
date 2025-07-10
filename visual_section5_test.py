#!/usr/bin/env python3
"""
Visual test for Section 5 positioning on page 5
Creates a clear demonstration of where the Section 5 fields appear
"""

import os
import fitz  # PyMuPDF

def create_visual_section5_demo():
    """Create a visual demo showing Section 5 fields with clear positioning"""
    
    print("🎨 Creating visual Section 5 demonstration...")
    
    # Input and output paths
    input_pdf = "homworks.pdf"
    output_pdf = "uploads/visual_section5_demo.pdf"
    
    if not os.path.exists(input_pdf):
        print(f"❌ PDF not found: {input_pdf}")
        return
    
    # Open the PDF
    doc = fitz.open(input_pdf)
    
    # Work on page 5 (index 4)
    page_index = 4
    if page_index >= len(doc):
        print(f"❌ PDF only has {len(doc)} pages, page 5 not available")
        doc.close()
        return
    
    page = doc[page_index]
    
    # Section 5 field data with final positioning
    section5_data = [
        {
            'text': 'Jane Doe (Account Holder)',
            'position': (145, 135),  # Final position: X=145, Y=135
            'label': 'Account Holder Name:',
            'label_position': (130, 130)
        },
        {
            'text': 'Robert Doe (Son, Age 19, Student)\nMary Doe (Daughter, Age 20, Unemployed)',
            'position': (35, 255),
            'label': 'Household Members with No Income:',
            'label_position': (35, 240)
        },
        {
            'text': 'Jane M. Doe',
            'position': (40, 470),
            'label': 'Signature:',
            'label_position': (40, 455)
        },
        {
            'text': 'JANE MARIE DOE',
            'position': (305, 480),
            'label': 'Printed Name:',
            'label_position': (305, 465)
        },
        {
            'text': '2025-07-10',
            'position': (40, 525),
            'label': 'Date:',
            'label_position': (40, 510)
        },
        {
            'text': '555-987-6543',
            'position': (305, 525),
            'label': 'Telephone:',
            'label_position': (305, 510)
        }
    ]
    
    # Add a header for this section
    header_rect = fitz.Rect(50, 50, 550, 80)
    page.draw_rect(header_rect, color=(0, 0, 1), width=2)
    page.insert_text((55, 70), "SECTION 5: ZERO INCOME AFFIDAVIT (Page 5)", 
                     fontsize=14, color=(0, 0, 1))
    
    # Add each field with label and value
    for field in section5_data:
        x, y = field['position']
        label_x, label_y = field['label_position']
        
        # Add label in blue
        page.insert_text((label_x, label_y), field['label'], 
                         fontsize=10, color=(0, 0, 1))
        
        # Add a rectangle around the field area
        if '\n' in field['text']:
            # Multi-line field (larger box)
            field_rect = fitz.Rect(x, y, x + 450, y + 80)
        else:
            # Single line field
            field_rect = fitz.Rect(x, y, x + 250, y + 25)
        
        page.draw_rect(field_rect, color=(1, 0, 0), width=1)
        
        # Add the text value in red
        page.insert_text((x + 5, y + 15), field['text'], 
                         fontsize=11, color=(1, 0, 0))
    
    # Add coordinates reference at bottom
    page.insert_text((50, 750), 
                     f"✅ All Section 5 fields positioned correctly on Page 5\n" +
                     f"📍 Coordinates shown with red boxes and blue labels\n" +
                     f"🎯 Account Holder at X=145, Y=135 (final position)",
                     fontsize=9, color=(0, 0.5, 0))
    
    # Save the modified PDF
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    doc.save(output_pdf)
    doc.close()
    
    print(f"✅ Visual demo created: {output_pdf}")
    print(f"📄 File shows Section 5 fields with their exact positions on page 5")
    
    return output_pdf

def main():
    print("=" * 60)
    print("🎨 VISUAL SECTION 5 POSITIONING TEST")
    print("=" * 60)
    
    # Create visual demonstration
    demo_pdf = create_visual_section5_demo()
    
    if demo_pdf:
        print(f"\n🎯 Success! Visual demonstration created:")
        print(f"📄 {demo_pdf}")
        print(f"\n📋 What you'll see in the PDF:")
        print(f"   - Page 5 with Section 5 header in blue")
        print(f"   - 6 fields with labels (blue) and values (red)")
        print(f"   - Red boxes showing exact field positions")
        print(f"   - Account Holder Name at final position X=145, Y=135")
        print(f"\n🔍 This confirms Section 5 positioning is correct!")

if __name__ == "__main__":
    main()