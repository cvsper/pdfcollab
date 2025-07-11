#!/usr/bin/env python3
"""
Test Section 5 with PDF Processor method to verify orientation and positioning
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def test_section5_pdf_processor():
    """Test Section 5 using the PDF processor method"""
    
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
    output_filename = f"SECTION5_PDF_PROCESSOR_TEST_{timestamp}.pdf"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    
    print("🧪 Testing Section 5 with PDF Processor Method")
    print("=" * 60)
    print(f"✅ Source: {homeworks_path}")
    print(f"📄 Output: {output_filename}")
    
    # Create test user2_data with Section 5 fields
    test_user2_data = {
        'account_holder_name_affidavit': 'John Smith',
        'household_member_names_no_income': 'Robert Smith (Age 22, Student)\nMary Smith (Age 19, Unemployed)',
        'affidavit_signature': 'John Smith',
        'printed_name_affidavit': 'JOHN SMITH',
        'date_affidavit': '2025-07-10',
        'telephone_affidavit': '(860) 555-1234',
        'affidavit_confirmation': 'on'
    }
    
    # Create mock document structure
    mock_document = {
        'id': 'test_document',
        'name': 'Test Document',
        'user2_data': test_user2_data,
        'pdf_fields': []  # Empty for this test
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
        
        # Test the Section 5 method directly
        print(f"\n🧾 Testing Section 5 positioning method...")
        section5_success = processor.add_section5_with_exact_positions(doc, test_user2_data)
        
        if section5_success:
            print(f"✅ Section 5 method completed successfully")
            
            # Save the PDF
            doc.save(output_path)
            print(f"💾 PDF saved with Section 5 fields")
        else:
            print(f"❌ Section 5 method failed")
        
        doc.close()
        
        if section5_success:
            file_size = os.path.getsize(output_path)
            
            print(f"\n🎯 PDF Processor Section 5 Test Complete!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            
            print(f"\n📍 Section 5 Fields Tested:")
            for field_name, field_value in test_user2_data.items():
                if field_name != 'affidavit_confirmation':
                    print(f"   • {field_name}: {field_value}")
            
            print(f"\n📋 Expected Positions:")
            print(f"   • Account Holder Name: x=155, y=145")
            print(f"   • Household Members: x=45, y=265")
            print(f"   • Signature: x=40, y=490")
            print(f"   • Printed Name: x=315, y=490")
            print(f"   • Date: x=50, y=535")
            print(f"   • Telephone: x=315, y=535")
            
            print(f"\n🔍 Open the PDF to verify:")
            print(f"   1. Text appears right-side up (not upside down)")
            print(f"   2. Fields are positioned correctly")
            print(f"   3. Text is readable and properly aligned")
            
            return output_path
        else:
            return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_both_methods_comparison():
    """Test both the PDF processor method and the app.py method for comparison"""
    
    print("\n" + "="*80)
    print("🔬 COMPARISON TEST: PDF Processor vs App.py Method")
    print("="*80)
    
    # Test PDF processor method
    result1 = test_section5_pdf_processor()
    
    # Test app.py method (if available)
    try:
        from app import fill_section5_with_exact_positions
        
        homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        if not os.path.exists(homeworks_path):
            try:
                from embedded_homworks import save_homworks_pdf_to_file
                save_homworks_pdf_to_file(homeworks_path)
            except ImportError:
                print("❌ Cannot test app.py method - no PDF available")
                return result1
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"SECTION5_APP_METHOD_TEST_{timestamp}.pdf"
        output_path = os.path.join(os.path.dirname(__file__), output_filename)
        
        import shutil
        shutil.copy2(homeworks_path, output_path)
        
        test_user2_data = {
            'account_holder_name_affidavit': 'Jane Doe (App Method)',
            'household_member_names_no_income': 'Robert Doe (Age 22)\nMary Doe (Age 19)',
            'affidavit_signature': 'Jane Doe',
            'printed_name_affidavit': 'JANE DOE',
            'date_affidavit': '2025-07-10',
            'telephone_affidavit': '(860) 555-9876'
        }
        
        import fitz
        doc = fitz.open(output_path)
        app_success = fill_section5_with_exact_positions(doc, test_user2_data)
        
        if app_success:
            doc.save(output_path)
            print(f"\n✅ App.py method test created: {output_filename}")
        
        doc.close()
        
    except ImportError as e:
        print(f"\n⚠️  Could not test app.py method: {e}")
    
    return result1

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Section 5 PDF Processor Test")
    print("Testing orientation and positioning fixes")
    print()
    
    result = test_both_methods_comparison()
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"📄 Test PDF created with PDF processor method")
        print(f"📁 Open: {result}")
        print(f"\n🔍 Check the PDF to verify:")
        print(f"   ✅ Text orientation is correct (not upside down)")
        print(f"   ✅ Field positions match expected coordinates")
        print(f"   ✅ Text is readable and properly formatted")
    else:
        print(f"\n❌ Test failed")

if __name__ == "__main__":
    main()