#!/usr/bin/env python3
"""
Create a demonstration showing the improved Section 5 positioning
"""

import fitz

def create_improved_positioning_demo():
    """Create a visual demonstration of the improved Section 5 positioning"""
    
    print("🎯 Creating improved Section 5 positioning demo...")
    
    # Create a new PDF to show the layout
    doc = fitz.open()
    page = doc.new_page()
    
    # Title
    page.insert_text(
        (50, 50),
        "SECTION 5: ZERO INCOME AFFIDAVIT - IMPROVED POSITIONING",
        fontsize=16,
        color=(0, 0, 0.8)
    )
    
    # Show the improved layout with annotations
    improved_positions = [
        {"name": "Account Holder Name (Affidavit)", "y": 159, "note": "Top of section, full width"},
        {"name": "Household Member Names (No Income)", "y": 264, "note": "Large area for multiple names"},
        {"name": "Affidavit Signature", "y": 332, "note": "Left side of row"},
        {"name": "Printed Name (Affidavit)", "y": 329, "note": "Right side of same row"},
        {"name": "Date (Affidavit)", "y": 379, "note": "Left side of bottom row"},
        {"name": "Telephone (Affidavit)", "y": 379, "note": "Right side of bottom row"}
    ]
    
    y_start = 100
    for i, field in enumerate(improved_positions):
        y_pos = y_start + i * 25
        
        # Field name
        page.insert_text(
            (60, y_pos),
            f"✓ {field['name']}",
            fontsize=11,
            color=(0, 0.6, 0)
        )
        
        # Position info
        page.insert_text(
            (300, y_pos),
            f"Y={field['y']} - {field['note']}",
            fontsize=9,
            color=(0.5, 0.5, 0.5)
        )
    
    # Add visual representation
    y_visual_start = 300
    page.insert_text(
        (60, y_visual_start),
        "Visual Layout on Page 5:",
        fontsize=14,
        color=(0, 0, 0.8)
    )
    
    # Draw boxes representing the field positions (scaled down)
    scale_factor = 0.3
    base_x = 100
    
    field_boxes = [
        {"name": "Account Holder", "x": 80, "y": 159, "w": 250, "h": 25, "color": (0.8, 0.9, 1.0)},
        {"name": "Household Members", "x": 80, "y": 264, "w": 450, "h": 80, "color": (0.9, 0.8, 1.0)},
        {"name": "Signature", "x": 80, "y": 332, "w": 200, "h": 30, "color": (1.0, 0.9, 0.8)},
        {"name": "Printed Name", "x": 300, "y": 329, "w": 230, "h": 25, "color": (1.0, 0.9, 0.8)},
        {"name": "Date", "x": 80, "y": 379, "w": 150, "h": 25, "color": (0.8, 1.0, 0.9)},
        {"name": "Telephone", "x": 280, "y": 379, "w": 150, "h": 25, "color": (0.8, 1.0, 0.9)}
    ]
    
    for box in field_boxes:
        # Scale and position the box
        scaled_x = base_x + (box["x"] - 80) * scale_factor
        scaled_y = y_visual_start + 40 + (box["y"] - 150) * scale_factor
        scaled_w = box["w"] * scale_factor
        scaled_h = box["h"] * scale_factor
        
        # Draw the field box
        rect = fitz.Rect(scaled_x, scaled_y, scaled_x + scaled_w, scaled_y + scaled_h)
        page.draw_rect(rect, color=box["color"], fill=True)
        page.draw_rect(rect, color=(0, 0, 0), width=1)
        
        # Add field label
        page.insert_text(
            (scaled_x + 2, scaled_y + scaled_h - 2),
            box["name"],
            fontsize=7,
            color=(0, 0, 0)
        )
    
    # Add positioning summary
    summary_y = y_visual_start + 200
    page.insert_text(
        (60, summary_y),
        "✅ Positioning Improvements:",
        fontsize=12,
        color=(0, 0.6, 0)
    )
    
    improvements = [
        "• Better vertical spacing between fields",
        "• Signature and Printed Name on same row",
        "• Date and Telephone on same row",
        "• Larger area for household member names",
        "• Consistent left alignment at X=80",
        "• Professional form layout"
    ]
    
    for i, improvement in enumerate(improvements):
        page.insert_text(
            (80, summary_y + 20 + i * 15),
            improvement,
            fontsize=10,
            color=(0, 0, 0)
        )
    
    # Save the demo
    output_path = "Section5_Improved_Positioning_Demo.pdf"
    doc.save(output_path)
    doc.close()
    
    print(f"✅ Created positioning demo: {output_path}")
    return output_path

def main():
    """Create the improved positioning demonstration"""
    
    print("="*60)
    print("🎯 SECTION 5 IMPROVED POSITIONING DEMO")
    print("="*60)
    
    demo_file = create_improved_positioning_demo()
    
    print(f"\n📄 Files available:")
    print(f"1. {demo_file} - Visual layout explanation")
    print(f"2. uploads/completed_test_section5_001_Test_Section5_Demo.pdf - Working PDF with improved positions")
    
    print(f"\n✅ Section 5 positioning improvements:")
    print(f"   - Fields now properly spaced on page 5")
    print(f"   - Better vertical layout (Y=159 to Y=379)")
    print(f"   - Logical grouping of related fields")
    print(f"   - Professional form appearance")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Download the working PDF to see Section 5 on page 5")
    print(f"   2. Fields should now be better positioned and easier to read")
    print(f"   3. Section 5 layout matches professional form standards")

if __name__ == "__main__":
    main()