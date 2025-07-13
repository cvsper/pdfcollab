#!/usr/bin/env python3
"""
Analyze the complete PDF structure to identify all fields
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

def analyze_complete_pdf():
    """Analyze all fields in the PDF to ensure complete mapping"""
    
    print("🔍 COMPLETE PDF FIELD ANALYSIS")
    print("=" * 60)
    
    try:
        import fitz
        pdf_path = 'homworks.pdf'
        
        if not os.path.exists(pdf_path):
            print(f"❌ {pdf_path} not found")
            return
        
        doc = fitz.open(pdf_path)
        print(f"📄 PDF has {len(doc)} pages")
        
        all_fields = {}
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            if widgets:
                print(f"\n📋 Page {page_num + 1}: Found {len(widgets)} form widgets")
                page_fields = []
                
                for i, widget in enumerate(widgets):
                    field_name = widget.field_name
                    field_type = widget.field_type
                    rect = widget.rect
                    
                    # Determine field type name
                    type_names = {
                        0: 'text',     # PDF_WIDGET_TYPE_TEXT
                        1: 'button',   # PDF_WIDGET_TYPE_BUTTON  
                        2: 'checkbox', # PDF_WIDGET_TYPE_CHECKBOX
                        3: 'radio',    # PDF_WIDGET_TYPE_RADIOBUTTON
                        4: 'listbox',  # PDF_WIDGET_TYPE_LISTBOX
                        5: 'combobox', # PDF_WIDGET_TYPE_COMBOBOX
                        6: 'signature',# PDF_WIDGET_TYPE_SIGNATURE
                        7: 'text'      # Additional text type
                    }
                    
                    type_name = type_names.get(field_type, f'unknown({field_type})')
                    
                    field_info = {
                        'name': field_name,
                        'type': type_name,
                        'position': {'x': rect.x0, 'y': rect.y0, 'width': rect.width, 'height': rect.height},
                        'page': page_num + 1
                    }
                    
                    page_fields.append(field_info)
                    all_fields[field_name] = field_info
                    
                    print(f"   {i+1:2d}. {field_name:<35} ({type_name:<9}) at ({rect.x0:5.1f}, {rect.y0:5.1f})")
                
                # Group by sections based on Y position
                page_fields.sort(key=lambda f: f['position']['y'])
                
        doc.close()
        
        print(f"\n📊 SUMMARY: Found {len(all_fields)} unique fields across 5 pages")
        
        # Categorize fields by section based on the form structure you provided
        print(f"\n🏗️ FIELD CATEGORIZATION:")
        
        section1_fields = []  # Property Information
        section2_fields = []  # Applicant and Energy Information  
        section3_fields = []  # Qualification Information
        section4_fields = []  # Authorization
        section5_fields = []  # Zero Income Affidavit
        
        for field_name, field_info in all_fields.items():
            name_lower = field_name.lower()
            
            # Section 1: Property Information
            if any(keyword in name_lower for keyword in ['property_address', 'apartment', 'apt', 'city', 'state', 'zip']):
                section1_fields.append(field_info)
            
            # Section 2: Applicant and Energy Information
            elif any(keyword in name_lower for keyword in ['first_name', 'last_name', 'phone', 'email', 'telephone', 'fuel', 'heat', 'electric', 'gas', 'util', 'acct', 'owner', 'renter', 'dwelling']):
                section2_fields.append(field_info)
            
            # Section 3: Qualification Information
            elif any(keyword in name_lower for keyword in ['discount', 'income', 'household', 'ebt', 'assistance', 'section', 'multifam', 'matching', 'bill', 'forgiv']):
                section3_fields.append(field_info)
            
            # Section 4: Authorization (signatures and dates)
            elif any(keyword in name_lower for keyword in ['signature', 'sign', 'date', 'landlord', 'address3']):
                section4_fields.append(field_info)
            
            # Section 5: Zero Income Affidavit
            elif any(keyword in name_lower for keyword in ['affidavit', 'account_holder', 'printed']):
                section5_fields.append(field_info)
            
            else:
                # Uncategorized fields
                print(f"   ❓ Unategorized: {field_name} ({field_info['type']})")
        
        print(f"\n📋 Section 1 - Property Information: {len(section1_fields)} fields")
        for field in section1_fields:
            print(f"   - {field['name']} ({field['type']})")
        
        print(f"\n👤 Section 2 - Applicant/Energy Info: {len(section2_fields)} fields")  
        for field in section2_fields:
            print(f"   - {field['name']} ({field['type']})")
        
        print(f"\n💰 Section 3 - Qualification Info: {len(section3_fields)} fields")
        for field in section3_fields:
            print(f"   - {field['name']} ({field['type']})")
        
        print(f"\n✍️ Section 4 - Authorization: {len(section4_fields)} fields")
        for field in section4_fields:
            print(f"   - {field['name']} ({field['type']})")
        
        print(f"\n📝 Section 5 - Zero Income Affidavit: {len(section5_fields)} fields")
        for field in section5_fields:
            print(f"   - {field['name']} ({field['type']})")
        
        return all_fields
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_complete_pdf()