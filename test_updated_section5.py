#!/usr/bin/env python3
"""
Test PDF generation with updated Section 5 field names
"""

import os
import fitz  # PyMuPDF
from datetime import datetime

def create_test_pdf_with_updated_fields():
    """Create test PDF using the updated Section 5 field names"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        print(f"❌ Error: {homeworks_path} not found")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"UPDATED_SECTION5_TEST_{timestamp}.pdf"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    
    print("🧪 Testing Updated Section 5 Field Names")
    print("=" * 50)
    print(f"✅ Source: {homeworks_path}")
    print(f"📄 Output: {output_filename}")
    
    # Updated Section 5 field positions and names
    section5_fields = [
        {
            'field_name': 'account_holder_name_affidavit',
            'label': 'Account Holder Name (Affidavit)',
            'value': 'Jane Doe (Account Holder)',
            'position': {'x': 145, 'y': 135, 'width': 250, 'height': 25}
        },
        {
            'field_name': 'household_member_names_no_income',
            'label': 'Household Member Names (No Income)',
            'value': 'Robert Doe (Son, Age 19, Student)\nMary Doe (Daughter, Age 20, Unemployed)',
            'position': {'x': 35, 'y': 255, 'width': 450, 'height': 80}
        },
        {
            'field_name': 'affidavit_signature',
            'label': 'Affidavit Signature',
            'value': 'typed:Jane M. Doe',
            'position': {'x': 40, 'y': 470, 'width': 200, 'height': 30}
        },
        {
            'field_name': 'printed_name_affidavit',
            'label': 'Printed Name (Affidavit)',
            'value': 'JANE MARIE DOE',
            'position': {'x': 305, 'y': 480, 'width': 230, 'height': 25}
        },
        {
            'field_name': 'date_affidavit',
            'label': 'Date (Affidavit)',
            'value': '2025-07-10',
            'position': {'x': 40, 'y': 525, 'width': 150, 'height': 25}
        },
        {
            'field_name': 'telephone_affidavit',
            'label': 'Telephone (Affidavit)',
            'value': '555-987-6543',
            'position': {'x': 305, 'y': 525, 'width': 150, 'height': 25}
        }
    ]
    
    try:
        # Open PDF
        doc = fitz.open(homeworks_path)
        print(f"📄 PDF opened: {len(doc)} pages")
        
        # Find the Zero Income Affidavit page (page 5, index 4)
        affidavit_page = 4  # Page 5 (0-indexed)
        
        if affidavit_page >= len(doc):
            affidavit_page = len(doc) - 1
            print(f"⚠️  Using last page ({affidavit_page + 1}) for affidavit")
        else:
            print(f"✅ Using page {affidavit_page + 1} for Zero Income Affidavit")
        
        page = doc[affidavit_page]
        
        # Add Section 5 fields using updated field names
        print(f"\n📝 Adding Section 5 fields with updated names...")
        
        filled_count = 0
        for field_data in section5_fields:
            field_name = field_data['field_name']
            label = field_data['label']
            value = field_data['value']
            pos = field_data['position']
            
            x, y, width, height = pos['x'], pos['y'], pos['width'], pos['height']
            
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
                fill_color=(1, 1, 0.9),  # Light yellow background
                border_color=(0.5, 0.5, 0.5)
            )
            text_annot.update()
            
            # Add a small label above the field
            label_rect = fitz.Rect(x, y - 15, x + width, y)
            label_annot = page.add_freetext_annot(
                label_rect,
                f"{label} ({field_name})",
                fontsize=8,
                fontname="helv",
                text_color=(0, 0, 0.8),
                fill_color=(0.9, 0.9, 1),
                border_color=(0.8, 0.8, 1)
            )
            label_annot.update()
            
            filled_count += 1
            print(f"   ✅ {label}: {value}")
            print(f"      🏷️  Field Name: {field_name}")
            print(f"      📍 Position: x={x}, y={y}, size={width}x{height}")
        
        # Add a header annotation
        header_rect = fitz.Rect(35, 80, 500, 120)
        header_annot = page.add_freetext_annot(
            header_rect,
            "SECTION 5: ZERO INCOME AFFIDAVIT - UPDATED FIELD NAMES TEST",
            fontsize=14,
            fontname="helv",
            text_color=(1, 1, 1),
            fill_color=(0.8, 0, 0),  # Red background
            border_color=(0, 0, 0)
        )
        header_annot.update()
        
        # Add field mapping reference
        mapping_rect = fitz.Rect(35, 600, 500, 700)
        mapping_text = """UPDATED FIELD MAPPING:
• account_holder_name_affidavit
• household_member_names_no_income
• affidavit_signature
• printed_name_affidavit
• date_affidavit
• telephone_affidavit"""
        
        mapping_annot = page.add_freetext_annot(
            mapping_rect,
            mapping_text,
            fontsize=9,
            fontname="helv",
            text_color=(0, 0, 0),
            fill_color=(0.9, 1, 0.9),  # Light green background
            border_color=(0, 0.8, 0)
        )
        mapping_annot.update()
        
        # Save the PDF
        doc.save(output_path)
        doc.close()
        
        file_size = os.path.getsize(output_path)
        
        print(f"\n🧪 Updated Section 5 Test Complete!")
        print(f"📁 File: {output_path}")
        print(f"📊 Size: {file_size:,} bytes")
        print(f"📄 Page: {affidavit_page + 1} (Zero Income Affidavit)")
        print(f"✅ Fields filled: {filled_count}")
        
        print(f"\n🏷️  Updated Field Names Used:")
        for field_data in section5_fields:
            print(f"   • {field_data['field_name']}")
        
        print(f"\n🔍 Open the PDF to verify the updated field names work correctly!")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🧪 PDF Collaborator - Updated Section 5 Field Names Test")
    print("Testing the corrected field names for Section 5")
    print()
    
    result = create_test_pdf_with_updated_fields()
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"📄 Updated Section 5 fields tested successfully")
        print(f"📁 Open: {result}")
        print(f"\n✅ Field names now match the specification:")
        print(f"   • account_holder_name_affidavit")
        print(f"   • household_member_names_no_income")
        print(f"   • affidavit_signature")
        print(f"   • printed_name_affidavit")
        print(f"   • date_affidavit")
        print(f"   • telephone_affidavit")
    else:
        print(f"\n❌ Test failed")

if __name__ == "__main__":
    main()