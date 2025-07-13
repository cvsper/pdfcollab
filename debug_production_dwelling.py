#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def debug_production_dwelling():
    """Debug why dwelling fields aren't working in production"""
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Load the template PDF
    template_path = "homworks.pdf"
    if not os.path.exists(template_path):
        print(f"❌ Template PDF not found: {template_path}")
        return
    
    # Extract fields to see what's actually in the PDF
    print("🔍 Extracting fields from PDF...")
    result = processor.extract_fields_with_pymupdf(template_path)
    
    if result.get('success'):
        fields = result.get('fields', [])
        print(f"\n📊 Total fields found: {len(fields)}")
        
        # Look for dwelling-related fields
        print("\n🏠 Dwelling-related fields:")
        dwelling_fields = []
        for field in fields:
            field_name = field.get('name', '').lower()
            pdf_field_name = field.get('pdf_field_name', '').lower()
            
            if 'dwelling' in field_name or 'dwelling' in pdf_field_name:
                dwelling_fields.append(field)
                print(f"   ✅ Display Name: {field.get('name')}")
                print(f"      PDF Name: {field.get('pdf_field_name')}")
                print(f"      Type: {field.get('type')}")
                print(f"      Position: ({field['position']['x']:.1f}, {field['position']['y']:.1f})")
                print()
        
        if not dwelling_fields:
            print("   ❌ No dwelling fields found!")
            
        # Check for checkbox fields on page 3
        print("\n📄 All checkbox fields on page 3:")
        page3_checkboxes = []
        for field in fields:
            if field.get('page') == 2 and field.get('type') == 'checkbox':  # Page 3 is index 2
                page3_checkboxes.append(field)
                print(f"   📦 {field.get('name')} [{field.get('pdf_field_name')}]")
                print(f"      Position: ({field['position']['x']:.1f}, {field['position']['y']:.1f})")
        
        if not page3_checkboxes:
            print("   ❌ No checkboxes found on page 3!")
            
        # Check field_type_map
        print("\n🗺️ Field type map dwelling entries:")
        for key, value in processor.field_type_map.items():
            if 'dwelling' in key.lower():
                print(f"   {key} → {value}")
                
    else:
        print(f"❌ Error extracting fields: {result.get('error')}")

if __name__ == "__main__":
    debug_production_dwelling()