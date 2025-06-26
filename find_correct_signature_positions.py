#!/usr/bin/env python3
"""
Find the exact correct positions for signatures by analyzing the PDF
"""

import fitz
from pdf_processor import PDFProcessor

def find_correct_signature_positions():
    """Analyze the PDF to find where signatures should actually go"""
    print("🔍 FINDING CORRECT SIGNATURE POSITIONS")
    print("=" * 60)
    
    doc = fitz.open('homeworks.pdf')
    
    # Look for signature-related text and fields
    signature_locations = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        print(f"\n📄 PAGE {page_num + 1} ANALYSIS:")
        print("-" * 30)
        
        # Method 1: Find widgets (form fields)
        widgets = list(page.widgets())
        print(f"Found {len(widgets)} form widgets")
        
        for widget in widgets:
            field_name = widget.field_name
            if field_name and ('sig' in field_name.lower() or 'sign' in field_name.lower()):
                rect = widget.rect
                signature_locations.append({
                    'type': 'widget',
                    'name': field_name,
                    'page': page_num,
                    'position': (rect.x0, rect.y0),
                    'size': (rect.width, rect.height),
                    'description': f"Form field '{field_name}'"
                })
                print(f"   ✍️  SIGNATURE WIDGET: {field_name}")
                print(f"      Position: ({rect.x0:.1f}, {rect.y0:.1f})")
                print(f"      Size: {rect.width:.1f} x {rect.height:.1f}")
        
        # Method 2: Search for signature-related text
        text_dict = page.get_text("dict")
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        text = span.get("text", "").lower()
                        if any(keyword in text for keyword in ["signature", "sign here", "applicant", "tenant", "owner"]):
                            bbox = span.get("bbox", [0, 0, 0, 0])
                            signature_locations.append({
                                'type': 'text',
                                'name': span.get("text", ""),
                                'page': page_num,
                                'position': (bbox[0], bbox[1]),
                                'size': (bbox[2] - bbox[0], bbox[3] - bbox[1]),
                                'description': f"Text: '{span.get('text', '')}'"
                            })
                            print(f"   📝 SIGNATURE TEXT: '{span.get('text', '')}'")
                            print(f"      Position: ({bbox[0]:.1f}, {bbox[1]:.1f})")
        
        # Method 3: Look for lines that might indicate signature areas
        drawings = page.get_drawings()
        for drawing in drawings:
            for item in drawing.get("items", []):
                if item[0] == "l":  # Line
                    # Check if it's a horizontal line (potential signature line)
                    p1, p2 = item[1], item[2]
                    if abs(p1.y - p2.y) < 5 and abs(p1.x - p2.x) > 50:  # Horizontal line > 50 pts
                        signature_locations.append({
                            'type': 'line',
                            'name': 'Signature line',
                            'page': page_num,
                            'position': (min(p1.x, p2.x), p1.y),
                            'size': (abs(p2.x - p1.x), 2),
                            'description': f"Horizontal line from ({p1.x:.1f}, {p1.y:.1f}) to ({p2.x:.1f}, {p2.y:.1f})"
                        })
                        print(f"   📏 SIGNATURE LINE: ({p1.x:.1f}, {p1.y:.1f}) to ({p2.x:.1f}, {p2.y:.1f})")
    
    doc.close()
    
    # Summarize findings
    print(f"\n📊 SIGNATURE LOCATIONS FOUND: {len(signature_locations)}")
    print("=" * 60)
    
    for i, loc in enumerate(signature_locations):
        print(f"{i+1}. {loc['description']}")
        print(f"   Page: {loc['page'] + 1}, Position: ({loc['position'][0]:.1f}, {loc['position'][1]:.1f})")
    
    return signature_locations

def create_precise_signature_placement(signature_locations):
    """Create a PDF with signatures placed at the correct identified locations"""
    print(f"\n🎯 CREATING PRECISE SIGNATURE PLACEMENT")
    print("-" * 40)
    
    doc = fitz.open('homeworks.pdf')
    
    signature_text = "James deen"
    
    # Place signature at each identified location
    for i, loc in enumerate(signature_locations):
        page_num = loc['page']
        x, y = loc['position']
        
        if page_num < len(doc):
            page = doc[page_num]
            
            # Adjust position based on type
            if loc['type'] == 'widget':
                # For form widgets, place text slightly above the widget
                y_offset = y + loc['size'][1] - 2
                color = (0, 0, 0)  # Black
                prefix = ""
            elif loc['type'] == 'text':
                # For text indicators, place signature nearby
                y_offset = y + 15
                color = (0, 0, 0.8)  # Blue
                prefix = ""
            elif loc['type'] == 'line':
                # For signature lines, place text slightly above the line
                y_offset = y - 3
                color = (0, 0, 0)  # Black
                prefix = ""
            
            # Insert signature text
            page.insert_text(
                (x + 2, y_offset),
                f"{prefix}{signature_text}",
                fontsize=12,
                color=color
            )
            
            print(f"   ✍️  Placed signature at location {i+1}: ({x:.1f}, {y_offset:.1f}) - {loc['description']}")
    
    # Save the precisely placed signature PDF
    output_path = 'PRECISE_SIGNATURE_PLACEMENT.pdf'
    doc.save(output_path)
    doc.close()
    
    print(f"\n✅ Created: {output_path}")
    print("📍 Signatures placed at all identified locations")
    
    return output_path

if __name__ == "__main__":
    signature_locations = find_correct_signature_positions()
    if signature_locations:
        create_precise_signature_placement(signature_locations)
    else:
        print("❌ No signature locations found")