#!/usr/bin/env python3
"""
Final Section 5 demonstration showing it correctly positioned on page 5
"""

import fitz

def create_final_demo():
    """Create a clear demonstration of Section 5 on page 5"""
    
    print("🎯 Creating final Section 5 demonstration...")
    
    # Open the test PDF that has Section 5 on page 5
    pdf_path = "uploads/completed_test_section5_001_Test_Section5_Demo.pdf"
    
    try:
        doc = fitz.open(pdf_path)
        
        if len(doc) < 5:
            print("❌ PDF doesn't have 5 pages")
            return
        
        # Get page 5 (index 4)
        page5 = doc[4]
        
        # Add a clear header to page 5 to highlight Section 5
        header_rect = fitz.Rect(50, 50, 550, 90)
        page5.draw_rect(header_rect, color=(0, 0, 0.8), fill=True)
        
        # Add white text on blue background
        page5.insert_text(
            (60, 75),
            "✅ SECTION 5: ZERO INCOME AFFIDAVIT - COMPLETED BY USER 2",
            fontsize=14,
            color=(1, 1, 1)  # White text
        )
        
        # Add arrows pointing to Section 5 content
        arrow_y = 150
        page5.insert_text(
            (60, arrow_y),
            "👇 Section 5 fields below were filled by User 2:",
            fontsize=12,
            color=(0.8, 0, 0)  # Red text
        )
        
        # Add a border around the Section 5 content area
        content_rect = fitz.Rect(90, 180, 530, 320)
        page5.draw_rect(content_rect, color=(0, 0.6, 0), width=3)
        
        # Add completion note at bottom
        bottom_y = page5.rect.height - 100
        completion_rect = fitz.Rect(50, bottom_y, 550, bottom_y + 40)
        page5.draw_rect(completion_rect, color=(0, 0.6, 0), fill=True)
        
        page5.insert_text(
            (60, bottom_y + 25),
            "✅ SUCCESS: Section 5 is now correctly positioned on Page 5!",
            fontsize=12,
            color=(1, 1, 1)  # White text
        )
        
        # Save the enhanced PDF
        output_path = "Section5_Final_Demo_Page5.pdf"
        doc.save(output_path)
        doc.close()
        
        print(f"✅ Created final demo: {output_path}")
        print(f"📄 Section 5 is clearly marked and positioned on page 5")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error creating demo: {e}")
        return None

def verify_page5_content():
    """Verify Section 5 content is on page 5"""
    
    print("\n🔍 Verifying Section 5 is on page 5...")
    
    pdf_path = "uploads/completed_test_section5_001_Test_Section5_Demo.pdf"
    
    try:
        doc = fitz.open(pdf_path)
        
        section5_data = [
            "Jane Doe (Account Holder)",
            "Robert Doe (Son, Age 19, Student)",
            "Mary Doe (Daughter, Age 20, Unemployed)",
            "Jane M. Doe",
            "JANE MARIE DOE",
            "2025-07-10",
            "555-987-6543"
        ]
        
        # Check each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            
            found_items = [item for item in section5_data if item in page_text]
            
            if found_items:
                print(f"📄 PAGE {page_num + 1}: Found {len(found_items)} Section 5 items")
                if page_num == 4:  # Page 5 (0-indexed)
                    print(f"   ✅ CORRECT: Section 5 is on page 5!")
                else:
                    print(f"   ⚠️  Section 5 content found on page {page_num + 1} (should be page 5)")
        
        doc.close()
        
        # Final verification
        doc = fitz.open(pdf_path)
        page5_text = doc[4].get_text()
        page5_section5_count = sum(1 for item in section5_data if item in page5_text)
        doc.close()
        
        print(f"\n📊 Final Verification:")
        print(f"   - Section 5 items on page 5: {page5_section5_count}/{len(section5_data)}")
        
        if page5_section5_count == len(section5_data):
            print(f"   ✅ SUCCESS: All Section 5 data is correctly on page 5!")
        else:
            print(f"   ⚠️  Only {page5_section5_count} items found on page 5")
        
        return page5_section5_count == len(section5_data)
        
    except Exception as e:
        print(f"❌ Error verifying: {e}")
        return False

def main():
    """Main demonstration"""
    
    print("="*60)
    print("🎯 FINAL SECTION 5 DEMONSTRATION")
    print("="*60)
    
    # Verify content is on page 5
    success = verify_page5_content()
    
    if success:
        # Create enhanced demo
        demo_file = create_final_demo()
        
        print(f"\n" + "="*60)
        print("🎉 SECTION 5 SUCCESS!")
        print("="*60)
        print(f"✅ Section 5 is now correctly positioned on page 5")
        print(f"✅ All 7 Section 5 data items are present")
        print(f"✅ Demo PDF created: {demo_file}")
        
        print(f"\n📄 Files to download and view:")
        print(f"1. uploads/completed_test_section5_001_Test_Section5_Demo.pdf")
        print(f"2. {demo_file} (enhanced with highlighting)")
        
        print(f"\n🎯 To see Section 5:")
        print(f"   1. Open either PDF file")
        print(f"   2. Navigate to PAGE 5")
        print(f"   3. Look for the Zero Income Affidavit section")
        print(f"   4. You'll see all 6 fields with filled data")
        
    else:
        print(f"\n❌ Section 5 verification failed")

if __name__ == "__main__":
    main()