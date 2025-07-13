#!/usr/bin/env python3
"""
Test to understand PDF coordinate system - place indicators at different Y positions
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
import uuid

def test_coordinate_system():
    """Test coordinate system by placing multiple indicators at different Y values"""
    
    print("🔍 TESTING PDF COORDINATE SYSTEM")
    print("=" * 60)
    print("Creating multiple indicators to understand Y coordinate behavior")
    
    # Extract PDF fields
    processor = PDFProcessor()
    pdf_analysis = processor.extract_fields_with_pymupdf('homworks.pdf')
    pdf_fields = pdf_analysis['fields']
    
    # Test data
    form_data = {
        'property_address': 'COORDINATE TEST - 999 Debug Street',
        'dwelling_type': 'apartment',
        'first_name': 'COORDINATE',
        'last_name': 'TEST'
    }
    
    print(f"📝 Testing dwelling_type: {form_data['dwelling_type']}")
    print(f"🔍 Will place indicators at y=5, y=100, y=200, y=400, y=600, y=800")
    
    # Apply basic mappings
    basic_mappings = {
        'property_address': 'property_address1',
        'first_name': 'first_name2',
        'last_name': 'last_name2'
    }
    
    for form_field, pdf_field_name in basic_mappings.items():
        form_value = form_data.get(form_field)
        if form_value:
            for field in pdf_fields:
                if field.get('pdf_field_name') == pdf_field_name or field['name'] == pdf_field_name:
                    field['value'] = str(form_value)
                    field['assigned_to'] = 'user1'
                    print(f"✅ Mapped: {form_field} → {field['name']}")
                    break
    
    # Handle dwelling_type specially
    dwelling_type = form_data.get('dwelling_type')
    if dwelling_type:
        dwelling_mappings = {
            'single_family': 'Single Family Home (Checkbox)',
            'apartment': 'Apartment (Checkbox)', 
            'condominium': 'Condominium (Checkbox)'
        }
        target_field = dwelling_mappings.get(dwelling_type)
        
        if target_field:
            for field in pdf_fields:
                if field['name'] == target_field:
                    field['value'] = 'true'
                    field['assigned_to'] = 'user1'
                    print(f"✅ Dwelling: {dwelling_type} → {field['name']} = true")
                    break
    
    # Create test document
    test_document = {
        'id': str(uuid.uuid4()),
        'pdf_fields': pdf_fields,
        'user1_data': form_data,
        'user2_data': {}
    }
    
    # Temporarily modify the dwelling indicators method to test coordinate system
    # We'll monkey-patch the method to add multiple test indicators
    original_method = processor.add_dwelling_visual_indicators
    
    def test_dwelling_indicators(doc, document):
        """Test method to add multiple indicators at different Y positions"""
        try:
            user1_data = document.get('user1_data', {})
            dwelling_type = user1_data.get('dwelling_type')
            
            if not dwelling_type:
                return
                
            print(f"🔍 Adding COORDINATE TEST indicators at various Y positions")
            
            # Get page 3 where dwelling checkboxes are located
            if len(doc) >= 3:
                page = doc[2]  # Page 3 (0-indexed)
                
                # Test positions at different Y coordinates
                test_positions = [
                    {'y': 5, 'label': 'Y=5 (Should be TOP)'},
                    {'y': 100, 'label': 'Y=100'},
                    {'y': 200, 'label': 'Y=200'},
                    {'y': 400, 'label': 'Y=400'},
                    {'y': 600, 'label': 'Y=600'},
                    {'y': 800, 'label': 'Y=800 (Should be BOTTOM?)'}
                ]
                
                x_base = 50  # Start at left side
                width = 120
                height = 15
                
                for i, pos in enumerate(test_positions):
                    y = pos['y']
                    x = x_base + (i * 130)  # Spread them horizontally too
                    label = pos['label']
                    
                    try:
                        # Add colored rectangle
                        colors = [
                            (1, 0, 0),    # Red for y=5
                            (0, 1, 0),    # Green for y=100
                            (0, 0, 1),    # Blue for y=200
                            (1, 1, 0),    # Yellow for y=400
                            (1, 0, 1),    # Magenta for y=600
                            (0, 1, 1)     # Cyan for y=800
                        ]
                        color = colors[i % len(colors)]
                        
                        banner_rect = fitz.Rect(x, y, x + width, y + height)
                        page.draw_rect(banner_rect, color=color, fill=(*color, 0.3), width=2)
                        
                        # Add text
                        page.insert_text(
                            (x + 2, y + height - 2),
                            label,
                            fontsize=10,
                            color=(0, 0, 0)
                        )
                        
                        print(f"   ✅ Added indicator at Y={y}, X={x}: {label}")
                        
                    except Exception as e:
                        print(f"   ❌ Error adding indicator at Y={y}: {e}")
                        
        except Exception as e:
            print(f"❌ Error in coordinate test: {e}")
    
    # Replace the method temporarily
    processor.add_dwelling_visual_indicators = test_dwelling_indicators
    
    # Generate PDF with coordinate test
    output_file = 'COORDINATE_SYSTEM_TEST.pdf'
    success = processor.fill_pdf_with_force_visible('homworks.pdf', test_document, output_file)
    
    # Restore original method
    processor.add_dwelling_visual_indicators = original_method
    
    if success:
        print(f"\n✅ COORDINATE TEST PDF created: {output_file}")
        
        print(f"\n🔍 COORDINATE SYSTEM TEST RESULTS:")
        print(f"   📍 RED (Y=5): Should be at the TOP of the page")
        print(f"   📍 GREEN (Y=100): Should be below red")
        print(f"   📍 BLUE (Y=200): Should be in upper middle")
        print(f"   📍 YELLOW (Y=400): Should be in middle")
        print(f"   📍 MAGENTA (Y=600): Should be in lower area")
        print(f"   📍 CYAN (Y=800): Should be at BOTTOM (if visible)")
        
        print(f"\n📖 WHAT TO CHECK:")
        print(f"   1. Open '{output_file}' in your PDF viewer")
        print(f"   2. Go to page 3")
        print(f"   3. Look for colored rectangles with Y coordinate labels")
        print(f"   4. Tell me which Y value appears HIGHEST on the page")
        print(f"   5. Tell me if the order is: Y=5 at top, then Y=100, Y=200, etc.")
        print(f"   6. Or if it's REVERSED: Y=800 at top, then Y=600, Y=400, etc.")
        
        return True
    else:
        print(f"❌ Failed to create coordinate test PDF")
        return False

if __name__ == "__main__":
    success = test_coordinate_system()
    if success:
        print("\n🎉 COORDINATE SYSTEM TEST COMPLETE!")
        print("🔍 Please check the PDF and tell me which Y value appears HIGHEST!")
    else:
        print("\n❌ Coordinate system test failed!")