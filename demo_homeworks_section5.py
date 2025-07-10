#!/usr/bin/env python3
"""
Demo using actual homeworks.pdf with Section 5 (Zero Income Affidavit) data
"""

import os
import sys
import fitz  # PyMuPDF
from datetime import datetime

def create_homeworks_demo():
    """Create a demo using the actual homeworks.pdf with Section 5 data filled in"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        print(f"❌ Error: {homeworks_path} not found")
        return None
    
    print("🔬 Creating Demo with Actual homeworks.pdf")
    print("=" * 50)
    print(f"✅ Found source PDF: {homeworks_path}")
    
    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"homeworks_section5_demo_{timestamp}.pdf"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    
    try:
        # Open the PDF
        doc = fitz.open(homeworks_path)
        print(f"📄 PDF opened successfully - {len(doc)} pages")
        
        # Sample Section 5 data that would be filled by User 2
        section5_data = {
            # Zero Income Affidavit fields
            'account_holder_name': 'John Smith',
            'zero_income_names': 'Mary Smith\nDavid Johnson\nSarah Wilson',
            'affidavit_printed_name': 'Jane Smith',
            'affidavit_date': '01/10/2025',
            'affidavit_telephone': '(860) 555-0123',
            
            # Also include some other sections for context
            'first_name': 'John',
            'last_name': 'Smith', 
            'property_address': '123 Main Street',
            'city': 'Hartford',
            'state': 'CT',
            'zip_code': '06103',
            'telephone': '(860) 555-0123',
            'email': 'john.smith@email.com',
            'qualification_option': 'Option C',
            'household_size': '3',
            'annual_income': '$45,000',
            'applicant_signature': 'Jane Smith',
            'signature_date': '01/10/2025'
        }
        
        print(f"\n📝 Filling PDF with Section 5 and sample data...")
        
        # Track what fields we fill
        filled_fields = []
        total_widgets = 0
        
        # Go through each page and fill form fields
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())  # Convert generator to list
            total_widgets += len(widgets)
            
            print(f"📄 Page {page_num + 1}: Found {len(widgets)} form widgets")
            
            for widget in widgets:
                field_name = widget.field_name
                field_type = widget.field_type
                
                if field_name:
                    # Try to match field name with our data
                    field_value = None
                    field_name_lower = field_name.lower()
                    
                    # Check for exact matches first
                    for data_key, data_value in section5_data.items():
                        if (data_key.lower() in field_name_lower or 
                            field_name_lower in data_key.lower() or
                            any(word in field_name_lower for word in data_key.split('_'))):
                            field_value = str(data_value)
                            break
                    
                    # Special handling for common field patterns
                    if not field_value:
                        if any(word in field_name_lower for word in ['name', 'holder', 'account']):
                            if 'print' in field_name_lower or 'affidavit' in field_name_lower:
                                field_value = section5_data['affidavit_printed_name']
                            elif 'holder' in field_name_lower or 'account' in field_name_lower:
                                field_value = section5_data['account_holder_name']
                            elif 'first' in field_name_lower:
                                field_value = section5_data['first_name']
                            elif 'last' in field_name_lower:
                                field_value = section5_data['last_name']
                        
                        elif any(word in field_name_lower for word in ['income', 'zero', 'household']):
                            if 'name' in field_name_lower or 'member' in field_name_lower:
                                field_value = section5_data['zero_income_names']
                            elif 'size' in field_name_lower:
                                field_value = section5_data['household_size']
                            elif 'annual' in field_name_lower:
                                field_value = section5_data['annual_income']
                        
                        elif any(word in field_name_lower for word in ['phone', 'telephone']):
                            if 'affidavit' in field_name_lower:
                                field_value = section5_data['affidavit_telephone']
                            else:
                                field_value = section5_data['telephone']
                        
                        elif any(word in field_name_lower for word in ['date']):
                            if 'affidavit' in field_name_lower:
                                field_value = section5_data['affidavit_date']
                            else:
                                field_value = section5_data['signature_date']
                        
                        elif any(word in field_name_lower for word in ['signature', 'sign']):
                            field_value = section5_data['applicant_signature']
                        
                        elif any(word in field_name_lower for word in ['address']):
                            field_value = section5_data['property_address']
                        
                        elif any(word in field_name_lower for word in ['city']):
                            field_value = section5_data['city']
                        
                        elif any(word in field_name_lower for word in ['state']):
                            field_value = section5_data['state']
                        
                        elif any(word in field_name_lower for word in ['zip']):
                            field_value = section5_data['zip_code']
                        
                        elif any(word in field_name_lower for word in ['email']):
                            field_value = section5_data['email']
                    
                    # Fill the field if we found a value
                    if field_value:
                        try:
                            if field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                                widget.field_value = field_value
                                widget.update()
                                filled_fields.append(f"✅ {field_name}: {field_value}")
                            elif field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                                if field_value.lower() in ['true', 'yes', 'confirmed', '1']:
                                    widget.field_value = True
                                    widget.update()
                                    filled_fields.append(f"✅ {field_name}: ☑ Checked")
                        except Exception as e:
                            print(f"   ⚠️ Could not fill {field_name}: {e}")
                    else:
                        print(f"   🔍 Found field: {field_name} (no matching data)")
        
        print(f"\n📊 Summary:")
        print(f"   📄 Total pages: {len(doc)}")
        print(f"   🔧 Total form widgets: {total_widgets}")
        print(f"   ✅ Fields filled: {len(filled_fields)}")
        
        if filled_fields:
            print(f"\n📝 Filled Fields:")
            for field in filled_fields[:15]:  # Show first 15
                print(f"   {field}")
            if len(filled_fields) > 15:
                print(f"   ... and {len(filled_fields) - 15} more fields")
        
        # Save the filled PDF
        doc.save(output_path)
        doc.close()
        
        file_size = os.path.getsize(output_path)
        print(f"\n🎯 Demo PDF created successfully!")
        print(f"📁 File: {output_filename}")
        print(f"📍 Path: {output_path}")
        print(f"📊 Size: {file_size:,} bytes")
        
        # Show specific Section 5 confirmation
        section5_filled = [f for f in filled_fields if any(word in f.lower() for word in ['income', 'affidavit', 'zero', 'holder'])]
        if section5_filled:
            print(f"\n🧾 Section 5 (Zero Income Affidavit) Fields Filled:")
            for field in section5_filled:
                print(f"   {field}")
        
        print(f"\n📄 Open the PDF to see Section 5 data in the actual homeworks form!")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error creating demo: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_pdf_structure():
    """Analyze the homeworks.pdf to understand its structure"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        print(f"❌ Error: {homeworks_path} not found")
        return
    
    print("🔍 Analyzing homeworks.pdf Structure")
    print("=" * 40)
    
    try:
        doc = fitz.open(homeworks_path)
        print(f"📄 PDF: {len(doc)} pages")
        
        all_fields = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())  # Convert generator to list
            
            print(f"\n📄 Page {page_num + 1}: {len(widgets)} form fields")
            
            for i, widget in enumerate(widgets):
                field_name = widget.field_name or f"unnamed_field_{i}"
                field_type_map = {
                    0: "Unknown",
                    1: "Button", 
                    2: "Text",
                    3: "Choice",
                    4: "Signature"
                }
                field_type_name = field_type_map.get(widget.field_type, "Unknown")
                
                all_fields.append({
                    'page': page_num + 1,
                    'name': field_name,
                    'type': field_type_name,
                    'rect': widget.rect
                })
                
                if len(widgets) <= 10:  # Only show details for pages with few fields
                    print(f"   {i+1:2d}. {field_name} ({field_type_name})")
        
        doc.close()
        
        print(f"\n📊 Total Form Fields: {len(all_fields)}")
        
        # Look for potential Section 5 fields
        section5_keywords = ['income', 'affidavit', 'zero', 'holder', 'household', 'affirm']
        potential_section5 = []
        
        for field in all_fields:
            field_name_lower = field['name'].lower()
            if any(keyword in field_name_lower for keyword in section5_keywords):
                potential_section5.append(field)
        
        if potential_section5:
            print(f"\n🧾 Potential Section 5 Fields Found: {len(potential_section5)}")
            for field in potential_section5:
                print(f"   Page {field['page']}: {field['name']} ({field['type']})")
        else:
            print(f"\n🔍 No obvious Section 5 fields found by name")
            print(f"   (This is normal - Section 5 may use generic field names)")
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")

def main():
    """Main demo function"""
    print("🏠 PDF Collaborator - homeworks.pdf Section 5 Demo")
    print("=" * 60)
    
    # First analyze the PDF structure
    analyze_pdf_structure()
    
    print("\n" + "=" * 60)
    
    # Create the demo
    demo_path = create_homeworks_demo()
    
    if demo_path:
        print(f"\n🎉 Success! Section 5 demo created with actual homeworks.pdf")
        print(f"📁 Open this file: {demo_path}")
        print(f"\n🔍 What to look for in the PDF:")
        print(f"   ✅ Account holder name filled")
        print(f"   ✅ Zero income household members listed")
        print(f"   ✅ Affidavit signature information")
        print(f"   ✅ Date and telephone fields")
        print(f"   ✅ Other form sections also filled for context")
    else:
        print(f"\n❌ Demo creation failed")

if __name__ == "__main__":
    main()