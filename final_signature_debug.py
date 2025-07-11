#!/usr/bin/env python3
"""
Final comprehensive signature debug - test every aspect of signature rendering
"""

import os
import sys
import fitz

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_direct_signature_rendering():
    """Test direct signature rendering without any complex processing"""
    
    print("🔍 FINAL SIGNATURE DEBUG - DIRECT RENDERING TEST")
    print("=" * 60)
    
    try:
        pdf_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        output_path = os.path.join(os.path.dirname(__file__), 'FINAL_SIGNATURE_TEST.pdf')
        
        print(f"📄 Source PDF: {pdf_path}")
        print(f"📄 Output PDF: {output_path}")
        
        # Open the PDF
        doc = fitz.open(pdf_path)
        print(f"✅ Opened PDF with {len(doc)} pages")
        
        # Go to page 3 (where signature fields are)
        page = doc[2]  # Page 3 (0-indexed)
        
        # Test 1: Add signature at known Applicant Signature location
        applicant_x, applicant_y = 66, 152
        applicant_text = "APPLICANT SIGNATURE TEST"
        
        print(f"🖋️  Test 1: Adding Applicant signature at ({applicant_x}, {applicant_y})")
        page.insert_text(
            (applicant_x, applicant_y),
            applicant_text,
            fontsize=12,
            color=(1, 0, 0),  # RED for visibility
            fontname="helv"
        )
        
        # Test 2: Add signature at known Property Owner location
        owner_x, owner_y = 369, 622
        owner_text = "PROPERTY OWNER SIGNATURE TEST"
        
        print(f"🖋️  Test 2: Adding Property Owner signature at ({owner_x}, {owner_y})")
        page.insert_text(
            (owner_x, owner_y),
            owner_text,
            fontsize=12,
            color=(0, 0, 1),  # BLUE for visibility
            fontname="helv"
        )
        
        # Test 3: Add signatures at widget locations for comparison
        print("🖋️  Test 3: Adding signatures at actual widget locations...")
        
        widgets = list(page.widgets())
        for widget in widgets:
            if widget.field_name and 'signature' in widget.field_name.lower():
                rect = widget.rect
                widget_x = rect.x0 + 10
                widget_y = rect.y0 + 10
                
                page.insert_text(
                    (widget_x, widget_y),
                    f"WIDGET: {widget.field_name}",
                    fontsize=8,
                    color=(0, 1, 0),  # GREEN for widget locations
                    fontname="helv"
                )
                print(f"   ✅ Added widget marker at ({widget_x}, {widget_y}) for {widget.field_name}")
        
        # Test 4: Add large visible text in multiple locations to test rendering
        test_locations = [
            (100, 100, "TOP LEFT TEST"),
            (300, 300, "CENTER TEST"),
            (100, 700, "BOTTOM LEFT TEST"),
            (400, 400, "MIDDLE RIGHT TEST")
        ]
        
        print("🖋️  Test 4: Adding large visible text at multiple locations...")
        for x, y, text in test_locations:
            page.insert_text(
                (x, y),
                text,
                fontsize=16,
                color=(1, 0, 1),  # MAGENTA for high visibility
                fontname="helv"
            )
            print(f"   ✅ Added test text '{text}' at ({x}, {y})")
        
        # Test 5: Try different text transformation matrices
        print("🖋️  Test 5: Testing different text orientations...")
        
        # Normal text
        page.insert_text(
            (200, 200),
            "NORMAL TEXT",
            fontsize=14,
            color=(0, 0, 0),
            fontname="helv"
        )
        
        # Text with matrix transformation (like we use for signatures)
        try:
            page.insert_text(
                (200, 230),
                "MATRIX TRANSFORMED TEXT",
                fontsize=14,
                color=(0.5, 0.5, 0),
                morph=(fitz.Point(200, 230), fitz.Matrix(1, 0, 0, -1, 0, 0))
            )
            print("   ✅ Matrix transformation text added")
        except Exception as e:
            print(f"   ❌ Matrix transformation failed: {e}")
        
        # Save the PDF
        doc.save(output_path)
        doc.close()
        
        file_size = os.path.getsize(output_path)
        print(f"\n✅ FINAL TEST PDF CREATED: {output_path}")
        print(f"📊 File size: {file_size:,} bytes")
        
        print(f"\n🔍 WHAT TO CHECK IN THE PDF:")
        print(f"   🔴 RED text: Applicant signature location ({applicant_x}, {applicant_y})")
        print(f"   🔵 BLUE text: Property Owner signature location ({owner_x}, {owner_y})")
        print(f"   🟢 GREEN text: Actual widget locations")
        print(f"   🟣 MAGENTA text: General visibility test locations")
        print(f"   ⚫ BLACK text: Normal text rendering")
        print(f"   🟤 BROWN text: Matrix transformed text")
        
        print(f"\n💡 ANALYSIS:")
        print(f"   • If NO text appears: PDF rendering is fundamentally broken")
        print(f"   • If SOME text appears: Check which colors/locations work")
        print(f"   • If MAGENTA text appears but RED/BLUE don't: Coordinate issue")
        print(f"   • If normal text works but matrix text doesn't: Transformation issue")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in final signature debug: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_widget_analysis():
    """Analyze the signature widget locations and properties"""
    
    print("\n" + "=" * 60)
    print("🔍 WIDGET ANALYSIS")
    print("=" * 60)
    
    try:
        pdf_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        doc = fitz.open(pdf_path)
        page = doc[2]  # Page 3
        
        widgets = list(page.widgets())
        signature_widgets = []
        
        for widget in widgets:
            if widget.field_name and 'signature' in widget.field_name.lower():
                signature_widgets.append(widget)
        
        print(f"📊 Found {len(signature_widgets)} signature widgets:")
        
        for i, widget in enumerate(signature_widgets, 1):
            rect = widget.rect
            print(f"\n🖋️  Signature Widget {i}:")
            print(f"   Field Name: {widget.field_name}")
            print(f"   Field Type: {widget.field_type}")
            print(f"   Rectangle: ({rect.x0:.1f}, {rect.y0:.1f}) to ({rect.x1:.1f}, {rect.y1:.1f})")
            print(f"   Width: {rect.width:.1f}, Height: {rect.height:.1f}")
            print(f"   Current Value: '{widget.field_value}'")
            
            # Test if we can write to this widget
            try:
                original_value = widget.field_value
                widget.field_value = "TEST SIGNATURE"
                widget.update()
                print(f"   ✅ Widget accepts text input")
                
                # Restore original value
                widget.field_value = original_value
                widget.update()
            except Exception as e:
                print(f"   ❌ Widget text input failed: {e}")
        
        doc.close()
        return True
        
    except Exception as e:
        print(f"❌ Error in widget analysis: {e}")
        return False

def main():
    """Main function"""
    print("🏠 PDF Collaborator - FINAL SIGNATURE DEBUG")
    print("This will test every aspect of signature rendering")
    print()
    
    # Test 1: Direct rendering
    success1 = test_direct_signature_rendering()
    
    # Test 2: Widget analysis
    success2 = test_widget_analysis()
    
    print(f"\n📊 FINAL DEBUG RESULTS:")
    print(f"   Direct rendering test: {'✅ COMPLETED' if success1 else '❌ FAILED'}")
    print(f"   Widget analysis test: {'✅ COMPLETED' if success2 else '❌ FAILED'}")
    
    if success1:
        print(f"\n🎯 CRITICAL TEST FILE CREATED:")
        print(f"   📄 FINAL_SIGNATURE_TEST.pdf")
        print(f"   🔍 Check this file to see if ANY text is visible")
        print(f"   📋 This will tell us if the issue is rendering or positioning")

if __name__ == "__main__":
    main()