#!/usr/bin/env python3
"""
Create a more visible Section 5 demonstration
This script creates a PDF with Section 5 fields positioned clearly on the page
"""

import os
import sys
import fitz
from datetime import datetime

def create_clear_section5_demo():
    """Create a PDF with clearly visible Section 5 content"""
    
    print("🎯 Creating clearly visible Section 5 demonstration...")
    
    # Create a new PDF document
    doc = fitz.open()
    page = doc.new_page()
    
    # Page dimensions
    page_width = page.rect.width
    page_height = page.rect.height
    
    print(f"📄 Page size: {page_width} x {page_height}")
    
    # Title
    title_text = "HOME ENERGY SOLUTIONS - SECTION 5: ZERO INCOME AFFIDAVIT"
    page.insert_text(
        (50, 50),
        title_text,
        fontsize=16,
        color=(0, 0, 0.8)  # Dark blue
    )
    
    # Subtitle
    subtitle_text = "Complete this section only if you qualify with Option C and have household members over 18 with no income"
    page.insert_text(
        (50, 80),
        subtitle_text,
        fontsize=10,
        color=(0.5, 0.5, 0.5)  # Gray
    )
    
    # Draw a border around Section 5
    section_rect = fitz.Rect(40, 40, page_width - 40, 450)
    page.draw_rect(section_rect, color=(0, 0, 0.8), width=2)
    
    # Section 5 fields with clear positioning
    y_position = 120
    line_height = 35
    
    section5_data = [
        ("Account Holder Name:", "Jane Doe (Account Holder)"),
        ("Household Member Names (No Income):", 
         "Robert Doe (Son, Age 19, Student)\nMary Doe (Daughter, Age 20, Unemployed)"),
        ("Affidavit Signature:", "Jane M. Doe"),
        ("Printed Name:", "JANE MARIE DOE"),
        ("Date:", "July 10, 2025"),
        ("Telephone:", "(555) 987-6543")
    ]
    
    for label, value in section5_data:
        # Field label
        page.insert_text(
            (60, y_position),
            label,
            fontsize=12,
            color=(0, 0, 0)  # Black
        )
        
        # Field value in a box
        value_rect = fitz.Rect(60, y_position + 5, page_width - 60, y_position + 25)
        page.draw_rect(value_rect, color=(0.9, 0.9, 0.9), fill=True)
        page.draw_rect(value_rect, color=(0, 0, 0), width=1)
        
        # Handle multi-line values
        if '\n' in value:
            lines = value.split('\n')
            for i, line in enumerate(lines):
                page.insert_text(
                    (65, y_position + 18 + (i * 12)),
                    line,
                    fontsize=10,
                    color=(0, 0, 0.8)  # Dark blue
                )
            y_position += len(lines) * 12
        else:
            page.insert_text(
                (65, y_position + 18),
                value,
                fontsize=10,
                color=(0, 0, 0.8)  # Dark blue
            )
        
        y_position += line_height
    
    # Add certification text
    cert_y = y_position + 20
    cert_text = [
        "I certify that the information provided above is true and accurate.",
        "I understand that providing false information may result in penalties.",
        "",
        "This section demonstrates how Section 5 (Zero Income Affidavit) appears",
        "when User 2 completes the form and the PDF is downloaded."
    ]
    
    for line in cert_text:
        page.insert_text(
            (60, cert_y),
            line,
            fontsize=9,
            color=(0.3, 0.3, 0.3)  # Dark gray
        )
        cert_y += 15
    
    # Add a footer
    footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    page.insert_text(
        (60, page_height - 50),
        footer_text,
        fontsize=8,
        color=(0.5, 0.5, 0.5)
    )
    
    # Save the PDF
    output_path = "Section5_Demo_Visible.pdf"
    doc.save(output_path)
    doc.close()
    
    file_size = os.path.getsize(output_path)
    print(f"✅ Created visible Section 5 demo: {output_path}")
    print(f"📄 File size: {file_size:,} bytes")
    
    return output_path

