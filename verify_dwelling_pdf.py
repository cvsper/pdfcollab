#!/usr/bin/env python3
"""
Verify the dwelling checkbox in the generated PDF
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import fitz  # PyMuPDF

def verify_dwelling_pdf():
    """Verify dwelling checkbox is actually working in the final PDF"""
    
    print("🔍 VERIFYING DWELLING CHECKBOX IN PDF")
    print("=" * 50)
    
    pdf_file = 'SIMPLE_DWELLING_TEST.pdf'
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        return False
    
    try:
        doc = fitz.open(pdf_file)
        print(f"📄 Opened PDF: {pdf_file}")
        print(f"📋 Pages: {len(doc)}")
        
        # Check page 3 (index 2) where dwelling checkboxes are
        page = doc[2]
        print(f"\n🔍 Checking page 3 for dwelling checkboxes...")
        
        # Get widgets using list comprehension to avoid generator issue
        widgets = list(page.widgets())
        print(f"📋 Found {len(widgets)} widgets on page 3")
        
        dwelling_widgets = []
        property_address_widget = None
        
        for widget in widgets:
            widget_name = widget.field_name
            widget_value = widget.field_value
            widget_type = widget.field_type_string
            
            print(f"🔧 Widget: {widget_name} = {widget_value} (type: {widget_type})")
            
            # Look for dwelling checkboxes
            if 'dwelling' in widget_name.lower():
                dwelling_widgets.append({
                    'name': widget_name,
                    'value': widget_value,
                    'type': widget_type,
                    'checked': widget_value in [True, 1, 'Yes']
                })
            
            # Look for property address
            elif 'property_address' in widget_name.lower():
                property_address_widget = {
                    'name': widget_name,
                    'value': widget_value,
                    'type': widget_type
                }
        
        print(f"\n🏠 DWELLING WIDGETS FOUND: {len(dwelling_widgets)}")
        for dwelling in dwelling_widgets:
            status = "✅ CHECKED" if dwelling['checked'] else "❌ UNCHECKED"
            print(f"   {dwelling['name']}: {dwelling['value']} ({status})")
        
        if property_address_widget:
            print(f"\n📍 PROPERTY ADDRESS: {property_address_widget['name']} = '{property_address_widget['value']}'")
        
        # Specific check for apartment checkbox
        apartment_checked = False
        for dwelling in dwelling_widgets:
            if 'apt' in dwelling['name'].lower() and dwelling['checked']:
                apartment_checked = True
                print(f"\n🎉 SUCCESS: Apartment checkbox is CHECKED!")
                break
        
        if not apartment_checked:
            print(f"\n⚠️  WARNING: Apartment checkbox is NOT checked")
            
            # Show all checkboxes for debugging
            print(f"\n📝 ALL CHECKBOXES ON PAGE 3:")
            for widget in widgets:
                if widget.field_type == 2:  # Checkbox type
                    checked_status = "✅" if widget.field_value in [True, 1, 'Yes'] else "❌"
                    print(f"   {checked_status} {widget.field_name}: {widget.field_value}")
        
        doc.close()
        return apartment_checked
        
    except Exception as e:
        print(f"❌ Error verifying PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_dwelling_pdf()
    if success:
        print("\n✅ Dwelling checkbox verification PASSED!")
    else:
        print("\n❌ Dwelling checkbox verification FAILED!")