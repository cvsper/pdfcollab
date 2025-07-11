#!/usr/bin/env python3
"""
Simple Section 5 test with proper PDF saving
"""

import os
import fitz  # PyMuPDF
from datetime import datetime

def test_section5_simple():
    """Simple test of Section 5 positioning"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        print(f"❌ Error: {homworks_path} not found")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"SECTION5_SIMPLE_TEST_{timestamp}.pdf"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    
    print("🧪 Simple Section 5 Test")
    print("=" * 40)
    print(f"✅ Source: {homeworks_path}")
    print(f"📄 Output: {output_filename}")
    
    # Section 5 test data
    test_data = {
        'account_holder_name_affidavit': 'John Smith',
        'household_member_names_no_income': 'Robert Smith (Age 22)\nMary Smith (Age 19)',
        'affidavit_signature': 'John Smith',
        'printed_name_affidavit': 'JOHN SMITH',
        'date_affidavit': '2025-07-10',
        'telephone_affidavit': '(860) 555-1234'
    }
    
    # Section 5 positions (same as in pdf_processor.py)
    positions = [
        {"field": "account_holder_name_affidavit", "x": 155, "y": 145, "width": 250, "height": 25},
        {"field": "household_member_names_no_income", "x": 45, "y": 265, "width": 450, "height": 80},
        {"field": "affidavit_signature", "x": 40, "y": 490, "width": 200, "height": 30},
        {"field": "printed_name_affidavit", "x": 315, "y": 490, "width": 230, "height": 25},
        {"field": "date_affidavit", "x": 50, "y": 535, "width": 150, "height": 25},
        {"field": "telephone_affidavit", "x": 315, "y": 535, "width": 150, "height": 25}
    ]
    
    try:
        # Open PDF
        doc = fitz.open(homeworks_path)
        print(f"📖 PDF opened: {len(doc)} pages")
        
        # Use page 5 (index 4) for Zero Income Affidavit
        page = doc[4]
        print(f"📄 Working on page 5")
        
        # Add Section 5 fields
        filled_count = 0
        for pos in positions:
            field_name = pos["field"]
            field_value = test_data.get(field_name, "")
            
            if field_value:
                x, y, width, height = pos["x"], pos["y"], pos["width"], pos["height"]
                
                # Determine font size
                fontsize = 9 if field_name == "household_member_names_no_income" else 11
                
                # Add freetext annotation (same method as pdf_processor.py)
                rect = fitz.Rect(x, y, x + width, y + height)
                text_annot = page.add_freetext_annot(
                    rect,
                    field_value,
                    fontsize=fontsize,
                    fontname="helv",
                    text_color=(0, 0, 0),
                    fill_color=(1, 1, 1),  # White background
                    border_color=(0, 0, 0)
                )
                text_annot.update()
                
                filled_count += 1
                print(f"   ✅ {field_name}: {field_value} at ({x}, {y})")
        
        # Save to new file (not overwriting original)
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        
        file_size = os.path.getsize(output_path)
        
        print(f"\n🎯 Simple Section 5 Test Complete!")
        print(f"📁 File: {output_path}")
        print(f"📊 Size: {file_size:,} bytes")
        print(f"✅ Fields filled: {filled_count}")
        
        print(f"\n🔍 Check the PDF for:")
        print(f"   • Text orientation (should be right-side up)")
        print(f"   • Field positioning (should be in correct locations)")
        print(f"   • Text readability (should be clear and aligned)")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Simple Section 5 Test")
    print("Testing current PDF processor method")
    print()
    
    result = test_section5_simple()
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"📄 Test PDF created")
        print(f"📁 Open: {result}")
    else:
        print(f"\n❌ Test failed")

if __name__ == "__main__":
    main()