def create_section5_workflow_demo():
    """Create a comprehensive workflow demonstration"""
    
    print("\n🎯 Creating Section 5 workflow demonstration...")
    
    # Create a new PDF document
    doc = fitz.open()
    
    # Page 1: User 1 View
    page1 = doc.new_page()
    page1.insert_text((50, 50), "USER 1 INTERFACE - SECTION 5 ASSIGNMENT", fontsize=16, color=(0, 0, 0.8))
    
    y_pos = 100
    user1_text = [
        "When User 1 processes the PDF, they see Section 5 fields assigned to User 2:",
        "",
        "✓ Account Holder Name (Affidavit) → Assigned to User 2",
        "✓ Household Member Names (No Income) → Assigned to User 2", 
        "✓ Affidavit Signature → Assigned to User 2",
        "✓ Printed Name (Affidavit) → Assigned to User 2",
        "✓ Date (Affidavit) → Assigned to User 2",
        "✓ Telephone (Affidavit) → Assigned to User 2",
        "",
        "User 1 completes their sections and submits to User 2.",
        "Section 5 appears as orange-highlighted fields for User 2."
    ]
    
    for line in user1_text:
        color = (0, 0.6, 0) if line.startswith("✓") else (0, 0, 0)
        page1.insert_text((60, y_pos), line, fontsize=11, color=color)
        y_pos += 20
    
    # Page 2: User 2 View  
    page2 = doc.new_page()
    page2.insert_text((50, 50), "USER 2 INTERFACE - SECTION 5 COMPLETION", fontsize=16, color=(0.8, 0.4, 0))
    
    y_pos = 100
    user2_text = [
        "User 2 receives the form and sees Section 5 fields to complete:",
        "",
        "Account Holder Name (Affidavit):",
        "[Text Input Field] → User 2 enters: Jane Doe (Account Holder)",
        "",
        "Household Member Names (No Income):",
        "[Textarea Field] → User 2 enters:",
        "  Robert Doe (Son, Age 19, Student)",
        "  Mary Doe (Daughter, Age 20, Unemployed)",
        "",
        "Affidavit Signature:",
        "[Signature Field] → User 2 enters: Jane M. Doe",
        "",
        "And so on for all Section 5 fields..."
    ]
    
    for line in user2_text:
        color = (0.8, 0.4, 0) if line.startswith("[") else (0, 0, 0)
        page2.insert_text((60, y_pos), line, fontsize=11, color=color)
        y_pos += 20
    
    # Page 3: Final Result
    page3 = doc.new_page()
    page3.insert_text((50, 50), "FINAL PDF - SECTION 5 COMPLETED", fontsize=16, color=(0, 0.6, 0))
    
    # Draw the actual Section 5 as it appears in the final PDF
    y_pos = 100
    page3.insert_text((60, y_pos), "Section 5: Zero Income Affidavit", fontsize=14, color=(0, 0, 0.8))
    y_pos += 40
    
    final_fields = [
        ("Account Holder Name:", "Jane Doe (Account Holder)"),
        ("Household Members:", "Robert Doe (Son, Age 19, Student)"),
        ("", "Mary Doe (Daughter, Age 20, Unemployed)"),
        ("Signature:", "Jane M. Doe"),
        ("Printed Name:", "JANE MARIE DOE"),
        ("Date:", "July 10, 2025"),
        ("Telephone:", "(555) 987-6543")
    ]
    
    for label, value in final_fields:
        if label:
            page3.insert_text((60, y_pos), f"{label}", fontsize=10, color=(0, 0, 0))
            page3.insert_text((200, y_pos), f"{value}", fontsize=10, color=(0, 0, 0.8))
        else:
            page3.insert_text((200, y_pos), f"{value}", fontsize=10, color=(0, 0, 0.8))
        y_pos += 18
    
    # Save the workflow PDF
    workflow_path = "Section5_Workflow_Demo.pdf"
    doc.save(workflow_path)
    doc.close()
    
    file_size = os.path.getsize(workflow_path)
    print(f"✅ Created workflow demo: {workflow_path}")
    print(f"📄 File size: {file_size:,} bytes")
    
    return workflow_path

def main():
    """Create demonstration files"""
    
    print("="*60)
    print("🎯 CREATING SECTION 5 DEMONSTRATIONS")
    print("="*60)
    
    # Create visible demo
    visible_demo = create_clear_section5_demo()
    
    # Create workflow demo
    workflow_demo = create_section5_workflow_demo()
    
    print(f"\n" + "="*60)
    print("📄 DEMONSTRATION FILES CREATED")
    print("="*60)
    print(f"1. Visible Section 5: {visible_demo}")
    print(f"2. Workflow Demo: {workflow_demo}")
    
    print(f"\n🎯 How to view Section 5:")
    print(f"1. Open {visible_demo} - Shows exactly how Section 5 looks")
    print(f"2. Open {workflow_demo} - Shows the complete workflow")
    print(f"3. For the real application, Section 5 appears in the slide interface")
    print(f"   when you navigate to 'Section 5: Zero Income Affidavit'")

if __name__ == "__main__":
    main()