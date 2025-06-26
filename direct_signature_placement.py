#!/usr/bin/env python3
"""
Direct signature placement - bypass form fields entirely
"""

import fitz
import os

def place_signature_directly():
    """Place signature directly on the PDF at visible locations"""
    print("🎯 DIRECT SIGNATURE PLACEMENT TEST")
    print("=" * 50)
    
    # Open the PDF
    doc = fitz.open('homeworks.pdf')
    
    # Find page 3 (where signature should be)
    if len(doc) >= 3:
        page = doc[2]  # Page 3 (0-indexed)
        print(f"📄 Working on page 3, size: {page.rect.width} x {page.rect.height}")
        
        # Place signature at multiple strategic locations
        signature_text = "James deen"
        
        # Location 1: Where we think the signature field is
        page.insert_text(
            (50, 480),  # Near the signature field location
            f"SIGNATURE: {signature_text}",
            fontsize=16,
            color=(1, 0, 0)  # Red color for visibility
        )
        
        # Location 2: Bottom of the page
        page.insert_text(
            (50, page.rect.height - 50),
            f"APPLICANT SIGNATURE: {signature_text}",
            fontsize=18,
            color=(0, 0, 1)  # Blue color
        )
        
        # Location 3: Center of page
        page.insert_text(
            (page.rect.width/2 - 100, page.rect.height/2),
            f"*** SIGNATURE: {signature_text} ***",
            fontsize=20,
            color=(0, 0.7, 0)  # Green color
        )
        
        # Location 4: Top of page
        page.insert_text(
            (50, 50),
            f"TEST SIGNATURE: {signature_text}",
            fontsize=14,
            color=(0.5, 0, 0.5)  # Purple color
        )
        
        print("✅ Added signatures at 4 different locations on page 3")
    
    # Also add signature to page 4 and 5 just in case
    for page_num in [3, 4]:
        if len(doc) > page_num:
            page = doc[page_num]
            page.insert_text(
                (50, 100),
                f"PAGE {page_num + 1} SIGNATURE: {signature_text}",
                fontsize=16,
                color=(1, 0, 0)
            )
            print(f"✅ Added signature to page {page_num + 1}")
    
    # Save the PDF
    output_path = 'DIRECT_SIGNATURE_PLACEMENT.pdf'
    doc.save(output_path)
    doc.close()
    
    file_size = os.path.getsize(output_path)
    print(f"\n🎉 DIRECT SIGNATURE PDF CREATED: {output_path} ({file_size:,} bytes)")
    print("📍 This PDF has signatures placed at multiple visible locations:")
    print("   🔴 Red signature near expected field location")
    print("   🔵 Blue signature at bottom of page")  
    print("   🟢 Green signature in center of page")
    print("   🟣 Purple signature at top of page")
    print("   🔴 Red signatures on additional pages")
    print("\n🔍 At least one of these signatures MUST be visible!")
    
    return True

def create_minimal_signature_test():
    """Create the most minimal signature test possible"""
    print("\n🎯 MINIMAL SIGNATURE TEST")
    print("-" * 30)
    
    from pdf_processor import PDFProcessor
    processor = PDFProcessor()
    
    # Just fill the signature field with a simple value
    minimal_doc = {
        'pdf_fields': [{
            'pdf_field_name': 'signature3',
            'value': 'James deen',
            'type': 'text'
        }]
    }
    
    # Use the regular method (not force visible)
    doc = fitz.open('homeworks.pdf')
    
    # Find and fill the signature field manually
    for page_num in range(len(doc)):
        page = doc[page_num]
        widgets = list(page.widgets())
        
        for widget in widgets:
            if widget.field_name == 'signature3':
                print(f"📝 Found signature3 field on page {page_num + 1}")
                
                # Set the field value
                widget.field_value = 'James deen'
                widget.update()
                
                # Also add visible text overlay
                rect = widget.rect
                page.insert_text(
                    (rect.x0, rect.y0 + rect.height - 2),
                    'James deen',
                    fontsize=12,
                    color=(0, 0, 0)
                )
                
                print(f"✅ Filled signature field and added overlay")
                break
    
    doc.save('MINIMAL_SIGNATURE_TEST.pdf')
    doc.close()
    
    print("✅ Created MINIMAL_SIGNATURE_TEST.pdf")

if __name__ == "__main__":
    place_signature_directly()
    create_minimal_signature_test()