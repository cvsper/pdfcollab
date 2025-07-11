#!/usr/bin/env python3
"""
Ultimate signature test - check if the PDF form fields are actually writable
"""

import os
import sys
import fitz

def test_pdf_form_capabilities():
    """Test if the PDF form fields can actually hold values"""
    
    print("🔍 ULTIMATE SIGNATURE TEST - PDF FORM CAPABILITIES")
    print("=" * 60)
    
    try:
        pdf_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        
        # Test 1: Check if form fields are fillable
        print("📋 Test 1: Form field analysis")
        doc = fitz.open(pdf_path)
        page = doc[2]  # Page 3
        
        widgets = list(page.widgets())
        
        # Find signature widgets
        signature_widgets = []
        for widget in widgets:
            if widget.field_name in ['signature3', 'property_ower_sig3']:
                signature_widgets.append(widget)
                
        print(f"Found {len(signature_widgets)} signature widgets:")
        
        for widget in signature_widgets:
            print(f"\n🖋️  Widget: {widget.field_name}")
            print(f"   Type: {widget.field_type}")
            print(f"   Flags: {widget.field_flags}")
            print(f"   Current value: '{widget.field_value}'")
            print(f"   Read-only: {bool(widget.field_flags & 1)}")  # Check read-only flag
            
            # Check widget properties
            rect = widget.rect
            print(f"   Position: ({rect.x0}, {rect.y0}) to ({rect.x1}, {rect.y1})")
            print(f"   Size: {rect.width} x {rect.height}")
            
        doc.close()
        
        # Test 2: Try to fill and save immediately
        print(f"\n📋 Test 2: Fill and save immediately")
        doc = fitz.open(pdf_path)
        page = doc[2]
        widgets = list(page.widgets())
        
        filled_count = 0
        for widget in widgets:
            if widget.field_name == 'signature3':
                print(f"🖋️  Filling Applicant signature...")
                widget.field_value = "APPLICANT TEST SIGNATURE"
                widget.update()
                filled_count += 1
                print(f"   ✅ Set to: '{widget.field_value}'")
                
            elif widget.field_name == 'property_ower_sig3':
                print(f"🖋️  Filling Property Owner signature...")
                widget.field_value = "PROPERTY OWNER TEST SIGNATURE"  
                widget.update()
                filled_count += 1
                print(f"   ✅ Set to: '{widget.field_value}'")
        
        # Save immediately without any other processing
        output_path1 = os.path.join(os.path.dirname(__file__), 'IMMEDIATE_SAVE_TEST.pdf')
        doc.save(output_path1)
        doc.close()
        
        print(f"✅ Saved immediately to: {output_path1}")
        print(f"   Filled {filled_count} signature fields")
        
        # Test 3: Open the saved file and check if values persisted
        print(f"\n📋 Test 3: Check if values persisted")
        doc2 = fitz.open(output_path1)
        page2 = doc2[2]
        widgets2 = list(page2.widgets())
        
        for widget in widgets2:
            if widget.field_name in ['signature3', 'property_ower_sig3']:
                print(f"🔍 {widget.field_name}: '{widget.field_value}'")
                if widget.field_value:
                    print(f"   ✅ Value persisted!")
                else:
                    print(f"   ❌ Value was lost!")
        
        doc2.close()
        
        # Test 4: Try flattening the PDF (making form fields permanent)
        print(f"\n📋 Test 4: Try flattening PDF")
        doc = fitz.open(pdf_path)
        page = doc[2]
        widgets = list(page.widgets())
        
        # Fill the fields again
        for widget in widgets:
            if widget.field_name == 'signature3':
                widget.field_value = "FLATTENED APPLICANT SIGNATURE"
                widget.update()
            elif widget.field_name == 'property_ower_sig3':
                widget.field_value = "FLATTENED PROPERTY OWNER SIGNATURE"
                widget.update()
        
        # Try to flatten (make form fields permanent)
        try:
            # Method 1: Convert to image and back
            output_path2 = os.path.join(os.path.dirname(__file__), 'FLATTENED_TEST.pdf')
            
            new_doc = fitz.open()
            for page_num in range(len(doc)):
                old_page = doc[page_num]
                
                # Convert to image at high resolution
                mat = fitz.Matrix(2, 2)  # 2x scale
                pix = old_page.get_pixmap(matrix=mat)
                
                # Create new page from image
                new_page = new_doc.new_page(width=old_page.rect.width, height=old_page.rect.height)
                new_page.insert_image(new_page.rect, pixmap=pix)
            
            new_doc.save(output_path2)
            new_doc.close()
            doc.close()
            
            print(f"✅ Flattened PDF saved to: {output_path2}")
            
        except Exception as e:
            print(f"❌ Flattening failed: {e}")
            doc.close()
        
        # Test 5: Try the simplest possible approach
        print(f"\n📋 Test 5: Simplest possible approach")
        
        doc = fitz.open(pdf_path)
        
        # Fill ALL text fields with visible content
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            for widget in widgets:
                if widget.field_type == 7:  # Text field
                    if widget.field_name == 'signature3':
                        widget.field_value = "SIMPLE APPLICANT SIG"
                        widget.update()
                        print(f"   ✅ Set {widget.field_name} = 'SIMPLE APPLICANT SIG'")
                    elif widget.field_name == 'property_ower_sig3':
                        widget.field_value = "SIMPLE PROPERTY OWNER SIG"
                        widget.update()
                        print(f"   ✅ Set {widget.field_name} = 'SIMPLE PROPERTY OWNER SIG'")
                    elif widget.field_name in ['first_name2', 'last_name2', 'property_address1']:
                        widget.field_value = f"TEST_{widget.field_name}"
                        widget.update()
                        print(f"   ✅ Set {widget.field_name} = 'TEST_{widget.field_name}'")
        
        output_path3 = os.path.join(os.path.dirname(__file__), 'SIMPLE_APPROACH_TEST.pdf')
        doc.save(output_path3)
        doc.close()
        
        print(f"✅ Simple approach saved to: {output_path3}")
        
        # Summary
        print(f"\n📊 SUMMARY - Files created:")
        print(f"   1. {output_path1} - Immediate save after filling")
        print(f"   2. {output_path2} - Flattened PDF (image conversion)")
        print(f"   3. {output_path3} - Simple approach with multiple fields")
        
        print(f"\n💡 CHECK THESE FILES:")
        print(f"   • If NONE show signatures: PDF form fields don't work")
        print(f"   • If #1 shows signatures: Our complex processing is breaking it")
        print(f"   • If #2 shows signatures: We need to flatten PDFs")
        print(f"   • If #3 shows other fields but not signatures: Signature fields are special")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in ultimate signature test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = test_pdf_form_capabilities()
    
    print(f"\n📊 ULTIMATE TEST RESULTS:")
    print(f"   Test completed: {'✅ YES' if success else '❌ NO'}")

if __name__ == "__main__":
    main()