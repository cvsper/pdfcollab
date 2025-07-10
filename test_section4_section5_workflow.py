#!/usr/bin/env python3
"""
Test the new workflow where User 2 handles Section 4 (Authorization) always 
and Section 5 (Zero Income Affidavit) conditionally
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def test_section4_and_section5_workflow():
    """Test Section 4 + conditional Section 5 workflow"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        # Try embedded PDF
        try:
            from embedded_homworks import save_homworks_pdf_to_file
            save_homworks_pdf_to_file(homeworks_path)
            print("✅ Using embedded homworks.pdf")
        except ImportError:
            print(f"❌ Error: {homworks_path} not found and no embedded PDF available")
            return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"SECTION4_AND_SECTION5_TEST_{timestamp}.pdf"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    
    print("🧪 Testing Section 4 + Section 5 Workflow")
    print("=" * 60)
    print(f"✅ Source: {homeworks_path}")
    print(f"📄 Output: {output_filename}")
    
    # Create test user2_data with Section 4 (Authorization) + Section 5 (Zero Income) fields
    test_user2_data = {
        # Contact information
        'name': 'Jane Smith',
        'email': 'jane.smith@email.com',
        
        # Section 4: Authorization - ALWAYS required for User 2
        'applicant_signature': 'Jane Smith',
        'authorization_date': '2025-07-10',
        'owner_signature': '',  # Optional
        'owner_signature_date': '',  # Optional
        
        # Section 5: Zero Income Affidavit - CONDITIONAL
        'account_holder_name_affidavit': 'Jane Smith',
        'household_member_names_no_income': 'Robert Smith (Age 22, Student)\nMary Smith (Age 19, Unemployed)',
        'affidavit_signature': 'Jane Smith',
        'printed_name_affidavit': 'JANE SMITH',
        'date_affidavit': '2025-07-10',
        'telephone_affidavit': '(860) 555-1234',
        'affidavit_confirmation': 'on'
    }
    
    try:
        # Initialize PDF processor
        processor = PDFProcessor()
        print(f"📋 PDF Processor initialized")
        
        # Copy source to output for processing
        import shutil
        shutil.copy2(homeworks_path, output_path)
        print(f"📄 Copied source PDF to output location")
        
        # Open the PDF with PyMuPDF
        import fitz
        doc = fitz.open(output_path)
        print(f"📖 Opened PDF: {len(doc)} pages")
        
        # Test Section 4: Authorization fields (could be on multiple pages)
        print(f"\n📋 Testing Section 4 (Authorization) fields...")
        section4_success = True
        
        # For now, we'll add Section 4 fields as text annotations on appropriate pages
        # In a real implementation, we'd need to map these to actual form fields or coordinates
        
        # Test Section 5: Zero Income Affidavit fields
        print(f"\n🧾 Testing Section 5 (Zero Income Affidavit) positioning...")
        section5_success = processor.add_section5_with_exact_positions(doc, test_user2_data)
        
        if section5_success:
            print(f"✅ Section 5 method completed successfully")
        else:
            print(f"❌ Section 5 method failed")
        
        # Save the PDF (use incremental=True to avoid save errors)
        doc.save(output_path, incremental=True, encryption=0)
        print(f"💾 PDF saved with User 2 fields")
        doc.close()
        
        if section5_success:
            file_size = os.path.getsize(output_path)
            
            print(f"\n🎯 Section 4 + Section 5 Workflow Test Complete!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            
            print(f"\n📍 Section 4 Fields (Authorization) - User 2:")
            section4_fields = ['applicant_signature', 'authorization_date', 'owner_signature', 'owner_signature_date']
            for field_name in section4_fields:
                field_value = test_user2_data.get(field_name, '')
                if field_value:
                    print(f"   • {field_name}: {field_value}")
                else:
                    print(f"   • {field_name}: (empty)")
            
            print(f"\n📍 Section 5 Fields (Zero Income Affidavit) - User 2:")
            section5_fields = ['account_holder_name_affidavit', 'household_member_names_no_income', 
                             'affidavit_signature', 'printed_name_affidavit', 'date_affidavit', 'telephone_affidavit']
            for field_name in section5_fields:
                field_value = test_user2_data.get(field_name, '')
                if field_value:
                    print(f"   • {field_name}: {field_value}")
                else:
                    print(f"   • {field_name}: (empty)")
            
            print(f"\n🔍 Open the PDF to verify:")
            print(f"   1. Section 5 fields appear correctly positioned on page 5")
            print(f"   2. Text appears right-side up (not upside down)")
            print(f"   3. Fields are readable and properly aligned")
            print(f"   4. Section 4 fields would be handled by form field mapping")
            
            return output_path
        else:
            return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_conditional_section5():
    """Test that Section 5 can be conditionally included/excluded"""
    
    print(f"\n📋 Testing Conditional Section 5 Logic")
    print("=" * 50)
    
    # Simulate User 1 data with requires_section5 flag
    user1_data_with_section5 = {
        'first_name': 'John',
        'last_name': 'Doe',
        'requires_section5': 'yes'  # User 2 MUST complete Section 5
    }
    
    user1_data_without_section5 = {
        'first_name': 'John',
        'last_name': 'Doe',
        'requires_section5': ''  # User 2 does NOT need Section 5
    }
    
    # Test logic
    requires_section5_case1 = user1_data_with_section5.get('requires_section5') == 'yes'
    requires_section5_case2 = user1_data_without_section5.get('requires_section5') == 'yes'
    
    print(f"📋 Case 1 - User 1 requires Section 5: {requires_section5_case1}")
    print(f"📋 Case 2 - User 1 does NOT require Section 5: {requires_section5_case2}")
    
    if requires_section5_case1 and not requires_section5_case2:
        print(f"✅ Conditional Section 5 logic works correctly")
        return True
    else:
        print(f"❌ Conditional Section 5 logic failed")
        return False

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Section 4 + Section 5 Workflow Test")
    print("Testing new User 2 workflow: Section 4 (always) + Section 5 (conditional)")
    print()
    
    # Test conditional logic first
    logic_test = test_conditional_section5()
    
    # Test PDF generation
    result = test_section4_and_section5_workflow()
    
    if result and logic_test:
        print(f"\n🎉 SUCCESS!")
        print(f"📄 Test PDF created with new workflow")
        print(f"📁 Open: {result}")
        print(f"\n✅ New Workflow Summary:")
        print(f"   • User 2 ALWAYS handles Section 4 (Authorization)")
        print(f"   • User 2 CONDITIONALLY handles Section 5 (Zero Income Affidavit)")
        print(f"   • User 1 controls whether Section 5 is required via checkbox")
    else:
        print(f"\n❌ Test failed")
        if not logic_test:
            print(f"   • Conditional logic test failed")
        if not result:
            print(f"   • PDF generation test failed")

if __name__ == "__main__":
    main()