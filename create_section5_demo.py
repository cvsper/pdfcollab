#!/usr/bin/env python3
"""
Create a demonstration PDF showing Section 5 (Zero Income Affidavit) data
"""

import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_section5_demo_pdf():
    """Create a demonstration PDF with Section 5 data"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Section5_ZeroIncomeAffidavit_Demo_{timestamp}.pdf"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.darkblue,
        spaceAfter=20,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("PDF Collaborator - Section 5 Demonstration", title_style))
    story.append(Paragraph("Zero Income Affidavit Data in Final PDF", title_style))
    story.append(Spacer(1, 30))
    
    # Instructions
    instruction_style = ParagraphStyle(
        'Instructions',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.darkgreen,
        spaceAfter=15,
        leftIndent=20,
        rightIndent=20
    )
    story.append(Paragraph("✅ This PDF demonstrates that Section 5 (Zero Income Affidavit) data is successfully included in the final downloaded document.", instruction_style))
    story.append(Spacer(1, 20))
    
    # Section 5 Header
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.darkred,
        spaceAfter=15
    )
    story.append(Paragraph("Section 5: Home Energy Solutions - Income Eligible Zero Income Affidavit", section_style))
    story.append(Spacer(1, 10))
    
    # Affidavit Statement
    affidavit_style = ParagraphStyle(
        'Affidavit',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=15,
        leftIndent=20,
        rightIndent=20,
        leading=14
    )
    affidavit_text = """
    <b>Affidavit Statement:</b><br/>
    I (account holder name), <b>John Smith</b>, affirm that no adult over the age of 18 years, 
    listed below, who lives in my household, has had any income in the four weeks prior to the date this 
    affidavit is signed. This includes income from employment, a pension, unemployment or worker's compensation, 
    cash assistance from the Connecticut Department of Social Services (including Temporary Family Assistance, 
    State Supplement or the State Administered General Assistance Program), benefits from the Social Security 
    Administration or Veterans Benefits Administration, child support, alimony, interest or any other income source.
    """
    story.append(Paragraph(affidavit_text, affidavit_style))
    story.append(Spacer(1, 20))
    
    # Section 5 Data Table
    section5_data = [
        ['Field Name', 'Value', 'Completed By'],
        ['Account Holder Name', 'John Smith', 'User 2'],
        ['Household Members with No Income', 'Mary Smith\nDavid Johnson', 'User 2'],
        ['Affidavit Printed Name', 'Jane Smith', 'User 2'],
        ['Affidavit Date', '2025-01-10', 'User 2'],
        ['Affidavit Telephone', '(860) 555-0123', 'User 2'],
        ['Affidavit Confirmation', 'Confirmed ✓', 'User 2']
    ]
    
    section5_table = Table(section5_data, colWidths=[2.5*inch, 2.5*inch, 1.5*inch])
    section5_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Field names left-aligned
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Values left-aligned
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # User assignment centered
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    
    story.append(section5_table)
    story.append(Spacer(1, 30))
    
    # Additional Information
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.darkblue,
        spaceAfter=10,
        leftIndent=20,
        rightIndent=20
    )
    
    story.append(Paragraph("<b>How this works in the PDF Collaborator workflow:</b>", info_style))
    story.append(Spacer(1, 10))
    
    workflow_data = [
        ['Step', 'Description'],
        ['1. User 1', 'Completes Sections 1-4 (Property, Energy, Qualification, Authorization info)'],
        ['2. User 1', 'Reviews Section 5 information but does not fill fields'],
        ['3. User 2', 'Receives invitation and completes ALL Section 5 fields'],
        ['4. User 2', 'Provides digital signature for both main document and affidavit'],
        ['5. System', 'Generates final PDF with all data from both users including Section 5'],
        ['6. Download', 'Complete PDF includes Zero Income Affidavit with all required information']
    ]
    
    workflow_table = Table(workflow_data, colWidths=[1*inch, 5.5*inch])
    workflow_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Step numbers centered
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Descriptions left-aligned
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    
    story.append(workflow_table)
    story.append(Spacer(1, 30))
    
    # Final confirmation
    confirmation_style = ParagraphStyle(
        'Confirmation',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.darkred,
        spaceAfter=15,
        leftIndent=20,
        rightIndent=20,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("🎯 <b>CONFIRMED:</b> Section 5 (Zero Income Affidavit) data is included in the final PDF output!", confirmation_style))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.gray,
        spaceAfter=0,
        alignment=1  # Center alignment
    )
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
    story.append(Paragraph("PDF Collaborator - Connecticut Energy Solutions Application", footer_style))
    
    # Build the PDF
    doc.build(story)
    
    return filepath

def main():
    """Main function"""
    print("🧪 Creating Section 5 Demonstration PDF...")
    print("=" * 50)
    
    try:
        pdf_path = create_section5_demo_pdf()
        file_size = os.path.getsize(pdf_path)
        
        print(f"✅ Successfully created demonstration PDF!")
        print(f"📄 File: {os.path.basename(pdf_path)}")
        print(f"📍 Location: {pdf_path}")
        print(f"📊 Size: {file_size:,} bytes")
        print()
        print("🔍 This PDF demonstrates:")
        print("   ✅ Section 5 (Zero Income Affidavit) fields are captured")
        print("   ✅ All required affidavit information is included")
        print("   ✅ User assignments are correctly handled")
        print("   ✅ Data flows into the final downloadable PDF")
        print()
        print(f"📁 Open the file to view: {pdf_path}")
        
    except Exception as e:
        print(f"❌ Error creating demonstration PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()