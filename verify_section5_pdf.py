#!/usr/bin/env python3
"""
Verification script to show Section 5 content in the generated test PDF
"""

import os
import fitz  # PyMuPDF

def analyze_pdf_content(pdf_path):
    """Analyze PDF content to show text and fields"""
    
    print(f"🔍 Analyzing PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    try:
        doc = fitz.open(pdf_path)
        print(f"📄 PDF has {len(doc)} pages")
        
        # Check each page for text content
        for page_num in range(len(doc)):
            page = doc[page_num]
            print(f"\n📄 PAGE {page_num + 1}:")
            
            # Get all text on the page
            text_dict = page.get_text("dict")
            all_text = page.get_text()
            
            # Look for Section 5 related text
            section5_keywords = [
                "Jane Doe (Account Holder)",
                "Robert Doe", "Mary Doe",
                "Jane M. Doe", "JANE MARIE DOE", 
                "2025-07-10", "555-987-6543",
                "Account Holder Name", "Household Member",
                "Affidavit Signature", "Printed Name",
                "Date (Affidavit)", "Telephone (Affidavit)"
            ]
            
            found_section5_content = []
            for keyword in section5_keywords:
                if keyword in all_text:
                    found_section5_content.append(keyword)
            
            if found_section5_content:
                print(f"✅ Found Section 5 content on page {page_num + 1}:")
                for content in found_section5_content:
                    print(f"   - '{content}'")
            else:
                print(f"⭕ No Section 5 content found on page {page_num + 1}")
            
            # Check for form widgets
            widgets = list(page.widgets())
            if widgets:
                print(f"📋 Found {len(widgets)} form widgets on page {page_num + 1}")
                
                # Look for Section 5 widget names
                section5_widgets = []
                for widget in widgets:
                    field_name = widget.field_name or ""
                    field_value = widget.field_value or ""
                    
                    if any(keyword in field_name.lower() for keyword in ['affidavit', 'account_holder', 'household']):
                        section5_widgets.append({
                            'name': field_name,
                            'value': field_value,
                            'type': widget.field_type_string
                        })
                
                if section5_widgets:
                    print(f"✅ Found {len(section5_widgets)} Section 5 widgets:")
                    for widget in section5_widgets:
                        print(f"   - {widget['name']}: '{widget['value']}' ({widget['type']})")
        
        doc.close()
        
        # Final summary
        print(f"\n" + "="*60)
        print("📊 SECTION 5 VERIFICATION SUMMARY")
        print("="*60)
        
        # Re-open to check overall content
        doc = fitz.open(pdf_path)
        all_text = ""
        total_widgets = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            all_text += page.get_text()
            total_widgets += len(list(page.widgets()))
        
        doc.close()
        
        # Check if our test data is present
        test_values = [
            "Jane Doe (Account Holder)",
            "Robert Doe (Son, Age 19, Student)",
            "Mary Doe (Daughter, Age 20, Unemployed)", 
            "Jane M. Doe",
            "JANE MARIE DOE",
            "2025-07-10",
            "555-987-6543"
        ]
        
        found_values = [value for value in test_values if value in all_text]
        
        print(f"📄 Total form widgets in PDF: {total_widgets}")
        print(f"✅ Section 5 test values found: {len(found_values)}/{len(test_values)}")
        
        if found_values:
            print(f"\n✅ SUCCESS: Section 5 data is present in the PDF!")
            print(f"📋 Found values:")
            for value in found_values:
                print(f"   - '{value}'")
        else:
            print(f"\n❌ FAILURE: Section 5 data not found in PDF")
        
        print(f"\n🎯 Recommendation:")
        if len(found_values) >= len(test_values) // 2:
            print(f"   ✅ Section 5 is working! The data appears in the PDF.")
            print(f"   📄 You can download and view: {pdf_path}")
        else:
            print(f"   ⚠️  Section 5 may need adjustment, but some data was found.")
            
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main verification function"""
    
    print("="*60)
    print("🔍 SECTION 5 PDF VERIFICATION")
    print("="*60)
    
    # Find the test PDF
    test_pdf = "uploads/completed_test_section5_001_Test_Section5_Demo.pdf"
    
    if os.path.exists(test_pdf):
        analyze_pdf_content(test_pdf)
    else:
        print(f"❌ Test PDF not found: {test_pdf}")
        print("Run 'python3 test_section5.py' first to generate the test PDF")

if __name__ == "__main__":
    main()