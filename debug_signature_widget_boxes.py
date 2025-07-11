#!/usr/bin/env python3
"""
Debug signature positioning by drawing boxes around widget areas
"""

import os
import sys
import fitz  # PyMuPDF

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def create_widget_debug_pdf():
    """Create a PDF with visible boxes around all widgets to debug positioning"""
    
    print("🔍 CREATING WIDGET DEBUG PDF WITH BOXES")
    print("=" * 60)
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        try:
            from embedded_homworks import save_homworks_pdf_to_file
            save_homworks_pdf_to_file(homeworks_path)
            print("✅ Using embedded homworks.pdf")
        except ImportError:
            print(f"❌ Error: {homeworks_path} not found")
            return False
    
    try:
        # Open the PDF
        doc = fitz.open(homeworks_path)
        
        signature_widgets = []
        
        print(f"📄 Analyzing {len(doc)} pages for widgets...")
        
        # Process each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            print(f"\n📋 Page {page_num + 1}: Found {len(widgets)} widgets")
            
            for i, widget in enumerate(widgets):
                field_name = widget.field_name
                rect = widget.rect
                field_type = widget.field_type_string
                
                # Draw a box around every widget
                if rect:
                    # Red box for signature fields, blue for others
                    if 'signature' in field_name.lower():
                        box_color = (1, 0, 0)  # Red
                        signature_widgets.append({
                            'name': field_name,
                            'rect': rect,
                            'page': page_num + 1,
                            'type': field_type
                        })
                        print(f"   🖋️  SIGNATURE: {field_name}")
                    else:
                        box_color = (0, 0, 1)  # Blue
                    
                    # Draw rectangle around widget
                    page.draw_rect(rect, color=box_color, width=2)
                    
                    # Add label with field name
                    label_rect = fitz.Rect(rect.x0, rect.y0 - 15, rect.x1, rect.y0)
                    page.draw_rect(label_rect, color=(1, 1, 0), fill=(1, 1, 0))  # Yellow background
                    
                    # Add text label
                    page.insert_text(
                        (rect.x0 + 2, rect.y0 - 2),
                        f"{field_name} ({rect.x0:.0f},{rect.y0:.0f})",
                        fontsize=8,
                        color=(0, 0, 0)
                    )
                    
                    print(f"   📦 {field_name}: ({rect.x0:.1f}, {rect.y0:.1f}, {rect.x1:.1f}, {rect.y1:.1f})")
        
        # Save the debug PDF
        output_path = os.path.join(os.path.dirname(__file__), 'WIDGET_DEBUG_WITH_BOXES.pdf')
        doc.save(output_path)
        doc.close()
        
        print(f"\n🎉 WIDGET DEBUG PDF CREATED!")
        print(f"📄 File: {output_path}")
        print(f"📄 Size: {os.path.getsize(output_path):,} bytes")
        
        print(f"\n🖋️  SIGNATURE WIDGET DETAILS:")
        for sig in signature_widgets:
            print(f"   📝 {sig['name']} (Page {sig['page']})")
            print(f"      Rect: ({sig['rect'].x0:.1f}, {sig['rect'].y0:.1f}, {sig['rect'].x1:.1f}, {sig['rect'].y1:.1f})")
            print(f"      Size: {sig['rect'].width:.1f} x {sig['rect'].height:.1f}")
            print(f"      Type: {sig['type']}")
            print(f"      Center: ({sig['rect'].x0 + sig['rect'].width/2:.1f}, {sig['rect'].y0 + sig['rect'].height/2:.1f})")
        
        print(f"\n🔍 IN THE DEBUG PDF:")
        print(f"   🔴 RED BOXES = Signature fields")
        print(f"   🔵 BLUE BOXES = Other form fields")
        print(f"   🟡 YELLOW LABELS = Field names and coordinates")
        
        print(f"\n💡 Use this to see:")
        print(f"   • Where signature widgets are actually located")
        print(f"   • How far off your signatures are from the boxes")
        print(f"   • What the correct target coordinates should be")
        
        return True, signature_widgets
        
    except Exception as e:
        print(f"❌ Error creating widget debug PDF: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def create_signature_positioning_test_with_boxes():
    """Create a test with both widget boxes AND signature placement"""
    
    print(f"\n🧪 CREATING COMBINED TEST: WIDGET BOXES + SIGNATURES")
    print("=" * 60)
    
    try:
        from pdf_processor import PDFProcessor
        
        homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        processor = PDFProcessor()
        
        # Test data
        test_user1_data = {
            'first_name': 'WIDGET',
            'last_name': 'BOX-TEST',
            'property_address': 'Widget Box Test Street'
        }
        
        test_user2_data = {
            'name': 'WIDGET BOX-TEST',
            'email': 'widget@boxtest.com',
            'applicant_signature': 'WIDGET BOX APPLICANT SIGNATURE',
            'authorization_date': '2025-07-11',
            'owner_signature': 'WIDGET BOX OWNER SIGNATURE',
            'owner_signature_date': '2025-07-11'
        }
        
        # Extract and map fields
        field_analysis = processor.extract_fields_with_pymupdf(homeworks_path)
        if "error" in field_analysis:
            print(f"❌ Error: {field_analysis['error']}")
            return False
        
        pdf_fields = field_analysis.get('fields', [])
        
        # Apply basic field mapping
        for field in pdf_fields:
            field['assigned_to'] = 'user1'
            field['value'] = ''
            field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
            
            if field['name'] == 'Applicant Signature':
                field['value'] = test_user2_data['applicant_signature']
                field['type'] = 'signature'
                field['assigned_to'] = 'user2'
            elif field['name'] == 'Property Owner Signature':
                field['value'] = test_user2_data['owner_signature']
                field['type'] = 'signature'
                field['assigned_to'] = 'user2'
            elif field['name'] == 'First Name':
                field['value'] = test_user1_data['first_name']
            elif field['name'] == 'Last Name':
                field['value'] = test_user1_data['last_name']
            elif field['name'] == 'Property Address':
                field['value'] = test_user1_data['property_address']
        
        # Create document structure
        document = {
            'user1_data': test_user1_data,
            'user2_data': test_user2_data,
            'pdf_fields': pdf_fields,
            'file_path': homeworks_path
        }
        
        # Generate the combined test PDF
        output_path = os.path.join(os.path.dirname(__file__), 'SIGNATURE_WITH_WIDGET_BOXES_TEST.pdf')
        
        print(f"🔧 Generating combined widget boxes + signatures test...")
        success = processor.fill_pdf_with_force_visible(homeworks_path, document, output_path)
        
        if success:
            # Now add widget boxes to the filled PDF
            doc = fitz.open(output_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = list(page.widgets())
                
                for widget in widgets:
                    field_name = widget.field_name
                    rect = widget.rect
                    
                    if rect:
                        # Draw boxes around widgets
                        if 'signature' in field_name.lower():
                            # Thick red box for signature fields
                            page.draw_rect(rect, color=(1, 0, 0), width=3)
                            
                            # Add detailed info for signatures
                            info_text = f"SIGNATURE WIDGET: {field_name}\\nRect: ({rect.x0:.0f},{rect.y0:.0f}) to ({rect.x1:.0f},{rect.y1:.0f})\\nSize: {rect.width:.0f}x{rect.height:.0f}"
                            info_rect = fitz.Rect(rect.x0, rect.y1 + 5, rect.x0 + 200, rect.y1 + 40)
                            page.draw_rect(info_rect, color=(1, 1, 0), fill=(1, 1, 0))
                            page.insert_text(
                                (rect.x0 + 2, rect.y1 + 15),
                                info_text,
                                fontsize=8,
                                color=(0, 0, 0)
                            )
                        else:
                            # Thin blue box for other fields
                            page.draw_rect(rect, color=(0, 0, 1), width=1)
            
            doc.save(output_path)
            doc.close()
            
            print(f"\n🎉 COMBINED TEST CREATED!")
            print(f"✅ File: {output_path}")
            print(f"📄 Size: {os.path.getsize(output_path):,} bytes")
            
            print(f"\n🔍 WHAT TO LOOK FOR:")
            print(f"   🔴 RED THICK BOXES = Signature widget boundaries")
            print(f"   🔵 BLUE THIN BOXES = Other form field boundaries")
            print(f"   🖋️  SIGNATURE TEXT = Where signatures are actually placed")
            print(f"   🟡 YELLOW INFO = Widget details and coordinates")
            
            print(f"\n📏 CHECK IF:")
            print(f"   • Signature text is INSIDE the red boxes")
            print(f"   • Signature text orientation is correct")
            print(f"   • Signature text is readable (not upside down/backwards)")
            
            return True
        else:
            print(f"❌ Failed to create combined test")
            return False
            
    except Exception as e:
        print(f"❌ Error creating combined test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Widget Debug with Boxes")
    print("Creating visual debug tools to see signature widget boundaries")
    print()
    
    # Step 1: Create widget debug PDF with boxes
    debug_success, signature_widgets = create_widget_debug_pdf()
    
    # Step 2: Create combined test with filled signatures AND widget boxes
    if debug_success:
        combined_success = create_signature_positioning_test_with_boxes()
    else:
        combined_success = False
    
    print(f"\n📊 DEBUG SESSION RESULTS:")
    print(f"   Widget debug PDF: {'✅ CREATED' if debug_success else '❌ FAILED'}")
    print(f"   Combined test PDF: {'✅ CREATED' if combined_success else '❌ FAILED'}")
    
    if debug_success:
        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Open WIDGET_DEBUG_WITH_BOXES.pdf")
        print(f"   2. Find the red signature widget boxes")
        print(f"   3. Note the exact coordinates where signatures should go")
        print(f"   4. Open SIGNATURE_WITH_WIDGET_BOXES_TEST.pdf") 
        print(f"   5. Compare where signatures appear vs widget boxes")
        print(f"   6. Provide the correct coordinates for adjustment")
        
        if signature_widgets:
            print(f"\n📍 SIGNATURE WIDGET COORDINATES FOUND:")
            for sig in signature_widgets:
                print(f"   🖋️  {sig['name']}:")
                print(f"      Top-left: ({sig['rect'].x0:.0f}, {sig['rect'].y0:.0f})")
                print(f"      Bottom-right: ({sig['rect'].x1:.0f}, {sig['rect'].y1:.0f})")
                print(f"      Center: ({sig['rect'].x0 + sig['rect'].width/2:.0f}, {sig['rect'].y0 + sig['rect'].height/2:.0f})")

if __name__ == "__main__":
    main()