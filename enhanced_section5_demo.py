#!/usr/bin/env python3
"""
Enhanced demo focusing specifically on Section 5 fields in homeworks.pdf
"""

import os
import fitz  # PyMuPDF
from datetime import datetime

def create_enhanced_section5_demo():
    """Create enhanced demo with clear Section 5 field mapping"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        print(f"❌ Error: {homeworks_path} not found")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"SECTION5_ENHANCED_DEMO_{timestamp}.pdf"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    
    print("🧾 Enhanced Section 5 Demo - homeworks.pdf")
    print("=" * 50)
    print(f"✅ Source: {homeworks_path}")
    print(f"📄 Output: {output_filename}")
    
    try:
        # Open PDF
        doc = fitz.open(homeworks_path)
        
        # Comprehensive Section 5 data
        section5_data = {
            # Main form sections (for context)
            'property_address1': '123 Main Street',
            'apt_num1': 'Apt 2B',
            'city1': 'Hartford',
            'state1': 'CT',
            'zip1': '06103',
            'first_name2': 'John',
            'last_name2': 'Smith',
            'phone2': '(860) 555-0123',
            'email2': 'john.smith@email.com',
            'phone_num1': '(860) 555-0123',
            
            # Section 5: Zero Income Affidavit specific fields
            'people_in_household4': '3',  # Household size
            'people_in_household_overage4': '2',  # Adults 18+
            'annual_income4': 'Mary Smith\nDavid Johnson\nSarah Wilson',  # Zero income names
            'low_income4': 'John Smith - Account Holder',  # Account holder name
            
            # Signature fields (User 2)
            'signature3': 'Jane Smith',
            'date3': '01/10/2025',
            'landlord_name3': 'Property Owner LLC',
            'address3': '456 Property St, Hartford, CT',
            'phone3': '(860) 555-0456',
            'email3': 'owner@property.com',
            'signature4': 'Jane Smith',
            'date4': '01/10/2025',
            
            # Additional fields that might be related
            'elect_acct_other_name2': 'John Smith',
            'gas_acct_other_name2': 'John Smith',
            'elec_acct_num2': 'EV123456789',
            'gas_acct_num2': 'CNG987654321'
        }
        
        print(f"\n📝 Filling PDF with Section 5 focused data...")
        
        filled_fields = []
        section5_specific = []
        
        # Process each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            if widgets:
                print(f"📄 Page {page_num + 1}: Processing {len(widgets)} fields")
                
                for widget in widgets:
                    field_name = widget.field_name
                    if not field_name:
                        continue
                    
                    # Try exact field name match first
                    if field_name in section5_data:
                        field_value = section5_data[field_name]
                        
                        try:
                            if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                                widget.field_value = field_value
                                widget.update()
                                filled_fields.append(f"✅ {field_name}: {field_value}")
                                
                                # Check if this is a Section 5 field
                                if any(keyword in field_name.lower() for keyword in ['income', 'household', 'people']):
                                    section5_specific.append(f"🧾 SECTION 5: {field_name} = {field_value}")
                                    
                            elif widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                                widget.field_value = True
                                widget.update()
                                filled_fields.append(f"✅ {field_name}: ☑ Checked")
                                
                        except Exception as e:
                            print(f"   ⚠️ Could not fill {field_name}: {e}")
                    
                    # Also try pattern matching for unlisted fields
                    else:
                        field_lower = field_name.lower()
                        matched_value = None
                        
                        if 'household' in field_lower and ('size' in field_lower or 'people' in field_lower):
                            matched_value = '3'
                        elif 'adult' in field_lower or ('18' in field_lower and 'over' in field_lower):
                            matched_value = '2'
                        elif any(word in field_lower for word in ['income', 'zero', 'names']):
                            matched_value = 'Mary Smith, David Johnson, Sarah Wilson'
                        elif 'holder' in field_lower or ('account' in field_lower and 'name' in field_lower):
                            matched_value = 'John Smith'
                        
                        if matched_value:
                            try:
                                if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                                    widget.field_value = matched_value
                                    widget.update()
                                    filled_fields.append(f"✅ {field_name}: {matched_value}")
                                    section5_specific.append(f"🧾 SECTION 5 (inferred): {field_name} = {matched_value}")
                            except:
                                pass
        
        # Save the filled PDF
        doc.save(output_path)
        doc.close()
        
        file_size = os.path.getsize(output_path)
        
        print(f"\n📊 Results Summary:")
        print(f"   📄 Total fields filled: {len(filled_fields)}")
        print(f"   🧾 Section 5 fields: {len(section5_specific)}")
        print(f"   📁 File size: {file_size:,} bytes")
        
        if section5_specific:
            print(f"\n🧾 SECTION 5 (Zero Income Affidavit) Fields:")
            for field in section5_specific:
                print(f"   {field}")
        
        print(f"\n📋 All Filled Fields:")
        for field in filled_fields:
            print(f"   {field}")
        
        print(f"\n🎯 Enhanced Demo Complete!")
        print(f"📁 File: {output_path}")
        print(f"\n📄 This PDF demonstrates Section 5 data in the actual Connecticut")
        print(f"   Home Energy Solutions - Income Eligible application form!")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Enhanced Section 5 Demonstration")
    print("Using actual Connecticut homeworks.pdf form")
    print()
    
    result = create_enhanced_section5_demo()
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"📄 Section 5 data has been filled into the actual homeworks.pdf")
        print(f"📁 Open: {result}")
        print(f"\n🔍 Look for:")
        print(f"   ✅ Household information on page 4")
        print(f"   ✅ Zero income affidavit data")
        print(f"   ✅ Signature fields filled")
        print(f"   ✅ Complete Connecticut energy assistance form")
    else:
        print(f"\n❌ Demo failed")

if __name__ == "__main__":
    main()