#!/usr/bin/env python3
"""
Test final Section 5 positions with recent adjustments
"""

import os
import fitz  # PyMuPDF
from datetime import datetime

def create_section5_test_pdf():
    """Create test PDF with updated Section 5 positions"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        print(f"❌ Error: {homeworks_path} not found")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"SECTION5_FINAL_TEST_{timestamp}.pdf"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    
    print("🎯 Section 5 Final Position Test")
    print("=" * 50)
    print(f"✅ Source: {homeworks_path}")
    print(f"📄 Output: {output_filename}")
    
    # Updated positions from app.py
    SECTION5_WIDGET_POSITIONS = [
        {"field": "account_holder_name_affidavit", "x": 155, "y": 145, "width": 250, "height": 25},
        {"field": "household_member_names_no_income", "x": 45, "y": 265, "width": 450, "height": 80},
        {"field": "affidavit_signature", "x": 40, "y": 490, "width": 200, "height": 30},
        {"field": "printed_name_affidavit", "x": 315, "y": 490, "width": 230, "height": 25},
        {"field": "date_affidavit", "x": 50, "y": 535, "width": 150, "height": 25},
        {"field": "telephone_affidavit", "x": 315, "y": 535, "width": 150, "height": 25}
    ]
    
    # Sample data for Section 5
    section5_data = {
        "account_holder_name_affidavit": "Jane Doe",
        "household_member_names_no_income": "Robert Doe (Son, Age 19, Student)\nMary Doe (Daughter, Age 20, Unemployed)",
        "affidavit_signature": "Jane Doe",
        "printed_name_affidavit": "JANE DOE",
        "date_affidavit": "07/10/2025",
        "telephone_affidavit": "(860) 555-0123"
    }
    
    try:
        # Open PDF
        doc = fitz.open(homeworks_path)
        print(f"📄 PDF opened: {len(doc)} pages")
        
        # Use page 5 (index 4) as confirmed
        affidavit_page = 4
        page = doc[affidavit_page]
        print(f"✅ Using page {affidavit_page + 1} for Zero Income Affidavit")
        
        # Add Section 5 fields with final positions
        print(f"\n📝 Adding Section 5 fields...")
        
        for pos in SECTION5_WIDGET_POSITIONS:
            field_name = pos["field"]
            x, y, width, height = pos["x"], pos["y"], pos["width"], pos["height"]
            value = section5_data.get(field_name, "")
            
            if value:
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
                    fill_color=(1, 1, 1),  # White background
                    border_color=(0, 0, 0)
                )
                text_annot.update()
                
                print(f"   ✅ {field_name}: {value}")
                print(f"      📍 Position: x={x}, y={y}")
        
        # Add a subtle header to indicate this is the test version
        header_rect = fitz.Rect(400, 20, 580, 40)
        header_annot = page.add_freetext_annot(
            header_rect,
            "Section 5 Test - Final",
            fontsize=10,
            fontname="helv",
            text_color=(0.5, 0.5, 0.5),
            fill_color=(1, 1, 1),
            border_color=(0.8, 0.8, 0.8)
        )
        header_annot.update()
        
        # Save the PDF
        doc.save(output_path)
        doc.close()
        
        file_size = os.path.getsize(output_path)
        
        print(f"\n🎯 Section 5 Final Test Complete!")
        print(f"📁 File: {output_path}")
        print(f"📊 Size: {file_size:,} bytes")
        print(f"📄 Page: {affidavit_page + 1}")
        
        print(f"\n📍 Final Positions:")
        print(f"   • Account Holder Name: x=155, y=145")
        print(f"   • Household Members: x=45, y=265")
        print(f"   • Signature: x=40, y=490 (adjusted)")
        print(f"   • Printed Name: x=315, y=490")
        print(f"   • Date: x=50, y=535")
        print(f"   • Telephone: x=315, y=535")
        
        print(f"\n🔍 Open the PDF to verify Section 5 field placement!")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Section 5 Final Position Test")
    print("Testing with signature moved to x=40, y=490")
    print()
    
    result = create_section5_test_pdf()
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"📄 Test PDF created with final Section 5 positions")
        print(f"📁 Open: {result}")
    else:
        print(f"\n❌ Test failed")

if __name__ == "__main__":
    main()