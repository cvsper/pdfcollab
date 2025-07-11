#!/usr/bin/env python3
"""
Test both signature widgets directly
"""

import os
import sys
import fitz

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_both_signature_widgets():
    """Test both signature widgets directly"""
    
    print("🔍 TESTING BOTH SIGNATURE WIDGETS DIRECTLY")
    print("=" * 60)
    
    try:
        pdf_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        output_path = os.path.join(os.path.dirname(__file__), 'BOTH_SIGNATURES_TEST.pdf')
        
        # Open PDF
        doc = fitz.open(pdf_path)
        page = doc[2]  # Page 3
        
        # Method 1: Use form field filling
        print("📋 Method 1: Form field filling")
        widgets = list(page.widgets())
        
        for widget in widgets:
            if widget.field_name == 'signature3':
                print(f"🖋️  Found Applicant signature widget: {widget.field_name}")
                widget.field_value = "APPLICANT FORM FIELD TEST"
                widget.update()
                print(f"   ✅ Set form field value")
                
            elif widget.field_name == 'property_ower_sig3':
                print(f"🖋️  Found Property Owner signature widget: {widget.field_name}")
                widget.field_value = "PROPERTY OWNER FORM FIELD TEST"
                widget.update()
                print(f"   ✅ Set form field value")
        
        # Method 2: Direct text insertion at widget locations
        print("\n📋 Method 2: Direct text insertion")
        
        for widget in widgets:
            if widget.field_name == 'signature3':
                rect = widget.rect
                x = rect.x0 + 5
                y = rect.y0 + rect.height - 3
                
                page.insert_text(
                    (x, y),
                    "APPLICANT TEXT OVERLAY",
                    fontsize=10,
                    color=(1, 0, 0),  # RED
                    fontname="helv"
                )
                print(f"   🔴 Added Applicant text overlay at ({x:.1f}, {y:.1f})")
                
            elif widget.field_name == 'property_ower_sig3':
                rect = widget.rect
                x = rect.x0 + 5
                y = rect.y0 + rect.height - 3
                
                page.insert_text(
                    (x, y),
                    "PROPERTY OWNER TEXT OVERLAY",
                    fontsize=10,
                    color=(0, 0, 1),  # BLUE
                    fontname="helv"
                )
                print(f"   🔵 Added Property Owner text overlay at ({x:.1f}, {y:.1f})")
        
        # Method 3: Use our exact coordinates
        print("\n📋 Method 3: Our exact coordinates")
        
        # Applicant signature at our coordinates
        page.insert_text(
            (66, 152),
            "APPLICANT EXACT COORDS",
            fontsize=10,
            color=(0, 1, 0),  # GREEN
            fontname="helv"
        )
        print(f"   🟢 Added Applicant at exact coords (66, 152)")
        
        # Property Owner at our coordinates
        page.insert_text(
            (369, 622),
            "PROPERTY OWNER EXACT COORDS",
            fontsize=10,
            color=(1, 1, 0),  # YELLOW
            fontname="helv"
        )
        print(f"   🟡 Added Property Owner at exact coords (369, 622)")
        
        # Method 4: Test with matrix transformation (like our actual code)
        print("\n📋 Method 4: Matrix transformation (like actual code)")
        
        try:
            page.insert_text(
                (66, 152),
                "APPLICANT MATRIX TEST",
                fontsize=10,
                color=(1, 0, 1),  # MAGENTA
                morph=(fitz.Point(66, 152), fitz.Matrix(1, 0, 0, -1, 0, 0))
            )
            print(f"   🟣 Added Applicant with matrix at (66, 152)")
        except Exception as e:
            print(f"   ❌ Applicant matrix failed: {e}")
        
        try:
            page.insert_text(
                (369, 622),
                "PROPERTY OWNER MATRIX TEST",
                fontsize=10,
                color=(0.5, 0.5, 0.5),  # GRAY
                morph=(fitz.Point(369, 622), fitz.Matrix(1, 0, 0, -1, 0, 0))
            )
            print(f"   ⚫ Added Property Owner with matrix at (369, 622)")
        except Exception as e:
            print(f"   ❌ Property Owner matrix failed: {e}")
        
        # Save and analyze
        doc.save(output_path)
        doc.close()
        
        file_size = os.path.getsize(output_path)
        print(f"\n✅ BOTH SIGNATURES TEST PDF CREATED: {output_path}")
        print(f"📊 File size: {file_size:,} bytes")
        
        print(f"\n🔍 WHAT TO LOOK FOR:")
        print(f"   📝 Form fields: Should show widget field values")
        print(f"   🔴 RED: Applicant text overlay at widget location")
        print(f"   🔵 BLUE: Property Owner text overlay at widget location")
        print(f"   🟢 GREEN: Applicant at our exact coordinates (66, 152)")
        print(f"   🟡 YELLOW: Property Owner at our exact coordinates (369, 622)")
        print(f"   🟣 MAGENTA: Applicant with matrix transformation")
        print(f"   ⚫ GRAY: Property Owner with matrix transformation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing both signatures: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = test_both_signature_widgets()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"   Both signatures test: {'✅ COMPLETED' if success else '❌ FAILED'}")
    
    if success:
        print(f"\n💡 This test will show which rendering method works for signatures!")

if __name__ == "__main__":
    main()