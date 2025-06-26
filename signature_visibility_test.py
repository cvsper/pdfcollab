#!/usr/bin/env python3
"""
Enhanced signature visibility test with multiple approaches
"""

import fitz
from pdf_processor import PDFProcessor
import os

def enhanced_signature_test():
    """Test signature with multiple visibility approaches"""
    print("🎯 ENHANCED SIGNATURE VISIBILITY TEST")
    print("=" * 60)
    
    processor = PDFProcessor()
    
    # Step 1: Find the exact signature field location
    doc = fitz.open('homeworks.pdf')
    signature_widgets = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        widgets = list(page.widgets())
        
        for widget in widgets:
            field_name = widget.field_name
            if field_name and ('sig' in field_name.lower() or field_name.lower() == 'signature'):
                rect = widget.rect
                signature_widgets.append({
                    'name': field_name,
                    'page': page_num,
                    'position': {'x': rect.x0, 'y': rect.y0, 'width': rect.width, 'height': rect.height},
                    'rect': rect
                })
                print(f"📝 Found signature field: {field_name} on page {page_num + 1}")
                print(f"   Position: ({rect.x0:.1f}, {rect.y0:.1f}) size: {rect.width:.1f}x{rect.height:.1f}")
    
    doc.close()
    
    if not signature_widgets:
        print("❌ No signature fields found!")
        return False
    
    # Step 2: Create test document with multiple signature approaches
    test_document = {
        'id': 'enhanced_signature_test',
        'name': 'enhanced_signature_test.pdf',
        'pdf_fields': []
    }
    
    # Add each signature field we found
    for i, sig_widget in enumerate(signature_widgets):
        test_document['pdf_fields'].append({
            'id': f'sig_{i}',
            'name': f'Signature {i+1}',
            'pdf_field_name': sig_widget['name'],
            'value': f'ENHANCED SIGNATURE TEST #{i+1} - James deen',
            'type': 'text',
            'assigned_to': 'user2'
        })
    
    # Step 3: Fill using force visible method
    print(f"\n🎯 Testing with {len(test_document['pdf_fields'])} signature fields...")
    
    success = processor.fill_pdf_with_force_visible('homeworks.pdf', test_document, 'ENHANCED_SIGNATURE_TEST.pdf')
    
    if not success:
        print("❌ Enhanced signature test failed")
        return False
    
    # Step 4: Additional manual signature overlay approach
    print("\n🎨 Adding manual signature overlays...")
    
    doc = fitz.open('ENHANCED_SIGNATURE_TEST.pdf')
    
    # Add large, bold signature overlays
    for sig_widget in signature_widgets:
        page_num = sig_widget['page']
        rect = sig_widget['rect']
        page = doc[page_num]
        
        # Clear the field area first (draw white rectangle)
        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), width=0)
        
        # Add large signature text
        signature_text = "MANUAL SIGNATURE - James deen"
        
        # Try multiple text insertions to ensure visibility
        for offset_y in [0, 2, 4]:
            for offset_x in [0, 1, 2]:
                page.insert_text(
                    (rect.x0 + offset_x, rect.y0 + rect.height - 3 + offset_y),
                    signature_text,
                    fontsize=12,
                    color=(0, 0, 0)  # Black
                )
        
        # Add a colored border around the signature area
        page.draw_rect(rect, color=(1, 0, 0), width=2)  # Red border
        
        print(f"   ✍️  Added manual signature overlay to {sig_widget['name']} on page {page_num + 1}")
    
    # Save the enhanced version
    doc.save('ENHANCED_SIGNATURE_FINAL.pdf')
    doc.close()
    
    file_size = os.path.getsize('ENHANCED_SIGNATURE_FINAL.pdf')
    print(f"\n🎉 ENHANCED SIGNATURE PDF CREATED: ENHANCED_SIGNATURE_FINAL.pdf ({file_size:,} bytes)")
    
    # Step 5: Create a simple test with just the signature field
    print("\n🎯 Creating SIMPLE SIGNATURE ONLY test...")
    
    simple_doc = {
        'id': 'simple_sig',
        'name': 'simple_sig.pdf',
        'pdf_fields': [{
            'id': 'signature3',
            'name': 'Signature',
            'pdf_field_name': 'signature3',
            'value': 'SIMPLE TEST - James deen',
            'type': 'text',
            'assigned_to': 'user2'
        }]
    }
    
    processor.fill_pdf_with_pymupdf('homeworks.pdf', simple_doc, 'SIMPLE_SIGNATURE_ONLY.pdf')
    
    print("✅ Created three test files:")
    print("   📄 ENHANCED_SIGNATURE_TEST.pdf - Force visible method")
    print("   📄 ENHANCED_SIGNATURE_FINAL.pdf - With manual overlays and red borders")
    print("   📄 SIMPLE_SIGNATURE_ONLY.pdf - Simple signature only")
    print("\n🔍 Check all three files - at least one should show the signature!")
    
    return True

if __name__ == "__main__":
    enhanced_signature_test()