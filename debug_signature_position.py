#\!/usr/bin/env python3
"""
Debug signature positioning by drawing markers at field boundaries
"""

import fitz
import os

def debug_signature_position():
    """Add visual markers to see where the signature field actually is"""
    
    print("🔧 Debugging Signature Position")
    print("=" * 50)
    
    # Open the PDF
    doc = fitz.open('homeworks.pdf')
    page = doc[2]  # Page 3
    
    # Find the signature field
    widgets = list(page.widgets())
    signature_widget = None
    
    for widget in widgets:
        if widget.field_name == 'signature3':
            signature_widget = widget
            break
    
    if not signature_widget:
        print("❌ Signature field not found")
        return
    
    rect = signature_widget.rect
    print(f"📍 Signature field coordinates:")
    print(f"   Top-left: ({rect.x0}, {rect.y0})")
    print(f"   Bottom-right: ({rect.x1}, {rect.y1})")
    print(f"   Width: {rect.width}, Height: {rect.height}")
    
    # Draw a red rectangle around the signature field boundaries
    page.draw_rect(rect, color=(1, 0, 0), width=2)  # Red border
    
    # Draw markers at the corners
    # Top-left corner
    page.insert_text((rect.x0 - 10, rect.y0), "TL", fontsize=8, color=(1, 0, 0))
    
    # Top-right corner
    page.insert_text((rect.x1 + 2, rect.y0), "TR", fontsize=8, color=(1, 0, 0))
    
    # Bottom-left corner
    page.insert_text((rect.x0 - 10, rect.y1), "BL", fontsize=8, color=(1, 0, 0))
    
    # Bottom-right corner
    page.insert_text((rect.x1 + 2, rect.y1), "BR", fontsize=8, color=(1, 0, 0))
    
    # Add center marker
    center_x = rect.x0 + rect.width/2
    center_y = rect.y0 + rect.height/2
    page.insert_text((center_x, center_y), "CENTER", fontsize=6, color=(0, 0, 1))
    
    # Test different signature positions
    test_positions = [
        ("TOP", rect.x0 + 5, rect.y0 + 2),
        ("MID", rect.x0 + 5, rect.y0 + rect.height/2),
        ("BOT", rect.x0 + 5, rect.y1 - 2),
        ("CURRENT", rect.x0 + 5, rect.y0 + (rect.height * 0.8))
    ]
    
    for label, x, y in test_positions:
        page.insert_text((x, y), f"{label}: Test", fontsize=8, color=(0, 0.5, 0))
    
    # Save debug PDF
    output_path = "debug_signature_position.pdf"
    doc.save(output_path)
    doc.close()
    
    print(f"✅ Debug PDF saved: {output_path}")
    print("📋 Check the PDF to see:")
    print("   - Red rectangle shows actual field boundaries")
    print("   - TL/TR/BL/BR mark the corners")
    print("   - GREEN text shows test positions")
    print("   - Compare with where signature currently appears")

if __name__ == "__main__":
    debug_signature_position()
EOF < /dev/null